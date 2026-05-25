# Regular variation

## Univariate

A measurable function :math:`\overline G : (0, \infty) \to (0, \infty)` is
**regularly varying with index** :math:`-\alpha` if

$$\lim_{x\to\infty} \frac{\overline G(t x)}{\overline G(x)} = t^{-\alpha}
  \quad\text{for every } t > 0.$$

This is the workhorse of the manuscript's first-order theory. The
[`factortail.utils.tails`](../api/utils.md) module implements four
canonical heavy-tailed families, each with exact `sf`, `logsf`, and
`ppf`:

| Family   | Distribution            | Tail constant ``c``                     |
|----------|-------------------------|-----------------------------------------|
| Pareto   | :math:`P(X>x)=(x/s)^{-\alpha}` | :math:`s^\alpha`                  |
| Lomax    | :math:`P(X>x)=(1+x/s)^{-\alpha}`| :math:`s^\alpha`                  |
| Burr     | :math:`P(X>x)=(1+(x/s)^k)^{-d}` | :math:`s^{kd}`                    |
| Student-t| :math:`P(T>x)`                 | :math:`\tfrac12 K_\nu s^\nu`      |

## Multivariate (MRV)

`factortail.dgp.RadialAngularMRV` constructs an MRV vector :math:`X = R\Theta`
with an exact Pareto radial component and a configurable angular component:

- ``axis``: discrete mass on coordinate axes (independent baseline);
- ``ray_mixture``: mixture of fixed rays (common-shock geometry);
- ``dirichlet``: continuous Dirichlet on the simplex;
- ``empirical``: bootstrap resample from an angular pool.

The [`factortail.diagnostics.spectral`](../api/diagnostics.md) module
exposes the empirical spectral measure estimator used in §5 and §9.
