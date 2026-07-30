"""Build hook that compiles ``bgenix`` with waf and vendors it into the wheel.

All static metadata lives in ``pyproject.toml``; this file exists only because
the package ships a binary produced by a build system setuptools knows nothing
about.

Two things are load-bearing here:

* the hook hangs off ``build_py``, not ``build_ext``.  ``build_ext`` is skipped
  entirely when a distribution declares no ``ext_modules``, so a hook installed
  there never runs and the wheel silently ships without the executable.
* ``BinaryDistribution`` forces a platform-specific wheel tag.  The wheel
  contains a compiled binary, so a ``py3-none-any`` tag would advertise it as
  installable on platforms where it cannot run.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.dist import Distribution

ROOT = Path(__file__).resolve().parent
WAF = ROOT / 'waf'
BUILT_BGENIX = ROOT / 'build' / 'apps' / 'bgenix'
VENDORED_BGENIX = ROOT / 'bgenix' / 'bin' / 'bgenix'


class BinaryDistribution(Distribution):
    """Marks the distribution as platform-specific (it ships a binary)."""

    def has_ext_modules(self):
        return True


class BuildWaf(build_py):
    """Compile bgenix with waf, then package it as bgenix/bin/bgenix."""

    def run(self):
        # waf's shebang is '/usr/bin/env python', which does not exist on
        # python3-only systems; invoke it with the interpreter we run under.
        subprocess.check_call([sys.executable, str(WAF), 'configure'], cwd=str(ROOT))
        subprocess.check_call([sys.executable, str(WAF)], cwd=str(ROOT))
        if not BUILT_BGENIX.exists():
            raise RuntimeError(
                'waf reported success but %s was not produced' % BUILT_BGENIX
            )
        VENDORED_BGENIX.parent.mkdir(parents=True, exist_ok=True)
        # copy, not rename: the build tree may live on another filesystem, and
        # moving the binary out of it breaks incremental rebuilds and the
        # functional tests, which run ./build/apps/bgenix in place.
        shutil.copy2(str(BUILT_BGENIX), str(VENDORED_BGENIX))
        VENDORED_BGENIX.chmod(0o755)
        super().run()


setup(
    distclass=BinaryDistribution,
    cmdclass={'build_py': BuildWaf},
)
