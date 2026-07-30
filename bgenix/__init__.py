"""The bgenix BGEN indexing tool, installable with pip.

This package is a packaging shim, not a BGEN library: it compiles the upstream
``bgenix`` tool from the BGEN C++ sources at install time and exposes it as a
console script.  For reading BGEN data in Python, use one of the existing
libraries (``bgen``, ``bgen-reader``, ``cbgen``, ``pybgen``) instead.
"""

from importlib.metadata import PackageNotFoundError, version

from bgenix.runner import bgenix_path, run_bgenix

try:
    __version__ = version('bgenix')
except PackageNotFoundError:  # running from a source tree, not installed
    __version__ = 'unknown'

__all__ = ['bgenix_path', 'run_bgenix', '__version__']
