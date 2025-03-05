from unittest.mock import Mock, patch

import pytest

from template_updater import GitOperations


@pytest.fixture
def git_ops():
    return GitOperations("/test/repo/path")


def test_get_current_branch(git_ops):
    """Test getting current branch name."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "main\n"
        branch = git_ops.get_current_branch()
        assert branch == "main"


def test_run_command_success(git_ops):
    """Test successful command execution."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(stdout="success", stderr="")
        result = git_ops.run_command(["git", "status"])
        assert result.stdout == "success"


def test_run_command_failure(git_ops):
    """Test failed command execution."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = Exception("Command failed")
        with pytest.raises(Exception):
            git_ops.run_command(["git", "invalid"])
