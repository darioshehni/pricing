import numpy as np
import pandas as pd
from .config import Config
from .demand import profit_at_price
from .utils import round_to_price_ending, clamp

def lerner_price(cost: float, beta: float) -> float | None:
    """
    Lerner rule: (P - C)/P = -1/β  =>  P* = |β|/(|β|-1) * C  (valid if |β| > 1)
    Returns None if not applicable.
    """
    b = abs(float(beta))
    if b <= 1.0:
        return None
    return (b / (b - 1.0)) * float(cost)

def grid_search_best_price(
    p0: float,
    alpha: float,
    beta: float,
    cost: float,
    cfg: Config
) -> float:
    lo = p0 * cfg.price_bounds_pct[0]
    hi = p0 * cfg.price_bounds_pct[1]
    raw = np.linspace(lo, hi, cfg.n_grid)

    # Snap first and de-duplicate
    if cfg.enforce_price_ending and cfg.price_ending is not None:
        snapped = [
            round_to_price_ending(p, cfg.price_ending, policy=getattr(cfg, "price_ending_policy", "down"))
            for p in raw
        ]
    else:
        snapped = [round(p, 2) for p in raw]

    candidates = sorted(set(snapped))

    # Filter feasibility AFTER snapping
    feas: list[float] = []
    for p in candidates:
        if p < cost + cfg.min_margin_abs:
            continue
        if p < lo or p > hi:
            continue
        feas.append(p)

    if not feas:
        # Safe fallback inside bounds and above cost+margin
        fallback = max(cost + cfg.min_margin_abs, lo)
        if cfg.enforce_price_ending and cfg.price_ending is not None:
            fallback = round_to_price_ending(
                fallback, cfg.price_ending, policy=getattr(cfg, "price_ending_policy", "down")
            )
        return float(min(max(fallback, lo), hi))

    # Evaluate profits on feasible snapped candidates
    best_p, best_pi = None, -1e18
    for p in feas:
        pi = profit_at_price(p, alpha, beta, cost)
        if pi > best_pi:
            best_p, best_pi = p, pi

    return float(best_p)

def recommend_prices(
    calib_df: pd.DataFrame,  # columns: sku_id, model, p0, q0, beta, alpha
    costs_df: pd.DataFrame,
    cfg: Config
) -> pd.DataFrame:
    """
    Produces recommended prices per SKU using:
      1) Lerner closed-form if |β|>1 and within bounds
      2) Else grid-search within [pct-bounds] of current price p0
    """
    df = calib_df.merge(costs_df, on="sku_id", how="left")
    out_rows: list[dict] = []

    for _, r in df.iterrows():
        sku_id = r["sku_id"]
        model = r["model"]
        p0 = float(r["p0"])
        q0 = float(r["q0"])
        beta = float(r["beta"])
        alpha = float(r["alpha"])
        cost = float(r["unit_cost"])

        lo = p0 * cfg.price_bounds_pct[0]
        hi = p0 * cfg.price_bounds_pct[1]

        p_lerner = lerner_price(cost, beta)
        use_lerner_rule = (
            p_lerner is not None
            and (not cfg.require_elasticity_gt_one or abs(beta) > 1.0)
        )

        if use_lerner_rule:
            # Pre-snap feasibility
            if (p_lerner >= cost + cfg.min_margin_abs) and (lo <= p_lerner <= hi):
                p_star_raw = p_lerner
                p_star = p_star_raw
                if cfg.enforce_price_ending and cfg.price_ending is not None:
                    p_star = round_to_price_ending(
                        p_star_raw, cfg.price_ending, policy=getattr(cfg, "price_ending_policy", "down")
                    )
                # Post-snap feasibility re-check
                if (p_star >= cost + cfg.min_margin_abs) and (lo <= p_star <= hi):
                    method = "lerner"
                else:
                    p_star = grid_search_best_price(p0, alpha, beta, cost, cfg)
                    method = "grid"
            else:
                p_star = grid_search_best_price(p0, alpha, beta, cost, cfg)
                method = "grid"
        else:
            p_star = grid_search_best_price(p0, alpha, beta, cost, cfg)
            method = "grid"

        pi0 = profit_at_price(p0, alpha, beta, cost)
        pistar = profit_at_price(p_star, alpha, beta, cost)

        out_rows.append({
            "sku_id": sku_id,
            "model": model,
            "beta": beta,
            "unit_cost": cost,
            "p0": p0,
            "q0": q0,
            "alpha": alpha,
            "price_recommended": round(p_star, 2),
            "profit_current": round(pi0, 2),
            "profit_recommended": round(pistar, 2),
            "delta_profit": round(pistar - pi0, 2),
            "method": method,
            "bounds": f"[{round(lo,2)}, {round(hi,2)}]",
        })

    return pd.DataFrame(out_rows)
