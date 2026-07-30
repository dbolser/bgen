"""Tests for the upstream version watcher.

No network: the fetch is stubbed.  What is worth testing here is that the
script notices drift and, just as importantly, that it treats a Fossil error
page as a failure rather than silently reporting 'in step' forever.
"""

import urllib.error

import pytest

from scripts import check_upstream_version as checker

WSCRIPT = 'import platform, os.path\n\nsrcdir="."\nAPPNAME = "bgen"\nVERSION = "%s"\n'


@pytest.fixture
def local_version(monkeypatch, tmp_path):
    """Pin the local version the script reads, independent of the real tree."""
    def _set(version):
        wscript = tmp_path / 'wscript'
        wscript.write_text(WSCRIPT % version)
        monkeypatch.setattr(checker, 'LOCAL_WSCRIPT', wscript)
        return version
    return _set


@pytest.fixture
def upstream(monkeypatch):
    """Stub the upstream fetch with a version, or an exception to raise."""
    def _set(outcome):
        def fake_fetch(url=None, timeout=None):
            if isinstance(outcome, Exception):
                raise outcome
            return outcome
        monkeypatch.setattr(checker, 'fetch_upstream_version', fake_fetch)
    return _set


def test_parse_version_reads_the_waf_version():
    assert checker.parse_version(WSCRIPT % '1.1.7') == '1.1.7'


def test_parse_version_rejects_a_wscript_without_one():
    with pytest.raises(ValueError):
        checker.parse_version('APPNAME = "bgen"\n')


def test_in_step_with_upstream(local_version, upstream, capsys):
    local_version('1.1.7')
    upstream('1.1.7')

    assert checker.main([]) == checker.EXIT_IN_STEP
    assert '1.1.7' in capsys.readouterr().out


def test_upstream_has_moved_on(local_version, upstream, capsys):
    local_version('1.1.7')
    upstream('1.2.0')

    assert checker.main([]) == checker.EXIT_MOVED
    out = capsys.readouterr().out
    assert '1.2.0' in out and '1.1.7' in out


def test_an_unreachable_upstream_is_distinct_from_drift(local_version, upstream):
    local_version('1.1.7')
    upstream(urllib.error.URLError('connection refused'))

    assert checker.main([]) == checker.EXIT_UNREACHABLE


def test_an_html_error_page_is_not_mistaken_for_a_wscript(monkeypatch):
    """Fossil serves HTML for its error pages and for documents it recognises.

    Without this guard the regex simply finds no VERSION and the script would
    keep reporting nothing to see, long after the endpoint stopped working.
    """
    class FakeResponse:
        def read(self):
            return b'<!DOCTYPE html>\n<html><title>500</title></html>'

        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            return False

    monkeypatch.setattr(
        checker.urllib.request, 'urlopen', lambda *args, **kwargs: FakeResponse()
    )

    with pytest.raises(ValueError):
        checker.fetch_upstream_version('https://example.invalid')


def test_github_output_is_written_when_present(local_version, upstream, tmp_path,
                                               monkeypatch):
    local_version('1.1.7')
    upstream('1.2.0')
    output = tmp_path / 'github_output'
    monkeypatch.setenv('GITHUB_OUTPUT', str(output))

    checker.main([])

    written = dict(line.split('=', 1) for line in output.read_text().splitlines())
    assert written == {'status': 'moved', 'local': '1.1.7', 'upstream': '1.2.0'}
