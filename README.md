# Samsung S25 Pricing MVP

Minimal tool to recommend SKU‑level prices for the Galaxy S25 series using simple, economics‑based rules.

## Quick Start

Option A — via script (creates venv, installs deps, runs):
```bash
./run.sh
```

Option B — manual run:
```bash
pip install -r requirements.txt    # or: pip install pandas numpy
python main.py
```

Output:
- Prints a table of SKU-level recommendations to the console.
- Writes `pricing_recommendations.csv` in the project root.

## From Input To Price
1) Load inputs: per‑SKU current price (p0) and sales (q0); per‑SKU marginal cost (C); per‑model elasticity (β) mapped to each SKU.
2) Calibrate demand scale (α) per SKU so today’s point lies on the curve (isoelastic).
3) Compute a closed‑form candidate (Lerner) when usable: if |β|>1, compute a price based on β and C.
4) Accept the candidate only if it’s within relative bounds around p0 and above cost; otherwise, scan a bounded grid around p0 and pick the most profitable price.
5) Snap to a .99 ending and re‑check bounds and margin (don’t price below cost).
6) Output a CSV with the recommended price per SKU, the method used (lerner/grid), and lift vs current price.

## Algorithms
- Demand (isoelastic): `Q(P) = α · P**β`.
- β (elasticity): from MMM at model level; mapped to each SKU by its `model`.
- α calibration (per SKU): `α = q0 / (p0**β)` so `(p0,q0)` lies on the curve.
- Profit: `π(P) = (P − C) · α · (P**β)` where `C` is marginal unit cost.
- Bounds: `[p0*lo, p0*hi]` (relative to current price; see `pricing/config.py`).
- Lerner candidate (only if `abs(β) > 1`): `P* = (|β|/(|β|−1)) · C`.
  - Use only if within bounds and `P* ≥ C + min_margin_abs`; after snapping to `.99`, re‑validate feasibility.
- Grid fallback: evaluate `π(P)` across a grid in `[p0*lo, p0*hi]`; for each candidate, snap to `.99`, enforce margin, and choose the highest‑profit feasible price (ties handled by the maximization).

## Results
1) Cost Sensitivity
- Change: increased cost for `S25-128-BLK` from 540 to 594 (+10%).
- Expectation: Lerner price scales with cost; with β=−2, `P*` moves ≈ +10% to about 1188 and snaps to 1187.99. Why: Lerner `P* = |β|/(|β|−1) · C` with fixed β.
- Result: price 1187.99, method `lerner`. Matches proportional markup.

2) Elasticity Sensitivity
- Change: set model `S25` elasticity to −3.0.
- Expectation: more elastic ⇒ smaller markup ⇒ price closer to cost (≈ 809.99). Why: multiplier drops from 2.0 to 1.5.
- Result: price 809.99, method `lerner`.
- Change: set model `S25` elasticity to −1.5.
- Expectation: less elastic ⇒ larger markup (≈ 1620) but outside bounds, so grid picks near the cap (≈ 1212.99). Why: Lerner candidate out of `[p0*lo, p0*hi]`.
- Result: price 1212.99, method `grid` (upper bound).

3) Sales Scaling (α Invariance)
- Change: doubled today’s sales for `S25-128-BLK` from 130 to 260.
- Expectation: α doubles; Lerner price unchanged at 1079.99; profits roughly double. Why: Lerner depends on β and cost, not α.
- Result: price 1079.99 (unchanged), method `lerner`; profits ≈ doubled.

4) Bounds Enforcement (Grid Fallback)
- Change: lowered current price `p0` to 750, shrinking bounds to [637.5, 1012.5].
- Expectation: Lerner ≈ 1080 is out of range; grid selects near the cap (≈ 1012.99). Why: feasibility guardrails dominate when theory is infeasible.
- Result: price 1011.99, method `grid` (near cap).

## Files
- `data/sku_daily.csv`: one snapshot row per SKU (`date, sku_id, model, price, sales`).
- `data/model_elasticity.csv`: model‑level elasticity mapping (`model, beta`).
- `data/sku_costs.csv`: marginal unit cost per SKU (`sku_id, unit_cost`).
- `pricing/config.py`: configuration (paths, bounds, grid density, .99 ending, min margin).
- `pricing/io.py`: CSV loading helpers.
- `pricing/demand.py`: demand calibration and profit computation.
- `pricing/optimizer.py`: price selection (Lerner when feasible, else grid search).
- `pricing/utils.py`: rounding (.99) and clamp utilities.
- `main.py`: orchestrates the full pipeline and writes the CSV.
- `run.sh`: convenience script to set up a venv and run.
