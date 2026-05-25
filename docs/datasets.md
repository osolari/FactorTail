# Data and DGPs

FactorTail uses three data sources, each with a single entry point.

## Synthetic — six simulation families (§8)

The DGP families live in `factortail.dgp`. Each exposes
`sample(size, rng) -> (size, N)`.

| Module | Family | Closed-form first-order constant |
|---|---|---|
| `factortail.dgp.IndependentINID` | I — independent inid (Pareto / Lomax / Burr / Student-t) | `first_order_sum_tail(marginals, x)` |
| `factortail.dgp.CommonShockModel` | II — common shock + idiosyncratic | `latent_constants()` (correct vs misspecified) |
| `factortail.dgp.LatentFactorModel` | II — general factor matrix `X = BZ + E` | `latent_tail_constant(exposure)` |
| `factortail.dgp.BlockModel` | III — independent blocks, within-block common shock | `fit_block_tail(block_model)` |
| `factortail.dgp.CopulaModel` | IV — heavy-tailed margins + copula (Gaussian / Student-t / Clayton / Gumbel / Frank) | via the conditional kernel |
| `factortail.dgp.RadialAngularMRV` | V — radial-angular MRV (axis / ray mixture / Dirichlet / empirical) | `spectral_constant_estimate(X, exposure, alpha)` |
| `factortail.dgp.HiddenConeMixture` | VI — axis + hidden-pair mixture, $\alpha_2 \ge \alpha$ | bootstrap or empirical |

All DGPs accept `from_spec(spec: dict)` for YAML-driven configuration.

## Public — Kenneth French Data Library

`factortail.real_data.fama_french.load_fama_french(name, *, offline=False)`
downloads (or reads cached) FF3 / FF5 / momentum / industry panels and
records:

- source URL,
- download timestamp,
- SHA-256 file hash,
- row count, first date, last date,
- parsing log.

### Offline / CI mode

`offline=True` (default in CI) returns
`factortail.real_data.fama_french.synthesize_panel(...)`: a deterministic
heavy-tailed surrogate with the same shape and column names as the
public panels. Margin tails are Student-t with df ∈ {4, 6}, coupled by a
single market common shock. Used by the test suite and by every
`generate_F1{5..8}*.py` script that doesn't have network access.

## Licensed — CRSP through WRDS (P7, optional)

The handoff plan reserves a CRSP path (`P7` of the priority manifest)
that mirrors `P6` over CRSP security-level data. Raw CRSP files **must
never be committed** (see
[`docs/report/appendices/F_data_specs.tex`](https://github.com/osolari/FactorTail/blob/main/docs/report/appendices/F_data_specs.tex)).
The hook is scaffolded; the implementation is conditional on
institutional WRDS access.

## Output schema

Every generated CSV under `results/` matches a row of
`factortail.io.schema.SCHEMA`. The same schema is mirrored verbatim in
[`results/SCHEMA.md`](https://github.com/osolari/FactorTail/blob/main/results/SCHEMA.md);
a pre-commit hook (`scripts/_dev/check_schema_headers.py`) keeps the two
in sync. See [Reproducibility](reproducibility.md) for the
provenance contract.
