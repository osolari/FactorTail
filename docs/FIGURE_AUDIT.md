# Figure audit — what each panel was supposed to show, what it shows now, and how to fix it

This document audits every figure in `results/` against the intended
purpose stated in its generator's docstring and the corresponding
manuscript section, and proposes a targeted improvement plan.

Severity codes:

- 🟢 **OK** — figure tells the right story; cosmetic polish only.
- 🟡 **Weak** — math is correct but the story is uninformative (e.g.
  degenerate design that hides the diagnostic).
- 🔴 **Broken** — numerical bug or misleading; needs a rewrite.

Counts: 4 🔴 broken (F3, F4, F6, F7), 4 🟡 weak (F2, F13, F14, F19),
11 🟢 ok.

---

## F1 — independent tail equivalence  🟢

**Intended.** Plot $P(S_N > x)$, the first-order asymptotic
$\sum_i \overline F_i(x)$, and the corrected second-order expansion on
log-log axes for a fixed $N$. Show the CdMC sitting between the
first-order line and the empirical reference, with the second-order
line tracking it.

**Now.** Three Pareto($\alpha=2$, varying scale) margins, $N=3$. CdMC
curve tracks second-order curve closely; first-order is below both.

**Issues.**
1. First-order line uses the same blue as the CdMC curve — visually
   confused.
2. The legend lists "95% CI" but the band is invisible (Bernstein CI
   is so tight at $n = 20\,000$ that it has zero pixel width).
3. The deep-tail ratio CdMC/first-order is not annotated; the
   convergence to 1 is the key claim.

**Plan.**
- Recolor first-order to a neutral grey dashed line; keep CdMC indigo
  and second-order in the accent colour.
- Drop the "95% CI" entry from the legend OR widen the fill by an
  $1/\sqrt{n}$ factor with `alpha=0.2`.
- Annotate the rightmost point with `ratio = mu_hat / first_order`.
- Add a faint α=2 slope reference line in light grey.

---

## F2 — maximum vs sum  🟡

**Intended.** Verify `thm:catastrophe-exact`:
$P(M_N > x) / P(S_N > x) \to 1$ as $x \to \infty$. Two-panel
figure: log-log of both probabilities, then the ratio on
semilog.

**Now.** Ratio rises from 0.17 (x=5) to 0.87 (x=80) — exactly the
expected monotone-toward-1 behaviour.

**Issues.**
1. The trend would be clearer if x extended further; at x=80 the
   ratio is still 0.87, not yet 0.99. The asymptotic claim looks
   under-supported.
2. Bands missing in the ratio panel (we have $p_\text{max}$ /
   $p_\text{sum}$ standard errors in the CSV).
3. The left panel y-axis labels "probability" instead of
   $P(\cdot > x)$.

**Plan.**
- Extend `x_grid` to `[5, 10, 20, 40, 80, 160, 320, 640]`. At the
  largest x the ratio should be above 0.97.
- Overlay $\pm 2$ SE error bars on the ratio panel using the delta
  method already in the script (`ci_low`, `ci_high` from CSV).
- Y-label left panel: `P(M_N > x)` / `P(S_N > x)` legend stays;
  axis becomes "probability $P(\cdot > x)$" with the math symbols
  inline.
- Add a "first-order sum-tail asymptotic" reference line
  ($\sum_i \overline F_i(x)$) on the left panel.

---

## F3 — efficiency rate vs threshold $x$  🔴

**Intended.** Plot the per-replicate exponential efficiency rate
$\lambda_n(x)$ of the independent CdMC against $x$, overlay the
finite-$N$ envelope and the asymptotic bound $1/(N^\alpha - 1)$.
Under BRE, the rate should be bounded and converge to its asymptote.

**Now.** The empirical rate spikes to 14 at $x=5$, drops to ~1 at
$x=20$, then **rises again to 7 at $x=160$**. The shape is wrong;
under BRE it should be monotone and bounded.

**Root cause.** The rate formula I implemented is
$\widehat{\mathrm{rate}}(x) = 1 / (\widehat\nu(x) \kappa(x)^2)$ with
$\kappa(x) = \log(1/\widehat\mu(x))$. Both pieces are ill-conditioned:

- $\widehat\nu$ (relative variance) goes to a constant under BRE
  (e.g., $N^\alpha - 1$).
- $\kappa$ blows up as $\widehat\mu \to 0$ (deep tail).
- $\widehat\mu \to 1$ at small $x$, so $\kappa \to 0$ and the rate
  blows up there too.

