# Estimator families

FactorTail ships six estimator families, all unified by the
[`CdMCResult`](api.md#3-5-conditional-monte-carlo-factortailcdmc)
contract (point estimate, sample variance, runtime, Bernstein CI,
estimator-specific diagnostics in `extra`).

## §3 Independent summed CdMC

`factortail.cdmc.independent.independent_cdmc(marginals, *, x, n)` is the
baseline of the manuscript. Given independent margins $X_1,\dots,X_N$
the estimator is

$$
  Z^{\mathrm{ind}}(x) \;=\; \sum_{i=1}^N \overline F_i(T_i(x)),
  \quad T_i(x) = (x - S_{-i}) \vee M_{-i}.
$$

Deterministic envelope $B(x) = \sum_i \overline F_i(x/N)$ and asymptotic
BRE constant $N^\alpha - 1$. The result's `extra["envelope"]` and
`extra["rel_envelope"]` expose the BRE diagnostic.

## §4 Dependent kernel CdMC

`factortail.cdmc.dependent.dependent_cdmc(sampler, kernel, *, x, n)`
implements Algorithm `alg:dep-cdmc`. The kernel is the conditional
survival $p_i(t; X_{-i}) = P(X_i > t | X_{-i})$ supplied by the caller.

The companion helpers
`factortail.cdmc.copula_kernel.build_copula_kernel(copula, marginals)` /
`build_copula_sampler(copula, marginals)` turn any
(copula, marginals) pair into the kernel callable that `dependent_cdmc`
expects. Closed-form conditional survivals are exposed for Gaussian,
Student-t (any dimension), Clayton (any dimension), and bivariate
Gumbel and Frank.

## §4 Latent-shock CdMC

`factortail.cdmc.latent_shock.latent_shock_cdmc(B, exposure, shocks, ...)`
implements Algorithm `alg:latent-cdmc` for the factor model
$X = BZ + E$. Transforms to the latent shock basis via $q = B^\top a$,
applies independent CdMC to the signed shock contributions
$q_k Z_k$, and adds the idiosyncratic axis terms. Returns the
attribution-by-shock alongside the standard `CdMCResult`.

## §4 Block CdMC

`factortail.cdmc.block.block_cdmc(block_sampler, block_tail, K, ...)`
runs independent summed CdMC on block sums. Helper
`factortail.cdmc.block.fit_block_tail(block_model, method=...)` produces
the `block_tail(t, k)` callable, either by closed-form Pareto when every
block is a common-shock model or by nested high-budget MC with log-grid
interpolation.

## §5 Spectral / radial CdMC

`factortail.cdmc.spectral.spectral_cdmc(angle_sampler, radial, exposure, x, n)`
implements Algorithm `alg:spectral-cdmc`. For a radial-angular MRV
representation $X = R\Theta$ and loss functional $\ell(\theta) = a^\top \theta$,

$$
  Z^{\mathrm{spec}}(x) \;=\; \overline F_R\bigl(x / \ell(\Theta)\bigr)
                              \mathbf 1\{\ell(\Theta) > 0\}.
$$

For exact Pareto radials this collapses to
$Z^{\mathrm{spec}}(x) = x^{-\alpha}(\ell(\Theta)_+)^\alpha$, so the
relative variance is independent of $x$.

## §6 Hidden-cone mixture estimator

`factortail.hrv.mixture_estimator.hrv_mixture_estimator(axis_estimator, hidden_estimator, pi_x, n)`
stratifies the rare event into an axis component and a hidden-cone
component, inverts the stratification weights, and returns an unbiased
estimator whose variance does not waste samples on a cone that is
negligible at the current threshold.

## §7 Control variate (oracle and sample-split)

Two flavours of Proposition `prop:vre`:

- `factortail.estimators.control_variate(Z, Y, m_Y=...)` — oracle
  centering. With $\rho(x)\to 1$ as $x\to\infty$ this is VRE.
- `factortail.estimators.control_variate(Z, Y)` — sample-split
  centering with pilot of size $n_0$ (defaults to $\sqrt n$).
  Asymptotically unbiased; the centering estimate contributes an
  additional $1/n_0$ variance term.

`factortail.estimators.spectral_control_variate(...)` is a coupled
pairing of independent CdMC with the spectral surrogate that shares the
$(R, \Theta)$ draw across both estimators.

## Confidence intervals

All `CdMCResult` instances carry a 95% Bernstein CI by default
(Theorem `thm:bernstein-ci`, implemented in
`factortail.cdmc.base.bernstein_ci`). Plain sample-Gaussian CIs are
available via `factortail.cdmc.base.sample_ci`.
