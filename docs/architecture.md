# Architecture

`FactorTail` is organised in narrow, composable layers.

```
┌──────────────────────────────────────────────────────────────┐
│  scripts/generate_F*.py / generate_T*.py  (one per artifact) │
├──────────────────────────────────────────────────────────────┤
│  factortail.cli  +  factortail.experiments.dispatch          │
├───────────────┬────────────────┬─────────────────────────────┤
│ factortail.   │ factortail.    │ factortail.                 │
│  cdmc.*       │  hrv.*         │  diagnostics.*              │
│  (§3-5)       │  (§6)          │  (§3 / §6 / §9)              │
├───────────────┼────────────────┼─────────────────────────────┤
│ factortail.   │ factortail.    │ factortail.                 │
│  dgp.*        │  copula.*      │  estimators.*               │
├──────────────────────────────────────────────────────────────┤
│ factortail.real_data.* (Fama-French loader, rolling VaR/ES)  │
├──────────────────────────────────────────────────────────────┤
│ factortail.io.* (schema, writers, validators)                │
│ factortail.manifest.* (replacement contract)                 │
│ factortail.plotting.* (unified theme + panel helpers)        │
│ factortail.utils.* (tails, regular variation, seeds, …)      │
└──────────────────────────────────────────────────────────────┘
```

Each layer depends only on the layers below it. The `scripts/` layer is
intentionally thin: it owns CLI plumbing, YAML loading, and the
provenance stamp, then delegates to the library.

## Why src/

The `src/` layout prevents the local checkout from shadowing the
installed package on `PYTHONPATH`. The CI matrix would otherwise pass
`tests/` against the checkout but ship a broken wheel.

## Why separate scripts/ from the library

The library is a stable API; the scripts are the experiment plan. A
manuscript revision should touch `scripts/` and a YAML, never the
library, in the common case. The manifest in
`factortail.manifest.replacement` ties the two together.
