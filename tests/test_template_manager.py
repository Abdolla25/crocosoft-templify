from unittest.mock import mock_open, patch

import pytest

from template_updater import Config, TemplateManager


@pytest.fixture
def config():
    return Config(
        base_path="/test/path",
        templify_repo_name="templify",
        email_users_repo_name="EmailUsersPackageBuilder",
        templify_repo_path="/test/path/templify",
        templates_repo_path="/test/path/EmailUsersPackageBuilder",
    )


@pytest.fixture
def template_manager(config):
    return TemplateManager(config)


def test_validate_html_content_valid(template_manager):
    """Test HTML content validation with valid input."""
    valid_content = "SET @html_content := 'some html';"
    template_manager.validate_html_content(valid_content)  # Should not raise


def test_validate_html_content_invalid(template_manager):
    """Test HTML content validation with invalid input."""
    invalid_content = "INVALID @html_content"
    with pytest.raises(ValueError):
        template_manager.validate_html_content(invalid_content)


def test_update_template(template_manager):
    """Test template update functionality."""
    template_content = "old content\nSET @html_content := 'old';\nmore content"
    new_html = "SET @html_content := 'new';"
    expected = "old content\nSET @html_content := 'new';\nmore content"

    mock_file = mock_open(read_data=template_content)
    with patch("builtins.open", mock_file):
        with patch("os.replace"):
            template_manager.update_template("test.sql", new_html)

    mock_file().write.assert_called_once_with(expected)
