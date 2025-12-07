"""Tests for CLI commands."""

import pytest
from click.testing import CliRunner
from jira_reporter.cli import main
import tempfile
import shutil
from pathlib import Path
from jira_reporter.config import Config


@pytest.fixture
def temp_config_dir(monkeypatch):
    """Create a temporary config directory for tests."""
    temp_dir = Path(tempfile.mkdtemp())
    monkeypatch.setattr(Config, 'CONFIG_DIR', temp_dir)
    monkeypatch.setattr(Config, 'CONFIG_FILE', temp_dir / "config.yaml")
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'Jira Reporter' in result.output


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert '0.1.0' in result.output


def test_configure_command_help():
    """Test configure command help."""
    runner = CliRunner()
    result = runner.invoke(main, ['configure', '--help'])
    assert result.exit_code == 0
    assert 'OAuth' in result.output


def test_configure_command(temp_config_dir):
    """Test configure command."""
    runner = CliRunner()
    result = runner.invoke(main, [
        'configure',
        '--jira-url', 'https://jira.example.com',
        '--consumer-key', 'test-key',
        '--key-cert', 'test-cert',
        '--access-token', 'test-token',
        '--access-token-secret', 'test-secret'
    ])
    assert result.exit_code == 0
    assert 'Configuration saved successfully' in result.output
    
    # Verify config was saved
    config = Config()
    assert config.get_jira_url() == 'https://jira.example.com'
    oauth = config.get_oauth_config()
    assert oauth['consumer_key'] == 'test-key'


def test_show_config_not_configured(temp_config_dir):
    """Test show-config when not configured."""
    runner = CliRunner()
    result = runner.invoke(main, ['show-config'])
    assert result.exit_code == 0
    assert 'Not configured' in result.output


def test_show_config_configured(temp_config_dir):
    """Test show-config when configured."""
    # First configure
    runner = CliRunner()
    runner.invoke(main, [
        'configure',
        '--jira-url', 'https://jira.example.com',
        '--consumer-key', 'test-key',
        '--key-cert', 'test-cert',
        '--access-token', 'test-token',
        '--access-token-secret', 'test-secret'
    ])
    
    # Then show config
    result = runner.invoke(main, ['show-config'])
    assert result.exit_code == 0
    assert 'https://jira.example.com' in result.output
    assert 'OAuth configured: Yes' in result.output


def test_report_command_help():
    """Test report command help."""
    runner = CliRunner()
    result = runner.invoke(main, ['report', '--help'])
    assert result.exit_code == 0
    assert 'username' in result.output
    assert 'start-date' in result.output
    assert 'end-date' in result.output
    assert 'format' in result.output


def test_report_command_no_config(temp_config_dir):
    """Test report command without configuration."""
    runner = CliRunner()
    result = runner.invoke(main, [
        'report',
        '--username', 'testuser',
        '--start-date', '2024-01-01',
        '--end-date', '2024-01-31'
    ])
    assert result.exit_code == 0
    assert 'configure' in result.output.lower()


def test_report_command_invalid_dates(temp_config_dir):
    """Test report command with invalid dates."""
    # Configure first
    runner = CliRunner()
    runner.invoke(main, [
        'configure',
        '--jira-url', 'https://jira.example.com',
        '--consumer-key', 'test-key',
        '--key-cert', 'test-cert',
        '--access-token', 'test-token',
        '--access-token-secret', 'test-secret'
    ])
    
    # Test with invalid date format
    result = runner.invoke(main, [
        'report',
        '--username', 'testuser',
        '--start-date', 'invalid-date',
        '--end-date', '2024-01-31'
    ])
    assert result.exit_code == 0
    assert 'Error' in result.output
    
    # Test with end date before start date
    result = runner.invoke(main, [
        'report',
        '--username', 'testuser',
        '--start-date', '2024-01-31',
        '--end-date', '2024-01-01'
    ])
    assert result.exit_code == 0
    assert 'Error' in result.output
