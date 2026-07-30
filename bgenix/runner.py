"""Launcher for the ``bgenix`` executable bundled inside this package."""

import os
import sys
from pathlib import Path

BIN_DIR = Path(__file__).resolve().parent / 'bin'


def bgenix_path():
    """Return the absolute path to the bundled ``bgenix`` executable.

    Raises ``FileNotFoundError`` if the executable is missing, which means the
    installed wheel was built without compiling bgenix.
    """
    exe = BIN_DIR / 'bgenix'
    if not exe.exists():
        raise FileNotFoundError(
            "the bgenix executable bundled with bgenix is missing (looked in"
            " %s). This install came from a wheel built without compiling"
            " bgenix; reinstall from source with"
            " 'pip install --no-binary bgenix bgenix'." % exe
        )
    return exe


def run_bgenix():
    """Console-script entry point: replace this process with ``bgenix``."""
    os.execv(str(bgenix_path()), ['bgenix', *sys.argv[1:]])
