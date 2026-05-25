# Manuscript

The companion manuscript lives in
[`docs/report/`](https://github.com/osolari/FactorTail/tree/main/docs/report)
as a TeX-Live-compatible LaTeX project.

## Title

*Sharp Tail Asymptotics and Efficient Rare-Event Simulation for
Independent and Dependent Regularly-Varying Factor Models*

## Authors

- O. Shams Solari (sAIm Labs)
- F. Pourbabaee

## Build

```bash
cd docs/report
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Requires a standard TeX Live distribution plus `texlive-fonts-extra`
(provides `dsfont.sty`). The `algorithm`, `algorithmicx`, `booktabs`,
`longtable`, `tabularx`, `hyperref`, `cleveref`, `microtype`,
`enumitem`, and `xcolor` packages are required.

## Section-by-section module map

See [Concepts](concepts.md) for the full theorem → module table. In
short:

| Section | Module |
|---|---|
| §3 Independent baseline | `factortail.cdmc.independent` |
| §4 Dependent CdMC + shock bases | `factortail.cdmc.{dependent,latent_shock,block}` |
| §5 MRV + spectral CdMC | `factortail.cdmc.spectral`, `factortail.diagnostics.spectral` |
| §6 Hidden RV | `factortail.hrv` |
| §7 Estimator families + efficiency | `factortail.estimators` |
| §8 Simulation study | `factortail.dgp` + `scripts/generate_*.py` |
| §9 Real-data protocol | `factortail.real_data.rolling_var_es` |
| App. E pseudo-code | every `alg:*` has a 1:1 Python entry point |
| App. F data specs / IO | `factortail.io`, `results/SCHEMA.md` |
| App. G manifest | `factortail.manifest` |

## Placeholder figures and tables

The manuscript ships with placeholders that are replaced by generated
artifacts only after passing the App. G contract — see
[Reproducibility](reproducibility.md) and [Results](results.md).

Each placeholder TikZ file under
[`docs/report/figures/`](https://github.com/osolari/FactorTail/tree/main/docs/report/figures)
is wired to a generated PDF with the same basename; an
`\includegraphics[width=0.85\linewidth]{figures/<basename>.pdf}`
directive points at the artifact produced by the corresponding
`scripts/generate_<basename>.py` driver.

## Citation

See the [home page](index.md) for the BibTeX entry, or
[`CITATION.cff`](https://github.com/osolari/FactorTail/blob/main/CITATION.cff)
for the machine-readable citation block.