The asymptotic bound `1/(N^α - 1)` plotted in the figure is the
*relative-variance* bound, not the LDP rate. Apples-to-oranges.

**Plan.**
- Swap the y-axis quantity from `rate_hat` to **inverse relative
  variance** $1/\widehat\nu(x)$. Asymptote is the BRE constant
  $1/(N^\alpha - 1)$, which is the right comparison.
- Use a **log y-scale** so the BRE-bounded constant is visible across
  the threshold sweep.
- Add a `1 / first_order(x)` reference line showing the crude-MC rate
  for comparison (which decays to 0 with $x^\alpha$).
- Update SCHEMA column names: drop `kappa` and `lambda_n` (now
  redundant), keep `rel_variance`, `rate_hat`, `rate_bound_finite`,
  `rate_bound_asymptotic`.

---

## F4 — efficiency rate vs $\bar\alpha$  🔴

**Intended.** Sweep the average tail index $\bar\alpha$; common-α
designs trace one curve, heterogeneous designs scatter near the
$\alpha_{\min}$-dominated regime.

**Now.** Common-α designs trace a clean monotone-decreasing curve
(good). But the heterogeneous designs sit **above** the common-α
curve at the same $\bar\alpha$, which is the wrong direction —
heterogeneity should *hurt* the rate, putting points below the
common-α line.

**Root cause.** Same as F3: the rate formula is wrong. The
heterogeneous designs have larger $\widehat\mu$ (more probability
mass) and therefore smaller $\kappa$, which inflates the rate.

**Plan.**
- Apply the F3 fix (use $1/\widehat\nu$).
- After the fix, heterogeneous designs should fall *below* the
  common-α curve because their effective BRE bound is governed by
  $\alpha_{\min}$ (worse than $\bar\alpha$).
- Label each heterogeneous point with `(α_min, α_max)` so the
  reader can see the gap.

---

## F5 — efficiency rate vs $\alpha_{\min}$  🟢

**Intended.** Sweep $\alpha_{\min}$ at fixed $\alpha_{\max}$.

**Now.** Clean monotone decreasing curve from $\alpha_{\min}=1.2$
(rate ~50) to $\alpha_{\min}=3.0$ (rate ~2.5). Math is consistent
because $\bar\alpha$ varies less here so the $\kappa$ artefact is
smaller.

**Issues.**
- Same conceptual rate-formula problem; the curve happens to look
  reasonable but the numbers are inflated.

**Plan.**
- Apply the F3 fix; the *shape* will not change (monotone decreasing)
  but the y-scale will reflect the actual BRE bound.

---

## F6 — VRE pilot benchmark  🟡 (informative non-result)

**Intended.** Compare crude / oracle / sample-split-pilot VRE
estimators across pilot rules $n_0 \in \{\sqrt n, n/\log n, n^{2/3}\}$.
Determine which pilot rule wins on Family I (handoff Q1).

**Now.** All five box plots cluster in $[0.00265, 0.0029]$ — they
*all* essentially tie. The story is: "under iid Pareto with identical
margins, the marginal surrogate has $\rho \approx 0$, so any control
variate is useless."

**Issues.**
1. The figure looks meaningless to a casual reader — boxes appear
   identical.
2. It misses the actual interesting finding: the surrogate **choice**
   (loss vs `max_coord` vs `second_largest_shift`) matters more
   than the pilot rule.

**Plan.**
- Replace the iid-Pareto surrogate with the `max_coord` surrogate
  from `spectral_control_variate` (ρ² ≈ 0.74).
- Add a second panel comparing surrogate **kinds** at fixed pilot
  rule, alongside the pilot-rule comparison at fixed surrogate.
- Subtitle: "Pilot rule matters only when the surrogate is
  informative."

---

## F7 — stratified CdMC  🔴

**Intended.** Compare unstratified, proportional-stratified, and
Neyman-stratified CdMC. Show that stratification reduces work-
normalized variance.

**Now.** Visual: three side-by-side bars. **Two numerical bugs:**

1. **Neyman estimator is biased.** The CSV shows
   `mu_hat[neyman] = 0.027` vs `0.025` for the other two. The Neyman
   variance is also **10× higher** than the proportional version.
2. **Runtime numbers are meaningless.** The figure measures
   wall-clock time on the *post-processing* of strata (Neyman: 10 µs,
   proportional: 309 µs, unstratified: 2.3 ms) without including
   the CdMC kernel cost itself.

