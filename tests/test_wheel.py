"""End-to-end test of the wheel: build it, install it, run the console script.

This is the regression test for the packaging bug that shipped bgenix 1.1.7 as
a 'py3-none-any' wheel containing no bgenix at all, so that the installed
'bgenix' command died with 'FileNotFoundError: [Errno 2]'.

Compiling the C++ tree takes about half a minute, so this module is marked slow
and skipped by default: run 'pytest -m slow' to include it.
"""

import stat
import subprocess
import sys
import zipfile

import pytest

from conftest import parse_variant_table, venv_with

pytestmark = pytest.mark.slow


@pytest.fixture(scope='module')
def wheel(pristine_source):
    """Build a wheel from a pristine copy of the working tree."""
    subprocess.run(
        [sys.executable, '-m', 'build', '--wheel'],
        cwd=str(pristine_source),
        check=True,
    )

    wheels = list((pristine_source / 'dist').glob('*.whl'))
    assert len(wheels) == 1, 'expected exactly one wheel, got %s' % wheels
    # The build must not consume the binary it packages: the functional tests
    # run ./build/apps/bgenix in place, and Path.rename() across filesystems
    # would fail outright.
    assert (pristine_source / 'build' / 'apps' / 'bgenix').exists()
    return wheels[0]


def test_the_wheel_contains_the_bgenix_executable(wheel):
    with zipfile.ZipFile(wheel) as archive:
        entry = archive.getinfo('bgenix/bin/bgenix')
        assert entry.file_size > 0
        mode = entry.external_attr >> 16
        assert mode & stat.S_IXUSR, 'bgenix is not executable inside the wheel'


def test_the_wheel_is_tagged_for_this_platform(wheel, package_version):
    assert 'py3-none-any' not in wheel.name, (
        'a wheel containing a compiled binary must not claim to be universal'
    )
    with zipfile.ZipFile(wheel) as archive:
        metadata = archive.read('bgenix-%s.dist-info/WHEEL' % package_version).decode()
    assert 'Root-Is-Purelib: false' in metadata


def test_the_installed_console_script_queries_a_bgen_file(wheel, tmp_path, example_dir):
    """Install the wheel into a throwaway environment and use it for real."""
    venv = venv_with(wheel, tmp_path / 'venv')

    result = subprocess.run(
        [
            str(venv / 'bin' / 'bgenix'),
            '-g', str(example_dir / 'example.16bits.bgen'),
            '-list',
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    _, rows = parse_variant_table(result.stdout)
    assert len(rows) == 199
