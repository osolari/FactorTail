# Math notes

A compact dictionary of the objects FactorTail tracks. For the
section-by-section manuscript map, see [Concepts](concepts.md); for
algorithm pseudo-code in code form, see [Estimator families](models.md).

## Univariate regular variation

A measurable function
$\overline G : (0, \infty) \to (0, \infty)$ is **regularly varying with
index** $-\alpha$ if

$$
  \lim_{x\to\infty} \frac{\overline G(t x)}{\overline G(x)} = t^{-\alpha}
  \quad\text{for every } t > 0.
$$

`factortail.utils.tails` provides four canonical heavy-tailed families,
each with exact `sf`, `logsf`, and `ppf`:

| Family | Distribution | Tail constant `c` |
|---|---|---|
| Pareto | $P(X>x)=(x/s)^{-\alpha}$ | $s^{\alpha}$ |
| Lomax | $P(X>x)=(1+x/s)^{-\alpha}$ | $s^{\alpha}$ |
| Burr | $P(X>x)=(1+(x/s)^k)^{-d}$ | $s^{kd}$ |
| Student-t | $P(T>x)$ | $\tfrac12 K_\nu s^\nu$ |

## Multivariate regular variation

$X\in\mathbb R^N$ is in $\mathrm{MRV}(\alpha, \overline G, \nu, \mathbb E)$ if
$\nu$ is a non-zero Radon measure on the cone $\mathbb E$ satisfying
$\nu(tA) = t^{-\alpha}\nu(A)$ and

$$
  \frac{P(X/x \in \cdot)}{\overline G(x)} \xrightarrow{v} \nu(\cdot)
  \quad\text{vaguely on } \mathbb E.
$$

In polar coordinates $X = R\Theta$ this factorises as
$\nu(\mathrm dr, \mathrm d\theta) = \alpha r^{-\alpha - 1}\mathrm dr\, S(\mathrm d\theta)$.
The angular measure $S$ on the unit sphere (or simplex on the positive
orthant) encodes the directional concentration of extreme vectors.

`factortail.dgp.RadialAngularMRV` constructs $X = R\Theta$ with an
exact Pareto radial and a configurable angular component
(`axis`, `ray_mixture`, `dirichlet`, `empirical`).

For a linear loss $\ell(z) = a^\top z$,
$P(\ell(X) > x) \sim \overline G(x) \nu(A_\ell)$ where
$\nu(A_\ell) = \int (\ell(\theta)_+)^\alpha S(\mathrm d\theta)$.

## Hidden regular variation

Ordinary MRV may report asymptotic independence: the limiting spectral
measure is concentrated on coordinate axes. The first-order tail
constant for $S_N$ then looks identical to the independent constant.
**Hidden RV** formalises the residual mass on a smaller cone
$\mathbb E_2$ at a slower scale.

$X \in \mathrm{HRV}(\alpha_2, \overline H_2, \nu_2, \mathbb E_2)$ if
$\overline H_2 \in \mathrm{RV}_{-\alpha_2}$ with $\alpha_2 \ge \alpha$ and
$P(X/x \in \cdot) / \overline H_2(x) \to \nu_2(\cdot)$ vaguely on
$\mathbb E_2$.

Two diagnostics:

- `factortail.hrv.ledford_tawn.ledford_tawn_eta(U, V, k)` — for
  independent uniforms $\eta = 1/2$; for the comonotone copula
  $\eta = 1$.
- `factortail.hrv.mixture_estimator.hrv_mixture_estimator(...)` — the
  stratified axis + hidden mixture estimator

$$
  Z^{\mathrm{mix}}(x) = \frac{\mathbf 1\{I=0\}}{\pi_x} Z_{\mathrm{axis}}(x)
                       + \frac{\mathbf 1\{I=1\}}{1-\pi_x} Z_{\mathrm{hid}}(x).
$$

## Conditional Monte Carlo identities

`thm:dep-cdmc-unbiased` (§4): for any joint distribution with regular
conditional laws,

$$
  P(S_N > x) = \sum_{i=1}^N \mathbb E\bigl[p_i(T_i(x); X_{-i})\bigr],
  \quad p_i(t; X_{-i}) = P(X_i > t \mid X_{-i}).
$$

This is the master identity that every CdMC variant in
[`models.md`](models.md) specializes.

## Bounded relative error (BRE) and VRE

For an unbiased estimator $Z(x)$ of $\mu(x)$,

$$
\begin{aligned}
\text{BRE:} &\quad \limsup_{x\to\infty}\operatorname{Var}Z(x)/\mu(x)^2 < \infty, \\
\text{VRE:} &\quad \operatorname{Var}Z(x)/\mu(x)^2 \to 0, \\
\text{log-efficient:} &\quad \liminf \log \mathbb E Z(x)^2 / \log \mu(x)^2 \ge 1.
\end{aligned}
$$

The independent CdMC has BRE constant $N^\alpha - 1$ in the limit
(Proposition `prop:ind-cdmc-bre`). Control-variate estimators
(Proposition `prop:vre`) can achieve VRE under oracle centering when
$\rho(x)\to 1$.

## Work-normalized variance

The **work** of $Z(x)$ at threshold $x$ is the mean cost per replicate
$\mathrm{cost}(Z; x)$. The **work-normalized variance** is
$W(Z; x) = \operatorname{Var}Z(x)\cdot\mathrm{cost}(Z; x)$ and the
**WNRE** is $\sqrt{W(Z; x)}/\mu(x)$.

## Bernstein-type CI

`thm:bernstein-ci` (§7): for an unbiased $Z(x)\in[0, B_Z(x)]$ with
$\operatorname{Var}Z(x)\le\sigma^2(x)$,

$$
  P\bigl(|\bar Z_n - \mu(x)| > \varepsilon\bigr)
  \le 2\exp\left\{-\frac{n\varepsilon^2}{2\sigma^2(x) + \tfrac{2}{3}B_Z(x)\varepsilon}\right\}.
$$

Used as the default 95% CI in every `CdMCResult` returned by
`factortail.cdmc.*`.