**Root cause.**
- I used Neyman weights $w_i \propto \mathrm{sd}_i$ both for the
  estimator and for variance reduction. Neyman weights only inform
  sample *allocation*; the estimator must average with the
  stratum-probability weights $\pi_i = n_i/n$. Conflating the two
  gives a biased estimator.
- The runtime measurements bracket only the stratum-aggregation
  step, not the full CdMC.

**Plan.**
- Replace the Neyman estimator with a proper *Neyman-allocated*
  scheme: run the unstratified CdMC to estimate `sd_i` on a pilot;
  then allocate $n_i = n \cdot w_i^{\text{Neyman}}$ samples to each
  stratum and average using $\pi_i$.
- Time the full pipeline (sampling + kernel + aggregation) for each
  estimator.
- Move the runtime numbers to a separate panel; keep the variance
  comparison on the primary y-axis.
- Add a math-correctness test asserting
  `|mu_neyman - mu_unstrat| < 5σ`.

---

## F8 — second-order independent expansion  🟢

**Intended.** Show that the corrected second-order expansion has
relative error an order of magnitude below the first-order
asymptotic across the threshold sweep.

**Now.** Two semilog curves: first-order $|\cdot|$ rel err 0.2–0.7;
second-order 0.01–0.04 — exactly the manuscript prediction.

**Issues.** None substantive. Could add a 10× reference line to
make the order-of-magnitude gain visually obvious.

**Plan.**
- Add a faint horizontal line at `first_order_err / 10` to visually
  call out the order-of-magnitude improvement.
- Title: "Second-order correction reduces error by ~10×" instead of
  the generic phrasing.

---

## F9 — single-portfolio VaR/ES path  🟢

**Intended.** Per-portfolio rolling VaR/ES at 99% and 99.5%.

**Now.** 1100 rolling dates with VaR₉₉, ES₉₉, VaR₉₉.₅, ES₉₉.₅.
CSV shows VaR ≈ 0.065 / 0.080 and ES ≈ 0.094 / 0.116 — sensible
orderings (ES > VaR; VaR₉₉.₅ > VaR₉₉).

**Issues.**
- Single-panel overlay of four series is busy.
- Realized loss series can dominate the y-axis if it has a few
  large excursions.

**Plan.**
- Two-panel layout: realized loss + VaR (top), ES (bottom).
- Mark exception dates (hits) as crosses on the loss series.
- Subtitle: "Mkt-RF, n=1100 trading days, FF3 factor model, 400-day
  rolling window".

---

## F10 — backtest rolling exception rate  🟢

**Intended.** Rolling violation rate vs the 1% / 0.5% target lines.

**Now.** 2200 rows × 2 levels = 1100 dates × {99%, 99.5%}. Rolling
violation rate plotted vs target.

**Issues.**
- The 60-day rolling window can show transient violations far above
  the target during a calm period (small sample size noise).
- No explicit "in/out of tolerance band" shading.

**Plan.**
- Add ±2σ tolerance band on the rolling violation rate (a
  Wilson-style binomial CI) around the target line.
- Shade out-of-band intervals in light red.

---

## F11 — common-shock geometry  🟢

**Intended.** Show that the empirical tail tracks the latent-shock
constant, not the misspecified observed-axes constant.

**Now.** Three log-log curves: latent (green) > observed (dashed
purple); empirical (blue dots) sits between but much closer to
latent. CSV confirms: mean rel-err to latent = 0.43, to observed =
0.79.

**Issues.**
- At x=5 the empirical tail is 0.9999 (saturated). The story is
  invisible there. The interesting range is x ∈ [10, 80].
- Crisis-window shading would help: "where the misspecification
  bites most".

**Plan.**
- Trim the x-axis to start at 10.
- Annotate the gap "latent vs observed" with a vertical line + text
  ratio (`latent/observed ≈ 2.8`).
- Subtitle: "Misspecified observed-axes constant under-states the
  loading-aligned tail by ~2.8×".

---

## F12 — empirical spectral simplex  🟢

**Intended.** Empirical angular exceedances on the 2-simplex,
verifying non-axis spectral mass under MRV with Dirichlet angles.

**Now.** 500 yellow dots inside the triangle, spread roughly evenly
with slight pull to the centroid — exactly what Dirichlet(1.5,1.5,1.5)
predicts.

**Issues.**
- Vertices not labelled (no `e_1, e_2, e_3` markers).
- No exposure direction indicator.
- Single-colour scatter — the `contribution = (a^T θ)^α` column
  could colour-map the points to show the loss-functional
  weighting.

