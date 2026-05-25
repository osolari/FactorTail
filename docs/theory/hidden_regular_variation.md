# Hidden regular variation

Ordinary MRV may report asymptotic independence: the limiting spectral
measure lives on coordinate axes. In that case the first-order tail
constant for the sum looks identical to the independent constant. But
joint-tail mass can live on smaller cones at a slower scale; hidden
regular variation (HRV) formalises that phenomenon.

Definition (`def:hrv` in the manuscript): if
:math:`X \in \mathrm{MRV}(\alpha, \overline G, \nu_1, \mathbb E_1)` with
:math:`\nu_1` axis-supported, then :math:`X \in \mathrm{HRV}(\alpha_2,
\overline H_2, \nu_2, \mathbb E_2)` for some :math:`\alpha_2 \ge \alpha`
and hidden cone :math:`\mathbb E_2`.

`FactorTail` implements two HRV tools:

- **Diagnostic.** `factortail.hrv.ledford_tawn.ledford_tawn_eta` is the
  Hill-based :math:`\eta` estimator. For independent uniform margins
  :math:`\eta = 1/2`; for the comonotone copula :math:`\eta = 1`.
- **Mixture estimator.** `factortail.hrv.mixture_estimator.hrv_mixture_estimator`
  is the stratified axis-plus-hidden estimator of §6:

  $$Z^{\mathrm{mix}}(x) = \frac{\mathbf 1\{I=0\}}{\pi_x} Z_{\mathrm{axis}}(x)
                          + \frac{\mathbf 1\{I=1\}}{1-\pi_x} Z_{\mathrm{hid}}(x).$$

The hidden cone DGP (`factortail.dgp.HiddenConeMixture`) is a Family VI
generator with controllable hidden-cone mass and a configurable
:math:`\alpha_2 \ge \alpha`.
