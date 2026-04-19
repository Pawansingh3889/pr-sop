# examples

Drop-in `.prsop.yml` files for common project shapes.

## `sql-guard.prsop.yml`

Config for scanning [sql-sop](https://github.com/Pawansingh3889/sql-guard) at
HEAD. `__init__.py` uses `importlib.metadata.version()` dynamically, so the
version-consistency check only has one literal source (`pyproject.toml`).

## `sql-guard-pre.prsop.yml`

Same project, but pinned to the pre-cleanup commit where `__init__.py` still
had a literal `__version__ = "0.4.0"` while `pyproject.toml` said `0.4.1`.
Used during pr-sop v0.1 validation to prove the `version-consistency` check
catches real drift.

Run from any repo:

```bash
pr-sop check --repo /path/to/sql-guard --config /path/to/examples/sql-guard.prsop.yml
```
