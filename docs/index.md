# FactorTail

Reference implementation of *Sharp Tail Asymptotics and Efficient Rare-Event
Simulation for Independent and Dependent Regularly-Varying Factor Models*
by O. Shams Solari and F. Pourbabaee.

`FactorTail` mirrors the manuscript section-by-section: every theorem in
§§3–7 has a Python implementation in `factortail.cdmc.*`, every data family
in §8 has a generator in `factortail.dgp.*`, and every figure or table in
the paper has a one-script entry point under `scripts/`.

## Three things to read first

1. [Installation](install.md) — `pip install -e ".[dev,plot]"`.
2. [Quickstart](quickstart.md) — running one figure from the CLI.
3. [Theory map](theory/manuscript_map.md) — how the code matches the
   manuscript section-by-section.

## Why FactorTail?

- **Sharp first-order constants** under independence, common shocks,
  blocks, copulas, MRV, and hidden RV — not just the textbook one-large-jump
  asymptotic.
- **BRE diagnostics** built into every estimator (see
  [`factortail.cdmc.base.CdMCResult`](api/cdmc.md)).
- **One script per figure / table**, every script writes a schema-validated
  CSV plus a publication-quality PDF/PNG using the unified
  [plotting theme](plotting.md).
- **Replacement contract** (appendix G of the paper) implemented in
  `factortail.manifest`: a generated artifact may replace a manuscript
  placeholder only after seed, config hash, git hash, and validated CSV are
  recorded.

## At a glance

```python
from factortail.cdmc import independent_cdmc
from factortail.utils.tails import ParetoTail

margs = [ParetoTail(alpha=2.0, scale=1.0) for _ in range(3)]
res = independent_cdmc(margs, x=20.0, n=20_000, seed=42)
# res.mu_hat is an unbiased estimate of P(S_3 > 20);
# res.variance and res.ci_low / res.ci_high give the BRE diagnostic.
```

## Stable links

- [GitHub repository](https://github.com/osolari/FactorTail)
- [Manuscript](https://github.com/osolari/FactorTail)
- [Manifest (App. G)](experiments/manifest.md)
- [API reference](api/cdmc.md)
