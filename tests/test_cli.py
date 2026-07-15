"""
Test command line usage
"""
import shlex
from re import fullmatch
from typing import List, Tuple
from unittest import mock

import pytest

from dtbsync import __version__, cli


def run(capsys, args: str, prog: str = "prog") -> Tuple[int, List[str], List[str]]:
    """
    Simulate a call to the command line tool by mocking arguments
    """
    with pytest.raises(SystemExit) as error:
        with mock.patch("sys.argv", [prog] + shlex.split(args)):
            cli.run()
    captured = capsys.readouterr()
    return (
        error.value.code,
        captured.out.splitlines(),
        captured.err.splitlines(),
    )


def test_help(capsys):
    """
    Check --help output
    """
    rc, stdout, stderr = run(capsys, "--help")
    assert rc == 0
    assert len(stdout) > 0
    assert len(stderr) == 0


def test_version(capsys):
    """
    Check --version output
    """
    rc, stdout, stderr = run(capsys, "--version")
    assert rc == 0
    assert len(stdout) > 0
    assert __version__ in stdout[0]
    assert len(stderr) == 0


@mock.patch("dtbsync.cli.sys.stdin")
def test_get_kernel_version_from_dtb_path(mock_stdin):
    """Extract the kernel version directory from an installed DTB path."""
    mock_stdin.isatty.return_value = False
    mock_stdin.__iter__.return_value = iter(
        [
            "usr/lib/modules/7.1.3-arch1-3/dtb/qcom/"
            "sc8280xp-lenovo-thinkpad-x13s.dtb\n"
        ]
    )

    assert cli.get_kernel_version() == "7.1.3-arch1-3"


@mock.patch("dtbsync.cli.sys.stdin")
def test_get_kernel_version_does_not_block_on_terminal(mock_stdin):
    """Interactive use fails instead of waiting indefinitely for input."""
    mock_stdin.isatty.return_value = True

    with pytest.raises(RuntimeError, match="No package paths on stdin"):
        cli.get_kernel_version()


def test_hello(capsys):
    """
    Check usage with 2 arguments
    """
    rc, stdout, stderr = run(capsys, "foo bar")
    assert rc == 0
    assert len(stdout) == 2
    assert fullmatch(r"Hello .*foo.*", stdout[0])
    assert fullmatch(r"Hello .*bar.*", stdout[1])
    assert len(stderr) == 0
