"""pr-sop — opinionated PR governance checks."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pr-sop")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0+unknown"
