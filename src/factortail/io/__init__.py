"""I/O contracts for FactorTail outputs.

* :mod:`factortail.io.schema` defines the authoritative output schema
  (mirrors ``results/SCHEMA.md``).
* :mod:`factortail.io.writers` writes validated CSVs with provenance.
* :mod:`factortail.io.validators` enforces the SCHEMA at write- and
  read-time, used by the CLI and the replacement-rule manifest.
"""

from factortail.io.schema import SCHEMA, RequiredColumns, get_schema
from factortail.io.validators import ValidationError, validate_csv, validate_dataframe
from factortail.io.writers import write_csv

__all__ = [
    "SCHEMA",
    "RequiredColumns",
    "ValidationError",
    "get_schema",
    "validate_csv",
    "validate_dataframe",
    "write_csv",
]