**Plan.**
- Add vertex labels at the three corners.
- Use the `contribution` column as a colormap (FACTORTAIL_CMAP).
- Add a dashed loss-iso-contour `a^T θ = const` line.

---

## F13 — hidden-cone diagnostic  🟡

**Intended.** Show axis term, hidden pair-cone term, and empirical
tail across thresholds, with the hidden term decaying at the steeper
$\alpha_2$ slope.

**Now.** Axis (blue) overlaps empirical (green) almost exactly.
Hidden term (orange) two orders of magnitude smaller, clipped at
x=40 (sparse).

**Issues.**
- The interesting design has $\alpha_2 = \alpha$; here we set
  $\alpha_2 = 3 > \alpha = 2$, so the hidden term decays *faster*
  than axis. The figure shows the *non*-interesting case.
- At x=40 the hidden term has < 5 sample points, looks degenerate.

**Plan.**
- Run a second design with $\alpha_2 = \alpha = 2$ (matched scale)
  and `hidden_prob = 0.5` so the hidden term is **comparable** in
  magnitude to the axis term. That's the regime the manuscript wants
  to highlight.
- Use $n = 10^6$ replicates so the hidden term doesn't drop below
  the empirical-tail floor at large x.
- Side-by-side: "hidden scale = axis scale" vs "hidden scale > axis
  scale" panels.

---

## F14 — simulation dashboard  🟡

**Intended.** Bar chart of estimator SE and runtime across the six
DGP families.

**Now.** Three bars per panel (Family I, II, V only; III, IV, VI
omitted). SE values are all ≈ 0.0025 — three estimators each within
0.0001 of each other.

**Issues.**
- Three families is incomplete; the dashboard should cover all six.
- All-SE-the-same bars are uninformative; the manuscript wants to
  show which estimator wins per family.
- Y-axis units are absolute SE; relative SE (SE/μ̂) would be a
  better comparator.

**Plan.**
- Run all six families and add Family III (block CdMC) and Family
  IV (copula CdMC) bars; Family VI uses the cone-mass estimator.
- Two-panel: left = relative SE; right = WNRE = `sqrt(var * runtime) / μ̂`.
- Use semilog y-axis so order-of-magnitude differences are visible.
- Annotate each bar with `μ̂` so the reader sees the underlying
  probability scale.

---

## F15 — tail-dependence heatmap  🟢

**Intended.** Pairwise $\chi$ and $\eta$ matrices on a real-data
panel.

**Now.** 3 factor pairs (Mkt-RF, SMB, HML). χ ranges from 0.20 to
0.61, η from 0.86 to 1.08. Heatmaps look fine.

**Issues.**
- Only 3 factors. With FF5 + momentum we'd have 6 factors and 15
  pairs — more visually compelling.
- Diagonal is excluded but the cells display as zero with the
  divergent colormap centered on 0.5 — visually misleading.

**Plan.**
- Switch to the FF5 panel (offline synthetic, n=5000) for a 5×5
  heatmap.
- Mask the diagonal (or set to NaN with a `set_bad('lightgrey')`).
- Two-row layout: chi on top, eta on bottom; one shared colorbar
  each.

---

## F16 — VaR/ES dashboard  🟢

**Intended.** Two-panel rolling VaR/ES at 99% and 99.5% with
exception markers.

**Now.** Two panels stacked, constrained-layout. ES > VaR ordering
correct; few exception markers.

**Issues.**
- Sub-plots are still slightly tight (4.0 inches per panel).
- Realized loss series (grey) is hard to distinguish from the
  background; line is too thin.

**Plan.**
- Bump to `figsize=(11, 4.5 * n_panels)` and `linewidth=1.0` on the
  loss series.
- Add a third panel showing exception count per 60-day window
  (rolling violation rate) — borrows from F10.

---

## F17 — rolling spectral measure  🟢

**Intended.** Rolling empirical spectral mass across periods.

**Now.** Three positive bars per factor (Mkt-RF ~0.56, SMB ~0.25,
HML ~0.18), all three periods very similar.

**Issues.**
- The three periods are visually indistinguishable because the
  synthetic FF panel is stationary. The diagnostic *can't* show
  period-to-period change here.
- Could add a "crisis window" period that injects a regime shift
  in the synthetic DGP for illustration.

**Plan.**
- Inject a synthetic crisis window (last 200 days reweight to
  concentrate angular mass on Mkt-RF) so the late period shows a
  visible shift.
