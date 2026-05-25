"""Replacement-rule enforcement for the manuscript artifact graph (App. G).

A placeholder figure or table may be replaced by a generated artifact only
when:

1. the source CSV exists and passes schema validation
   (:mod:`factortail.io.validators`);
2. the generation run records ``run_id``, ``config_hash``, ``git_hash``,
   and ``seed`` (see :func:`record_run`);
3. the generated PDF/TeX has the same basename as the placeholder;
4. the caption and label in the manuscript remain unchanged unless the
   underlying diagnostic changes.
"""

from factortail.manifest.replacement import (
    PriorityRow,
    ReplacementError,
    load_manifest,
    record_run,
    validate_run,
)

__all__ = [
    "PriorityRow",
    "ReplacementError",
    "load_manifest",
    "record_run",
    "validate_run",
]
