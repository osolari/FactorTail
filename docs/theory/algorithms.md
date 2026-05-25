# Algorithms

The five algorithms in appendix E of the manuscript map 1:1 to Python
entry points:

| Pseudocode label       | Python                                                                |
|-------------------------|-----------------------------------------------------------------------|
| `alg:dep-cdmc`          | `factortail.cdmc.dependent.dependent_cdmc`                             |
| `alg:latent-cdmc`       | `factortail.cdmc.latent_shock.latent_shock_cdmc`                       |
| `alg:spectral-cdmc`     | `factortail.cdmc.spectral.spectral_cdmc`                               |
| `alg:real-data`         | `factortail.real_data.rolling_var_es.run_rolling_var_es`               |

## Numerical-stability conventions

Following remark `rem:numerical-stability` in the manuscript:

- Tail kernels are evaluated on log-scale (`TailDistribution.logsf`)
  whenever the deep tail is involved.
- Log-sum-exp is used to aggregate near-zero kernel evaluations.
- The sign correction for negative shock contributions
  (`q_k < 0`) is handled in `latent_shock_cdmc` by reflecting the shock
  distribution and dropping it from the right-tail estimator.

## Tie-breaking rule

Following `ass:tie`, the selected-maximum index is the smallest
``argmax`` coordinate. The implementation in `factortail.cdmc.independent._T_values`
uses ``np.sort`` to read the two largest values per row in :math:`O(N \log N)`
per replicate (sufficient for the dimensions used in §8).
