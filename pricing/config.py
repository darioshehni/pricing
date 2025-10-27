from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Config:
    # Data paths
    data_dir: Path = Path("data")
    sku_daily_csv: Path = data_dir / "sku_daily.csv"
    model_elasticity_csv: Path = data_dir / "model_elasticity.csv"
    sku_costs_csv: Path = data_dir / "sku_costs.csv"

    # Optimization behavior
    price_bounds_pct: tuple[float, float] = (0.85, 1.35)  # relative to current price
    n_grid: int = 121                                      # grid resolution
    price_ending: float = 0.99                             # psychological ending
    enforce_price_ending: bool = True

    # Guards
    min_margin_abs: float = 0.0            # don't price below cost
    require_elasticity_gt_one: bool = True # use grid if |β| <= 1
