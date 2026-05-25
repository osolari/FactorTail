---
hide:
  - navigation
  - toc
---

<div class="saim-hero" markdown>
  <img src="assets/saim_logo.png" alt="sAIm Labs" class="saim-hero-logo">
  <h1>FactorTail</h1>
  <p><strong>Sharp tail asymptotics and efficient rare-event simulation</strong>
  for independent and dependent regularly-varying factor models. Exact
  conditional Monte Carlo identities under arbitrary dependence, MRV
  and hidden-RV diagnostics, and a rolling VaR/ES pipeline with formal
  Bernstein CIs.</p>
  <p class="saim-hero-badges">
    <a href="https://github.com/osolari/FactorTail">GitHub</a>
    <a href="report.md">Manuscript</a>
    <a href="quickstart.md">Quickstart</a>
    <a href="results.md">Results</a>
    <a href="api.md">API</a>
  </p>
</div>

<div class="saim-cite" markdown>
**Citation.** If FactorTail is useful to your research, please cite the
companion manuscript and the library together (see
[`CITATION.cff`](https://github.com/osolari/FactorTail/blob/main/CITATION.cff)):

> O. Shams Solari and F. Pourbabaee (2026). *Conditional Monte Carlo for
> Multivariate Heavy Tails: Latent Shocks, Spectral Measures, Hidden
> Cones.* sAIm Labs.

```bibtex
@article{solari2026factortail,
  title   = {Conditional Monte Carlo for Multivariate Heavy Tails:
             Latent Shocks, Spectral Measures, Hidden Cones},
  author  = {Shams Solari, Omid and Pourbabaee, Farzad},
  year    = {2026},
  url     = {https://github.com/osolari/FactorTail},
}
```
</div>

## What FactorTail does

FactorTail is the reference implementation of the manuscript, with a
narrow separation between **estimator algebra** and **experiment
orchestration**:

| Layer | What it computes |
|---|---|
| **Conditional Monte Carlo** | Independent, dependent-kernel, latent-shock, block, and spectral CdMC estimators with BRE diagnostics, Bernstein CIs, and a control-variate VRE pairing. |
| **DGP families** | Six data-generating processes (independent inid, common-shock, block, copula, MRV, hidden RV) with closed-form first-order constants. |
| **Diagnostics** | Hill / Pickands / POT-GPD tail-index estimators; pairwise $\chi$, $\bar\chi$, Ledford–Tawn $\eta$; empirical spectral measure with iid / block / stationary bootstrap bands. |
| **Real data** | Fama–French loader, rolling VaR/ES (Algorithm `alg:real-data`), Kupiec / Christoffersen / dynamic-quantile / Acerbi–Szekely Z2 backtests. |
| **Reproducibility** | PCG-style replicate seeds, config-hash provenance, schema-validated CSV writers, App. G replacement-rule enforcement. |

The §3 baseline estimator
$\widehat\mu = n^{-1}\sum_m \sum_i \overline F_i(T_i(X^{(m)}))$ has
asymptotic BRE constant $N^\alpha - 1$. The §4 identity
$\mathbb P(S_N > x) = \sum_i \mathbb E\,p_i(T_i; X_{-i})$ holds under
arbitrary dependence; FactorTail exposes the kernel $p_i$ for Gaussian,
Student-$t$, and Archimedean copulas in any dimension where a closed
form exists.

## Highlight reel

```python
import numpy as np
from factortail.cdmc import independent_cdmc
from factortail.utils.tails import ParetoTail

margs = [ParetoTail(alpha=2.0, scale=1.0) for _ in range(3)]
res = independent_cdmc(margs, x=20.0, n=20_000, seed=42)

res.mu_hat                  # unbiased estimate of P(S_3 > 20)
res.variance                # sample variance of Z
res.rel_sd                  # relative standard error
res.ci_low, res.ci_high     # empirical Bernstein CI
res.extra["envelope"]       # deterministic envelope sum_i sf_i(x/N)
```

## Headline empirical results

See [Results](results.md) for the embedded figures and validation
output. Selected snapshots from the offline-synthetic Fama–French run:

| Priority | Output | Diagnostic | Result |
|---|---|---|---|
| **P1** | `F1_tail_equivalence` | $\widehat\mu / \text{first-order}$ at $x=40$, $\alpha=2$ | ratio → 1 in the deep tail; second-order curve tracks CdMC almost exactly |
| **P2** | `F11_common_shock_geometry` | latent vs misspecified constant under positive same-sign loadings | empirical tail tracks latent (mean rel-err 0.43) vs observed-axes (0.79) |
| **P4** | `F12_spectral_simplex` | Dirichlet(1.5,1.5,1.5) angular mass on the 2-simplex | non-axis mass dominates; angle sums verified to 1 |
| **P5** | `F13_hidden_cones` | axis vs hidden-pair term at $\alpha=2$, $\alpha_2=3$ | hidden term decays at the steeper $x^{-3}$ rate |
| **P6** | `F18_hill_plots` | Hill stability on synthetic FF3 with df=4 | $\widehat\alpha_H \approx 3$ at $k = 200$ |

## Where to go next

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg } **[Quickstart](quickstart.md)**

    Install, run one experiment, render the figure. Under a minute.

-   :material-school:{ .lg } **[Concepts](concepts.md)**

    Theorem → module map; architecture diagram; replacement-contract
    summary.

-   :material-cog:{ .lg } **[Estimator families](models.md)**

    The six CdMC variants — independent, dependent kernel, latent
    shock, block, spectral, hidden-cone mixture — with the
    control-variate pairing.

-   :material-database:{ .lg } **[Data and DGPs](datasets.md)**

    Six simulation families + Fama–French loader (offline-synthetic
    surrogate for CI).

-   :material-chart-line:{ .lg } **[Diagnostics](diagnostics.md)**

    Hill / Pickands / POT tail-index estimators, $\chi$ / $\bar\chi$ /
    $\eta$ pairwise dependence, empirical spectral measure with
    bootstrap bands.

-   :material-test-tube:{ .lg } **[Math notes](math.md)**

    Univariate / multivariate / hidden regular variation, the CdMC
    identity, BRE / VRE / WNRE, Bernstein CI.

-   :material-checkbox-marked-circle-outline:{ .lg } **[Reproducibility](reproducibility.md)**

    Seeds, hashing, run records, App. G replacement contract.

-   :material-image-multiple:{ .lg } **[Results](results.md)**

    Every generated figure embedded inline with its diagnostic
    interpretation.

-   :material-book:{ .lg } **[API reference](api.md)**

    Every public class and function with manuscript cross-references.

-   :material-file-pdf-box:{ .lg } **[Manuscript](report.md)**

    Build instructions for the LaTeX source in
    [`docs/report/`](https://github.com/osolari/FactorTail/tree/main/docs/report).

</div>