- Alternative: drop F17 from the synthetic demo and produce only
  when live FF data is available.

---

## F18 — Hill stability plots  🟢

**Intended.** Hill $\widehat\alpha$ across $k$ for each factor side.

**Now.** Three curves (Mkt-RF / SMB / HML right tail). Mkt-RF
plateaus near 3.0 (synthetic df=4 ⇒ tail index 4 should be visible
at small k; Hill biases downward for larger k). SMB/HML start near
4.3 and drop.

**Issues.**
- POT estimator curve not plotted (it's in the CSV but only Hill
  is on the figure).
- 95% CI bands not shown.

**Plan.**
- Overlay POT $\widehat\alpha$ curve as a dotted line per factor.
- Add CI bands as `fill_between` with `alpha=0.15`.
- Mark the "selected_threshold" k with a vertical dashed line per
  factor.

---

## F19 — bootstrap-scheme audit  🟡

**Intended.** Compare iid / block / stationary bootstrap coverage on
a known-truth AR(1)-injected MRV series.

**Now.** All three schemes achieve coverage 1.0 at every k. The
coverage panel is therefore a flat line at 1 — uninformative.

**Issues.**
- Single seed, single design → no variance in the coverage
  proportion (it's deterministic: covered or not).
- AR(1) ρ = 0.4 is too mild; under stronger serial dependence iid
  bootstrap would under-cover.

**Plan.**
- Run **B = 50** independent replications of the design and report
  empirical coverage proportions (with binomial SE bands).
- Add ρ ∈ {0.0, 0.4, 0.7, 0.9} as a sweep so the panel becomes
  "coverage vs ρ for each scheme".
- Expected: iid stays at ≈ 0.95 for ρ = 0; drops below 0.85 for
  ρ ≥ 0.7. Block/stationary stay near 0.95.

---

# Improvement-plan summary table

| Figure | Severity | Effort | Headline fix |
|---|---|---|---|
| F1  | 🟢 | 0.5 h | Recolor first-order; drop CI from legend; annotate ratio at the deep tail |
| F2  | 🟡 | 1 h   | Extend x-grid; add SE bands; add first-order reference |
| F3  | 🔴 | 2 h   | Rewrite rate formula: $1/\widehat\nu$ with BRE asymptote |
| F4  | 🔴 | 1 h   | Apply F3 fix; label heterogeneous designs |
| F5  | 🟢 | 0.5 h | Apply F3 fix; cosmetic only |
| F6  | 🟡 | 2 h   | Swap surrogate to max_coord; add surrogate-kind panel |
| F7  | 🔴 | 3 h   | Correct Neyman estimator; honest runtime measurement |
| F8  | 🟢 | 0.5 h | 10× reference line; better title |
| F9  | 🟢 | 1 h   | Two-panel layout; exception markers |
| F10 | 🟢 | 1 h   | Wilson tolerance bands |
| F11 | 🟢 | 0.5 h | Trim x-axis; ratio annotation |
| F12 | 🟢 | 1 h   | Vertex labels; contribution colormap; exposure contour |
| F13 | 🟡 | 2 h   | Add matched-scale design; bump n; side-by-side panels |
| F14 | 🟡 | 1 h   | Add Families III/IV/VI; semilog y; annotate μ̂ |
| F15 | 🟢 | 0.5 h | FF5 panel; mask diagonal |
| F16 | 🟢 | 0.5 h | Larger panels; thicker loss line; rolling-rate panel |
| F17 | 🟢 | 1 h   | Inject crisis window OR defer to live FF |
| F18 | 🟢 | 1 h   | POT overlay; CI bands; selected-threshold marker |
| F19 | 🟡 | 2 h   | Replication averaging; ρ sweep |

**Total budget: ≈ 21 hours of focused work.**

The 🔴 broken figures (F3, F4, F6, F7) should be fixed before the
next release. The 🟡 weak figures are correct but undersell their
diagnostic; they're optional polish.

# Suggested fix order

1. **F3 + F4 + F5** as a single PR (shared rate-formula refactor).
2. **F7** as its own PR (Neyman bias fix needs care).
3. **F6** swap to spectral surrogate (depends on `spectral_control_variate`).
4. **F19** add replication averaging (small change, big payoff).
5. **F1 + F8 + F11** cosmetic touch-ups in one sweep.
6. **F12 + F15 + F18** plotting polish in one sweep.
7. **F2 + F13 + F14 + F17** content additions (data + design).
8. **F9 + F10 + F16** real-data panel polish.
