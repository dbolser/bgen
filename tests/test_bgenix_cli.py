"""Functional smoke tests for bgenix against the example data.

These exercise the binary the wheel ships, using the index committed alongside
example/example.16bits.bgen.  They are deliberately shallow: the format itself
is covered by the C++ unit tests under test/unit.
"""

import shutil

from conftest import parse_variant_table, run_bgenix

EXAMPLE_VARIANT_COUNT = 199


def test_list_reports_every_variant(built_bgenix, example_dir):
    result = run_bgenix(built_bgenix, '-g', example_dir / 'example.16bits.bgen', '-list')
    header, rows = parse_variant_table(result.stdout)

    assert header[:4] == ['alternate_ids', 'rsid', 'chromosome', 'position']
    assert len(rows) == EXAMPLE_VARIANT_COUNT
    assert result.stdout.rstrip().endswith(
        '# bgenix: success, total %d variants.' % EXAMPLE_VARIANT_COUNT
    )


def test_variants_can_be_selected_by_rsid(built_bgenix, example_dir):
    result = run_bgenix(
        built_bgenix,
        '-g', example_dir / 'example.16bits.bgen',
        '-list',
        '-incl-rsids', 'RSID_101',
    )
    _, rows = parse_variant_table(result.stdout)

    assert len(rows) == 1
    assert rows[0]['rsid'] == 'RSID_101'
    assert rows[0]['position'] == '1001'
    assert (rows[0]['first_allele'], rows[0]['alternative_alleles']) == ('A', 'G')


def test_variants_can_be_selected_by_range(built_bgenix, example_dir):
    result = run_bgenix(
        built_bgenix,
        '-g', example_dir / 'example.16bits.bgen',
        '-list',
        '-incl-range', '01:2000-3000',
    )
    _, rows = parse_variant_table(result.stdout)

    positions = sorted(int(row['position']) for row in rows)
    assert positions and all(2000 <= p <= 3000 for p in positions)


def test_an_index_can_be_built_and_then_queried(built_bgenix, example_dir, tmp_path):
    """The full bgenix workflow: index a bgen file, then read it back."""
    bgen = tmp_path / 'example.bgen'
    shutil.copy(example_dir / 'example.16bits.bgen', bgen)

    run_bgenix(built_bgenix, '-g', bgen, '-index')
    index = bgen.with_suffix('.bgen.bgi')
    assert index.is_file() and index.stat().st_size > 0

    result = run_bgenix(built_bgenix, '-g', bgen, '-list')
    _, rows = parse_variant_table(result.stdout)
    assert len(rows) == EXAMPLE_VARIANT_COUNT


def test_a_missing_bgen_file_is_an_error(built_bgenix, tmp_path):
    import subprocess

    result = subprocess.run(
        [str(built_bgenix), '-g', str(tmp_path / 'nope.bgen'), '-list'],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
