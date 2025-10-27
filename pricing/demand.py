import numpy as np
import pandas as pd

def alpha_from_point(q0: float, p0: float, beta: float) -> float:
    """
    Q = α * P^β  =>  α = Q / P^β
    Basic guards to avoid division errors.
    """
    if p0 <= 0 or q0 <= 0:
        return 1e-6
    return float(q0) / float(p0) ** float(beta)

def estimate_alpha_per_sku(sku_snapshot: pd.DataFrame, beta_by_model: dict) -> pd.DataFrame:
    """
    Input columns: sku_id, model, price, sales
    Output columns: sku_id, model, p0, q0, beta, alpha
    """
    rows: list[dict] = []
    for _, r in sku_snapshot.iterrows():
        sku_id = r["sku_id"]
        model = r["model"]
        p0 = float(r["price"])
        q0 = float(r["sales"])
        beta = float(beta_by_model[model])
        alpha = alpha_from_point(q0, p0, beta)
        rows.append({
            "sku_id": sku_id,
            "model": model,
            "p0": p0,
            "q0": q0,
            "beta": beta,
            "alpha": alpha,
        })
    return pd.DataFrame(rows)

def profit_at_price(p: float, alpha: float, beta: float, cost: float) -> float:
    """
    π(P) = (P - C) * α * P^β
    """
    if p <= 0:
        return -1e18
    q = alpha * (p ** beta)
    return (p - cost) * q
