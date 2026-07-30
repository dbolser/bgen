"""End-to-end test of the sdist, i.e. of 'pip install bgenix' from source.

The sdist has to carry the whole C++ tree, because installing it compiles
bgenix.  Setuptools ships only the Python modules unless told otherwise, so
without MANIFEST.in the install fails on a missing './waf'.

Slow (a full compile) and needs network access for pip's build isolation to
fetch the build backend; run with 'pytest -m slow'.
"""

import subprocess
import sys
import tarfile

import pytest

from conftest import parse_variant_table, venv_with

pytestmark = pytest.mark.slow

# What waf needs to get from an unpacked sdist to a working bgenix.
REQUIRED_MEMBERS = [
    'waf',
    'wscript',
    'src/bgen.cpp',
    'apps/bgenix.cpp',
    'apps/wscript',
    '3rd_party/wscript',
    'genfile/include/genfile/bgen/bgen.hpp',
]


@pytest.fixture(scope='module')
def sdist(pristine_source):
    subprocess.run(
        [sys.executable, '-m', 'build', '--sdist'],
        cwd=str(pristine_source),
        check=True,
    )
    archives = list((pristine_source / 'dist').glob('*.tar.gz'))
    assert len(archives) == 1, 'expected exactly one sdist, got %s' % archives
    return archives[0]


@pytest.fixture(scope='module')
def sdist_members(sdist, package_version):
    with tarfile.open(sdist) as archive:
        prefix = 'bgenix-%s/' % package_version
        return {
            name[len(prefix):]
            for name in archive.getnames()
            if name.startswith(prefix)
        }


@pytest.mark.parametrize('member', REQUIRED_MEMBERS)
def test_the_sdist_carries_the_sources_needed_to_build(member, sdist_members):
    assert member in sdist_members


def test_the_sdist_leaves_out_the_example_data(sdist_members):
    """The .bgen example files are 15M and are not needed to compile."""
    assert 'example/bgen_to_vcf.cpp' in sdist_members
    assert not [name for name in sdist_members if name.endswith('.bgen')]


def test_installing_the_sdist_compiles_a_working_bgenix(sdist, tmp_path, example_dir):
    venv = venv_with(sdist, tmp_path / 'venv', isolated=False)

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
