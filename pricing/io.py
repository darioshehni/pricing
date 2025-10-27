import pandas as pd
from .config import Config

def load_sku_daily(cfg: Config) -> pd.DataFrame:
    df = pd.read_csv(cfg.sku_daily_csv, parse_dates=["date"])
    # For MVP, we assume one snapshot row per SKU is already provided
    return df

def load_model_elasticity(cfg: Config) -> dict:
    df = pd.read_csv(cfg.model_elasticity_csv)
    return {row["model"]: float(row["beta"]) for _, row in df.iterrows()}

def load_sku_costs(cfg: Config) -> pd.DataFrame:
    return pd.read_csv(cfg.sku_costs_csv)
