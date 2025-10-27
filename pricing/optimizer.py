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
    grid = np.linspace(lo, hi, cfg.n_grid)

    profits = []
    prices = []
    for p in grid:
        if p < cost + cfg.min_margin_abs:
            continue
        p_eval = p
        if cfg.enforce_price_ending and cfg.price_ending is not None:
            p_eval = round_to_price_ending(p, cfg.price_ending)
        profits.append(profit_at_price(p_eval, alpha, beta, cost))
        prices.append(p_eval)

    if not profits:
        return clamp(cost + 0.01, lo, hi)

    idx = int(np.argmax(profits))
    return float(prices[idx])

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
        use_lerner = (
            p_lerner is not None
            and (not cfg.require_elasticity_gt_one or abs(beta) > 1.0)
            and lo <= p_lerner <= hi
            and p_lerner >= cost + cfg.min_margin_abs
        )

        if use_lerner:
            p_star = p_lerner
            if cfg.enforce_price_ending and cfg.price_ending is not None:
                p_star = round_to_price_ending(p_star, cfg.price_ending)
            method = "lerner"
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
