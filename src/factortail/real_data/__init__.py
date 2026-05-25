"""Real-data pipeline: Fama-French loaders, rolling VaR/ES, backtests.

* :mod:`factortail.real_data.fama_french` downloads and caches public
  Kenneth-French panels.
* :mod:`factortail.real_data.rolling_var_es` implements ``alg:real-data``.
* :mod:`factortail.real_data.backtests` runs Kupiec / Christoffersen /
  dynamic-quantile VaR tests plus Acerbi-Szekely ES tests.
"""

from factortail.real_data.fama_french import FFPanel, load_fama_french, synthesize_panel
from factortail.real_data.rolling_var_es import RollingVaRConfig, run_rolling_var_es

__all__ = [
    "FFPanel",
    "RollingVaRConfig",
    "load_fama_french",
    "run_rolling_var_es",
    "synthesize_panel",
]
