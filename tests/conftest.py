"""Shared fixtures for the bgenix Python-layer tests."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib

ROOT = Path(__file__).resolve().parent.parent

# Skipped when copying the repo into a scratch tree to build from: outputs
# ('build', 'dist', the vendored binary), caches, and waf's lock file, which
# records absolute paths from the original directory.
BUILD_TREE_IGNORE = shutil.ignore_patterns(
    '.git', '.venv', 'build', 'dist', '*.egg-info', '__pycache__',
    '.pytest_cache', '.lock-waf*', '.waf3-*', '.waf-*',
)


@pytest.fixture(scope='session')
def repo_root():
    return ROOT


@pytest.fixture(scope='session')
def example_dir():
    """The example BGEN data shipped with the repository."""
    return ROOT / 'example'


@pytest.fixture(scope='session')
def package_version():
    """The declared version, which names the built wheel and sdist."""
    with open(ROOT / 'pyproject.toml', 'rb') as handle:
        return tomllib.load(handle)['project']['version']


@pytest.fixture(scope='session')
def built_bgenix():
    """The bgenix built by waf into ./build, skipping if it is not there."""
    exe = ROOT / 'build' / 'apps' / 'bgenix'
    if not exe.exists():
        pytest.skip("bgenix is not built; run './waf configure && ./waf' first")
    return exe


@pytest.fixture(scope='module')
def pristine_source(tmp_path_factory):
    """A scratch copy of the working tree with every build output removed.

    Distribution tests build here rather than in the repository so that they
    exercise a from-scratch build and leave the developer's tree alone.
    """
    source = tmp_path_factory.mktemp('source') / 'bgen'
    shutil.copytree(ROOT, source, ignore=BUILD_TREE_IGNORE)
    # A bgenix left over from an earlier build would otherwise be packaged
    # even if the waf step did nothing at all.
    shutil.rmtree(source / 'bgenix' / 'bin', ignore_errors=True)
    return source


def venv_with(distribution, venv_dir, isolated=True):
    """Create a virtualenv at ``venv_dir`` with ``distribution`` installed.

    ``isolated=False`` allows pip to reach the network, which an sdist install
    needs in order to fetch its build backend.
    """
    subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], check=True)
    command = [str(venv_dir / 'bin' / 'pip'), 'install', str(distribution)]
    if isolated:
        command.insert(-1, '--no-index')
    subprocess.run(command, check=True)
    return venv_dir


def run_bgenix(exe, *args, cwd=None):
    """Run bgenix and return the CompletedProcess, asserting it succeeded."""
    result = subprocess.run(
        [str(exe)] + [str(a) for a in args],
        cwd=None if cwd is None else str(cwd),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        'bgenix %s failed (%d):\n%s' % (args, result.returncode, result.stderr)
    )
    return result


def parse_variant_table(stdout):
    """Extract the variant rows from a 'bgenix -list' run.

    bgenix wraps its table in a banner, progress output and '#'-prefixed
    status lines; the table starts at the 'alternate_ids' header.
    """
    lines = stdout.splitlines()
    for index, line in enumerate(lines):
        if line.startswith('alternate_ids\t'):
            header = line.split('\t')
            rows = [
                dict(zip(header, row.split('\t')))
                for row in lines[index + 1:]
                if row and not row.startswith('#')
            ]
            return header, rows
    raise AssertionError('no variant table found in bgenix output:\n%s' % stdout)
