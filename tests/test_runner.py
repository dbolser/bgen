"""Unit tests for the console-script launcher."""

import os
import sys

import pytest

from bgenix import runner


@pytest.fixture
def bin_dir(tmp_path, monkeypatch):
    """Point the launcher at an empty scratch 'bin' directory."""
    monkeypatch.setattr(runner, 'BIN_DIR', tmp_path)
    return tmp_path


def test_bgenix_path_returns_bundled_executable(bin_dir):
    exe = bin_dir / 'bgenix'
    exe.touch()
    assert runner.bgenix_path() == exe


def test_bgenix_path_reports_a_missing_executable(bin_dir):
    """The failure mode of the first packaging attempt: no binary in the wheel.

    That shipped as a bare 'FileNotFoundError: [Errno 2]' from os.execv, which
    says nothing about what went wrong.
    """
    with pytest.raises(FileNotFoundError) as excinfo:
        runner.bgenix_path()
    message = str(excinfo.value)
    assert str(bin_dir / 'bgenix') in message
    assert 'bgenix' in message and 'missing' in message


def test_run_bgenix_execs_the_executable_with_forwarded_arguments(bin_dir, monkeypatch):
    exe = bin_dir / 'bgenix'
    exe.touch()
    calls = []
    monkeypatch.setattr(os, 'execv', lambda path, argv: calls.append((path, argv)))
    monkeypatch.setattr(sys, 'argv', ['bgenix', '-g', 'x.bgen', '-list'])

    runner.run_bgenix()

    assert calls == [(str(exe), ['bgenix', '-g', 'x.bgen', '-list'])]


def test_run_bgenix_does_not_exec_when_the_executable_is_missing(bin_dir, monkeypatch):
    monkeypatch.setattr(os, 'execv', lambda path, argv: pytest.fail('execv called'))
    with pytest.raises(FileNotFoundError):
        runner.run_bgenix()
