import pandas as pd
from pricing.config import Config
from pricing.io import load_sku_daily, load_model_elasticity, load_sku_costs
from pricing.demand import estimate_alpha_per_sku
from pricing.optimizer import recommend_prices

def main() -> None:
    cfg = Config()

    # 1) Load data
    df_daily = load_sku_daily(cfg)  # expects columns: date, sku_id, model, price, sales
    beta_by_model = load_model_elasticity(cfg)  # dict: model -> beta
    df_costs = load_sku_costs(cfg)  # columns: sku_id, unit_cost

    # 2) Build one snapshot per SKU (already one per in dummy data)
    sku_snapshot = df_daily[["sku_id", "model", "price", "sales"]].copy()

    # 3) Calibrate α per SKU
    calib = estimate_alpha_per_sku(sku_snapshot, beta_by_model)

    # 4) Recommend prices
    recs = recommend_prices(calib, df_costs, cfg)

    # 5) Present / save
    cols = [
        "sku_id","model","beta","unit_cost",
        "p0","q0","alpha","price_recommended",
        "profit_current","profit_recommended","delta_profit",
        "method","bounds"
    ]
    recs = recs[cols].sort_values("delta_profit", ascending=False)
    print(recs.to_string(index=False))

    recs.to_csv("pricing_recommendations.csv", index=False)
    print("\nSaved: pricing_recommendations.csv")

if __name__ == "__main__":
    main()
