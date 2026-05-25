# Plan to ship FactorTail v1.0

A concrete punch-list to finish the implementation, tests, experiments,
and figure/table generation that the manuscript needs. Each item has an
acceptance criterion, an effort estimate, and a dependency chain.

The current state (commit `bee5804`):

- 50 modules, src/ layout, MIT-licensed.
- 6 DGP families (I–VI), 5 CdMC estimators, control-variate + HRV mixture.
- 5 copula types with conditional kernels (Gaussian, Student-t, Clayton in
  any dim; Gumbel / Frank in d=2).
- Hill / Pickands / POT-GPD, χ / χ̄ / η, empirical spectral measure +
  IID / block / stationary bootstrap.
- Fama–French loader (online + offline-synthetic), rolling VaR/ES,
  Kupiec / Christoffersen / DQ / Acerbi–Szekely.
- 20 schema'd CSV outputs + 10 figure PDFs, all schema-validated.
- 6 priority-run records (P1–P6) pass `factortail validate-run`.
- 113 tests of mathematical correctness, all passing.
- App. G replacement contract enforced.
- MkDocs site deployed to `gh-pages`.

What follows is what's still open, ranked.

---

## Tier A — manuscript completion (high priority, ≤ 2 weeks)

These are the gaps that prevent dropping `(PLANNED.)` / `(PARTIAL.)`
prefixes in the manuscript captions.

### A1. Original-schema simulation diagnostics (F2–F7)

The current SCHEMA.md (in `docs/report/`) lists six efficiency-diagnostic
figures that were never wired up. The long-form manuscript draft does
not currently embed them but they're needed to back up §3 / §7 claims.

| Figure | Diagnostic | Effort | Owner |
|---|---|---|---|
| `F2_max_vs_sum` | $P(M_N>x) / P(S_N>x)$ ratio under independence; verifies `thm:catastrophe-exact` | 0.5 d | Family I |
| `F3_exp_eff_vs_x` | exponential efficiency rate $\lambda_n(x)$ vs threshold | 0.5 d | Family I |
| `F4_exp_eff_vs_alpha` | rate vs $\bar\alpha$ at common vs heterogeneous indices | 0.5 d | Family I |
| `F5_exp_eff_vs_amin` | rate vs $\alpha_{\min}$ in heterogeneous Pareto sums | 0.5 d | Family I |
| `F6_relative_error` | oracle vs sample-split VRE — handoff open question Q1 | 0.5 d | Family I + control variate |
| `F7_stratified` | stratified CdMC variance vs unstratified | 0.5 d | Family I |

**Acceptance:** each script writes a schema-validated CSV + PDF; the
schema entry is added to `factortail.io.schema`; a math-correctness test
is added to `tests/unit/`. Total: **3 days**.

### A2. F9–F10 single-portfolio VaR/ES outputs

The original schema reserves `F9_var_path` and `F10_backtest` for a
single-portfolio time series (the `F16` we have today is the *dashboard*
overlay). Worth keeping if §9 wants per-portfolio breakouts.

**Acceptance:** schema rows, generation scripts, math tests. **1 day.**

### A3. Tables that are still in the long-form manuscript but not yet
populated from generated CSVs

| Table | Status |
|---|---|
| `T_simulation_grid` | (PARTIAL.) — needs truth-method and outcome columns |
| `T_estimator_summary` | already populated (categorical descriptors); no CSV needed |
| `T_dependent_estimator_summary` | same |
| `T_experiment_status` | static categorical labels; verify against manifest |
| `T_extension_ranking` | static categorical labels; ditto |
| `T_literature_map_dependent` | static; ditto |
| `T_planned_real_data_figures` | static; ditto |
| `T_compute_cost` (legacy schema) | superseded by `T_runtime_placeholder`; mark as such |

**Acceptance:** every (PARTIAL.) prefix dropped where the corresponding
CSV exists; every (PLANNED.) prefix dropped where the artifact has
landed. **0.5 day.**

### A4. Caption-prefix sweep

Mechanical pass: for every figure/table with a generated companion in
`results/`, drop `\textbf{(PLANNED.)}` / `\textbf{(PARTIAL.)}` in the
caption. Re-build the manuscript locally.

**Acceptance:** zero `(PLANNED.)` / `(PARTIAL.)` prefixes remain on
artifacts that ship a CSV. **0.5 day.**

### A5. Handoff Q1 — pilot-size benchmark

