# Pricing Experiments

Four focused experiments to validate the core mechanics and guardrails. Run one change at a time and observe the recommendation for a representative SKU.

## 1) Cost sensitivity
- What it tests: The Lerner rule sets price as a markup over cost; with β fixed, P* moves proportionally with C.
- Why it matters: Confirms the markup mechanics are correct and that a change in cost produces the expected directional and proportional change.
- Pass signal: +10% cost ⇒ ≈ +10% price (as long as bounds don’t clip it). Method stays "lerner".

Results (S25-128-BLK)
- Baseline: price 1079.99, method lerner, bounds [764.15, 1213.65]
- +10% cost (C=594): price 1187.99, method lerner (≈ +10%)

## 2) Elasticity sensitivity
- What it tests: How β affects markup.
  - More elastic (e.g., −3) ⇒ customers are more price‑sensitive ⇒ smaller markup ⇒ price moves closer to cost.
  - Less elastic (e.g., −1.5) ⇒ less sensitivity ⇒ larger markup ⇒ price tends to rise, sometimes beyond the upper bound.
- Why it matters: Validates that the tool responds to demand sensitivity in the correct direction and that guardrails (bounds, method switch to grid) take over when the closed form is unrealistic.
- Pass signal: β = −3 lowers the price; β = −1.5 pushes toward/onto the upper bound with method "grid" if Lerner is out of range.

Results (S25-128-BLK)
- β = −3.0: price 809.99, method lerner (moves closer to cost)
- β = −1.5: price 1212.99, method grid (upper bound), as Lerner is out of range

## 3) Sales scaling (α invariance)
- What it tests: Doubling today’s sales q0 doubles α, but doesn’t change the Lerner candidate (which ignores α).
- Why it matters: Proves level (α) is separated from sensitivity (β). The recommended price under Lerner is driven by β and C, not absolute volume.
- Pass signal: Price unchanged; predicted profits roughly double (since demand scale rose).

Results (S25-128-BLK)
- q0 doubled to 260: price 1079.99 (unchanged), method lerner; profits roughly doubled

## 4) Bounds enforcement (grid fallback)
- What it tests: If you lower p0, the allowed range shrinks; the theoretical Lerner price may fall outside the bounds.
- Why it matters: Ensures the tool switches to grid and respects operational constraints when theory proposes something infeasible.
- Pass signal: Method shows "grid" and the recommended price sits near the nearest bound (snapped to .99), not at the theoretical Lerner value.

---

## Results
- Cost sensitivity:
  - I increased cost for S25-128-BLK by 10% (540 → 594). I saw the recommended price move from 1079.99 to 1187.99 (about +10%) with method "lerner". So that means the markup logic is working and prices scale with cost when bounds don’t clip. It does not mean profits are exact to the penny; they still depend on α from a single snapshot and on using marginal (not fully‑loaded) cost.

- Elasticity sensitivity:
  - I changed the model’s β to −3.0. I saw the price drop to 809.99 (closer to cost) and stay on "lerner". So that means higher elasticity (more price‑sensitive) produces a smaller markup as expected.
  - Then I changed β to −1.5. I saw the price jump to 1212.99 with method "grid" (upper bound), because the Lerner price was outside the allowed range. So that means the guardrails take over when theory proposes something infeasible. It does not mean profit magnitudes are comparable across β runs—α is recalibrated each time, so this test is about direction, not absolute levels.

- Sales scaling (α invariance):
  - I doubled today’s sales for that SKU (q0: 130 → 260). I saw the price remain 1079.99 (still "lerner") while profits roughly doubled. So that means α only scales demand and doesn’t change the Lerner price, which is set by β and cost. It does not mean the broader demand curve is validated—this checks local scaling under the isoelastic assumption.

- Bounds enforcement (grid fallback):
  - I lowered today’s price to 750, which shrank the allowed bounds to [637.5, 1012.5]. I saw the tool pick 1011.99 with method "grid". So that means when the Lerner suggestion is out of range, the tool respects constraints and lands on the best feasible (snapped) price. It does not mean the chosen bounds are economically optimal; if p0 is stale or promotional, relative bounds can anchor the outcome.

## What these collectively validate
- Economic correctness: cost ↑ ⇒ price ↑; |β| ↑ ⇒ price ↓; α doesn’t affect the Lerner price.
- Guardrail behavior: when theory collides with constraints, the tool switches methods and lands on a feasible price.
- Numerical stability: prices remain ≥ cost, stay within bounds, and rounding doesn’t break feasibility.
 - Cost `C` should approximate marginal cost (COGS + variable costs); average/fully-loaded cost biases Lerner prices upward.
