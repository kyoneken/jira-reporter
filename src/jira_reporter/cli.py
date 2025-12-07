"""Command-line interface for Jira Reporter."""

import click
from datetime import datetime
from typing import List
from .config import Config
from .jira_client import JiraClient
from .formatters import get_formatter
from .oauth_flow import JiraOAuthFlow


@click.group()
@click.version_option()
def main():
    """Jira Reporter - Fetch and report Jira work logs with OAuth authentication."""
    pass


@main.command()
@click.option('--jira-url', required=True, help='Jira base URL (e.g., https://jira.example.com)')
@click.option('--consumer-key', required=True, help='OAuth consumer key')
@click.option('--private-key', required=True, help='Path to RSA private key file (PEM format)')
@click.option('--no-browser', is_flag=True, help='Do not automatically open browser')
def login(jira_url, consumer_key, private_key, no_browser):
    """Authenticate with Jira using OAuth (interactive web-based flow)."""
    try:
        # Initialize OAuth flow
        oauth_flow = JiraOAuthFlow(jira_url, consumer_key, private_key)
        
        # Perform OAuth dance
        access_token, access_token_secret = oauth_flow.perform_oauth_dance(
            auto_open_browser=not no_browser
        )
        
        # Load private key for storage
        from pathlib import Path
        key_path = Path(private_key)
        if key_path.exists():
            with open(key_path, 'r') as f:
                key_cert = f.read()
        else:
            key_cert = private_key
        
        # Save configuration
        config = Config()
        config.set_jira_url(jira_url)
        config.set_oauth_config(consumer_key, key_cert, access_token, access_token_secret)
        config.save()
        
        click.echo("✓ Authentication successful!")
        click.echo(f"✓ Configuration saved to: {Config.CONFIG_FILE}")
        click.echo("\nYou can now use 'jira-reporter report' to fetch work logs.")
        
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        return
    except Exception as e:
        click.echo(f"Unexpected error during authentication: {e}", err=True)
        return


@main.command()
@click.option('--jira-url', required=True, help='Jira base URL (e.g., https://jira.example.com)')
@click.option('--consumer-key', required=True, help='OAuth consumer key')
@click.option('--key-cert', required=True, help='OAuth key certificate (private key content or path to file)')
@click.option('--access-token', required=True, help='OAuth access token')
@click.option('--access-token-secret', required=True, help='OAuth access token secret')
def configure(jira_url, consumer_key, key_cert, access_token, access_token_secret):
    """Configure Jira Reporter with OAuth credentials (manual configuration)."""
    config = Config()
    
    # Check if key_cert is a file path
    try:
        from pathlib import Path
        key_path = Path(key_cert)
        if key_path.exists():
            with open(key_path, 'r') as f:
                key_cert = f.read()
    except (OSError, IOError, UnicodeDecodeError) as e:
        # If file reading fails, assume it's the actual certificate content
        pass
    
    config.set_jira_url(jira_url)
    config.set_oauth_config(consumer_key, key_cert, access_token, access_token_secret)
    config.save()
    
    click.echo("Configuration saved successfully!")
    click.echo(f"Configuration file: {Config.CONFIG_FILE}")


@main.command()
@click.option('-u', '--username', 'usernames', multiple=True, required=True, help='Jira username(s) to fetch work logs for')
@click.option('-s', '--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('-e', '--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('-f', '--format', 'output_format', 
              type=click.Choice(['table', 'csv', 'json', 'yaml', 'tsv'], case_sensitive=False),
              default='table',
              help='Output format (default: table)')
def report(usernames: List[str], start_date: str, end_date: str, output_format: str):
    """Generate work log report for specified user(s) and date range."""
    # Parse dates
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        click.echo(f"Error: Invalid date format. Please use YYYY-MM-DD. {e}", err=True)
        return
    
    if start > end:
        click.echo("Error: Start date must be before or equal to end date.", err=True)
        return
    
    # Load configuration and initialize client
    try:
        config = Config()
        client = JiraClient(config)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("\nPlease run 'jira-reporter login' to authenticate with Jira.")
        return
    except Exception as e:
        click.echo(f"Error initializing Jira client: {e}", err=True)
        return
    
    # Get formatter
    try:
        formatter = get_formatter(output_format)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        return
    
    # Fetch and format work logs for each user
    for username in usernames:
        try:
            click.echo(f"Fetching work logs for {username}...", err=True)
            worklogs = client.get_user_worklogs(username, start, end)
            aggregated = client.aggregate_worklogs_by_day(worklogs)
            
            # Format and output
            output = formatter.format(username, aggregated)
            click.echo(output)
            
        except ValueError as e:
            click.echo(f"Error fetching work logs for {username}: {e}", err=True)
        except Exception as e:
            click.echo(f"Unexpected error for {username}: {e}", err=True)


@main.command()
def show_config():
    """Show current configuration."""
    config = Config()
    
    click.echo(f"Configuration file: {Config.CONFIG_FILE}")
    click.echo(f"Jira URL: {config.get_jira_url() or 'Not configured'}")
    
    oauth = config.get_oauth_config()
    if oauth:
        click.echo("OAuth configured: Yes")
        click.echo(f"  Consumer key: {oauth.get('consumer_key', 'Not set')}")
        click.echo("  Access token: ***")
        click.echo("  Access token secret: ***")
    else:
        click.echo("OAuth configured: No")


if __name__ == '__main__':
    main()
