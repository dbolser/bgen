"""Tests for the packaging configuration itself.

These are cheap static checks of the wiring that the wheel build depends on.
The end-to-end proof is in test_wheel.py, which is slow and opt-in; these run
everywhere and catch the same regressions early.
"""

import importlib.util
import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib

import pytest
import setuptools
from setuptools.command.build_py import build_py

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope='module')
def pyproject():
    with open(ROOT / 'pyproject.toml', 'rb') as handle:
        return tomllib.load(handle)


@pytest.fixture
def setup_kwargs(monkeypatch):
    """Import setup.py with setuptools.setup stubbed, returning its arguments."""
    captured = {}
    monkeypatch.setattr(setuptools, 'setup', lambda **kwargs: captured.update(kwargs))
    spec = importlib.util.spec_from_file_location('bgen_setup', ROOT / 'setup.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return captured


def test_the_waf_build_hook_runs_during_a_wheel_build(setup_kwargs):
    """Regression: the hook was originally installed on build_ext.

    setuptools skips build_ext entirely for a distribution with no ext_modules,
    so the hook never ran and the wheel shipped without bgenix in it.
    """
    hook = setup_kwargs['cmdclass']['build_py']
    assert issubclass(hook, build_py)
    assert 'build_ext' not in setup_kwargs.get('cmdclass', {})


def test_the_distribution_is_platform_specific(setup_kwargs):
    """Regression: the wheel was tagged py3-none-any despite holding a binary."""
    assert setup_kwargs['distclass']().has_ext_modules() is True


def test_the_build_hook_copies_rather_than_moves_the_binary():
    """Regression: Path.rename() fails across filesystems and empties ./build."""
    source = (ROOT / 'setup.py').read_text()
    assert 'shutil.copy2' in source
    assert '.rename(' not in source


def test_package_version_matches_the_bgen_version(pyproject):
    """The PyPI version has to say which BGEN you are getting.

    A packaging-only re-release adds a PEP 440 '.postN' suffix, since upstream
    BGEN has not changed; the part in front of it must still be the upstream
    version.
    """
    wscript_version = re.search(
        r'^VERSION\s*=\s*"([^"]+)"', (ROOT / 'wscript').read_text(), re.MULTILINE
    )
    assert wscript_version, 'no VERSION found in wscript'

    expected = re.escape(wscript_version.group(1)) + r'(\.post\d+)?'
    version = pyproject['project']['version']
    assert re.fullmatch(expected, version), (
        '%s is neither BGEN %s nor a .postN repackaging of it'
        % (version, wscript_version.group(1))
    )


def test_the_console_script_points_at_the_launcher(pyproject):
    assert pyproject['project']['scripts'] == {'bgenix': 'bgenix.runner:run_bgenix'}


def test_the_binary_is_declared_as_package_data(pyproject):
    package_data = pyproject['tool']['setuptools']['package-data']
    assert 'bin/bgenix' in package_data['bgenix']


def test_declared_license_file_exists(pyproject):
    for name in pyproject['project']['license-files']:
        assert (ROOT / name).is_file()