Compare $n_0 \in \{\sqrt n,\, n/\log n,\, n^{2/3}\}$ for the
sample-split control-variate estimator on Family I. Drives the §7
"recommended pilot size" claim.

**Acceptance:** new `scripts/generate_F6_relative_error.py` (or piggyback
on A1) with the three pilot rules; a row of `T_sim_results_independent`
records the WNRE ranking. **1 day.**

### A6. Handoff Q2 — hidden-tail scale benchmark

Compare Ledford–Tawn $\eta$ against a direct cone-mass estimator on
Family VI as the estimator of $\overline H_2$. Drives the §6
"recommended hidden-tail estimator" claim.

**Acceptance:** new column on `T_sim_results_dependent` for Family VI
rows; math test that recovers the true $\alpha_2$ within bootstrap SE on
a Pareto-pair design. **1 day.**

---

## Tier B — implementation maturity (medium priority, ≤ 2 weeks)

### B1. Vectorize the dependent CdMC and block CdMC inner loops

Both currently use Python-level `for m in range(n)` loops. For $n=20{,}000$
this is fine; for $n \ge 10^5$ it's the bottleneck.

**Acceptance:** identical numerical output (within 1e-12) but ≥ 10×
faster on n=50k. **2 days.**

### B2. Higher-dimensional Gumbel and Frank conditionals

Currently both are bivariate-only. The manuscript's vine-truncation
discussion (§4 copula CdMC) wants $d > 2$.

**Acceptance:** d-dim closed-form or numerically-integrated conditional
survival with a Monte Carlo consistency test. **2 days.**

### B3. Spectral measure: handoff Q4 — bootstrap-scheme audit

`bootstrap_bands` ships all three schemes (iid / block / stationary).
Add a head-to-head benchmark on a stationary Pareto-mixture time
series and document which scheme to recommend.

**Acceptance:** new figure (or sub-figure of F17) with coverage curves
per scheme; method note in `docs/diagnostics.md`. **1 day.**

### B4. Live Fama-French downloader

`load_fama_french(offline=False)` is implemented but not exercised in
CI (network access blocked). Wire a `make test-live` target that pulls
the public ZIP and runs the full P6 pipeline.

**Acceptance:** local `make test-live` succeeds; CI continues to use
offline-synthetic. **0.5 day.**

### B5. CRSP licensed extension (P7, optional)

Scaffold `factortail.real_data.crsp` with a WRDS shim that respects the
license: derived per-portfolio CSVs only, no raw CRSP files.

**Acceptance:** WRDS pull stubbed behind an env var; documentation note
in `docs/datasets.md`. **2 days** (skeleton); full execution depends on
WRDS access.

### B6. Mypy clean

Roughly 20 type errors in script bootstrap + dgp dispatchers + copula
type narrowing. Currently the pre-commit hook is informational.

**Acceptance:** `mypy src/factortail` exit 0; gate the pre-commit hook.
**1.5 days.**

### B7. Hypothesis property-based tests

Add a `tests/property/` directory with hypothesis strategies for:

- Tail distributions (monotone sf, ppf inverse-of-sf, alpha range).
- Regular variation (sum-tail = sum of sf in deep tail).
- CdMC unbiasedness (mu_hat close to crude MC reference under known DGP).

**Acceptance:** 5 property-based tests added; CI matrix still green.
**1 day.**

### B8. Performance benchmark page

A `docs/performance.md` (or `benchmarks/`) with reproducible timing for
every estimator on a fixed grid; updated on each release.

**Acceptance:** `make benchmark` produces a CSV; the docs page renders
a table from it. **1 day.**

---

## Tier C — release engineering (≤ 1 week)

### C1. CI matrix green

Verify the GitHub Actions run on `bee5804` passes for the full matrix
(Py 3.10–3.12 × Linux/macOS). Fix any genuine breakages.

**Acceptance:** all jobs green on `main`. **0.5 day** (assuming no
hidden environment issues).

### C2. Enable GitHub Pages

One-time repo setting: `Settings → Pages → Branch: gh-pages, /`. After
that, the live site at https://osolari.github.io/FactorTail/ updates
on every push to `main` via the workflow we just shipped.

**Acceptance:** the URL serves the saim-themed site. **5 minutes.**

### C3. Tag v0.1.0

```bash
git tag -a v0.1.0 -m "FactorTail v0.1.0: initial release"
git push origin v0.1.0
```

Create a GitHub Release with the changelog excerpt.

**Acceptance:** release page lists the wheel and sdist. **0.5 day.**

### C4. TestPyPI dry run + PyPI publish

```bash
python -m build
twine upload --repository testpypi dist/*
# verify
pip install --index-url https://test.pypi.org/simple/ factortail
# real
twine upload dist/*
```

**Acceptance:** `pip install factortail` works from PyPI. **0.5 day.**

### C5. Zenodo DOI

Connect the GitHub repo to Zenodo, mint a DOI for the v0.1.0 tag,
update `CITATION.cff` with the DOI.

**Acceptance:** DOI resolves to the release artifact. **0.5 day.**

### C6. README badges sweep

Currently the README has placeholder badges. After C1–C5 land,
update with real CI / docs / PyPI / DOI badges.

**Acceptance:** all README badges click through to live pages.
**15 minutes.**

---

## Tier D — research bonus (lower priority)

### D1. Estimator coupling for the spectral control variate

The current `spectral_control_variate` exhibits weak correlation under
Pareto-radial MRV (rho^2 < 0.05). Investigate a tighter coupling:
either use the same radial draw in both Z and Y, or evaluate Z on
the spectral angles rather than the original X. The manuscript's
Proposition `prop:vre` is agnostic to the coupling; we just need a
choice that drives rho^2 ↑ 1.

**Acceptance:** rho^2 ≥ 0.5 on the Family V design; variance
reduction documented in §7. **1 day.**

### D2. Numba / Cython acceleration

After B1 vectorizes, the next bottleneck is the per-replicate kernel
evaluation. JIT compile the hot path.

**Acceptance:** ≥ 3× speedup on Family I with n=10^6. **2 days.**

### D3. GPU offloading (experimental)

For families where the sampler is pure numpy, a JAX or PyTorch backend
could fuse the entire CdMC into a single kernel.

**Acceptance:** opt-in `factortail.cdmc.gpu` namespace; equal numerical
output. **3 days.**

### D4. CLI: `factortail repro <id>`

Re-run a previously recorded `_run_<id>.json` and verify the produced
CSVs are byte-identical (the manuscript's reproducibility contract).

**Acceptance:** new CLI subcommand + integration test. **0.5 day.**

### D5. Tutorial notebooks

Three notebooks for the docs site (currently we don't have any):

1. `01_quickstart.ipynb` — minimal CdMC run end-to-end.
2. `02_dependent_designs.ipynb` — common-shock vs copula vs MRV.
3. `03_real_data_pipeline.ipynb` — rolling VaR/ES on the FF panel.

**Acceptance:** notebooks execute on CI; rendered in the docs site
via `mkdocs-jupyter`. **2 days.**

---

## Suggested sequence

```
week 1 ─ A1 (F2–F7) ─┬─ A5 (Q1 pilot) ──┐
                     └─ A6 (Q2 hidden) ─┤
                                        ├─ A3, A4 (manuscript sweep)
week 2 ─ A2 (F9/F10) ─ B1 (vectorize) ──┤
                                        │
                       B2 (copula d>2) ─┤
                       B3 (bootstrap)  ─┤
                                        │
week 3 ─ B6 (mypy) ─┬─ B7 (hypothesis) ─┤
                    └─ B8 (benchmarks) ─┤
                                        │
week 4 ─ C1 (CI) ─ C2 (Pages) ─ C3 (tag) ─ C4 (PyPI) ─ C5 (Zenodo) ─ C6 (badges)
```

D-tier items can be scheduled opportunistically — D5 (tutorials) is
the highest-value of the four because it directly improves the docs
site.

---

## Acceptance for "v1.0 ready"

All Tier-A and Tier-C items closed. Specifically:

- [ ] Every schema row in `factortail.io.schema` has a generation
  script and a generated CSV.
- [ ] Every figure / table placeholder in `docs/report/figures/` and
  `docs/report/tables/` is either populated or its `(PLANNED.)` /
  `(PARTIAL.)` prefix is justified by an explicit deferment note.
- [ ] `factortail validate-run` accepts P1–P6; P7 is documented as
  optional.
- [ ] CI is green; the live docs site renders the saim theme.
- [ ] v0.1.0 is tagged; PyPI install works.
- [ ] At least one independent reviewer can re-run `make run-all`
  and `factortail validate-run` from a fresh clone without
  intervention.

---

## Total effort estimate

| Tier | Days |
|---|---|
| A | 7.5 |
| B | 11 |
| C | 2.25 |
| D (optional) | 9 |
| **A + B + C (v1.0)** | **20.75** |

At one engineer half-time: ≈ 4 calendar weeks. At full time: ≈ 2 weeks.
