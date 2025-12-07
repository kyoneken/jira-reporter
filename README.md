# Jira Reporter

A CLI tool to fetch and report Jira work logs using OAuth authentication.

## Features

- **OAuth Authentication**: Securely connect to Jira using OAuth 1.0
- **Work Log Reporting**: Fetch work logs for specified users and date ranges
- **Daily Summary**: Aggregate work time by day with issue references
- **Multiple Users**: Generate reports for multiple users at once
- **Multiple Output Formats**: 
  - Table (default, human-readable)
  - CSV
  - TSV
  - JSON
  - YAML
- **Configuration Management**: Store credentials securely in user config directory (`~/.jira-reporter`)

## Requirements

- Python 3.12+
- uv (Python package manager)
- Jira instance with OAuth configured

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/kyoneken/jira-reporter.git
cd jira-reporter

# Install dependencies with uv
uv sync

# Run the tool
uv run jira-reporter --help
```

### Install as a Package

```bash
# Install in editable mode
uv pip install -e .

# Or install directly
uv pip install .
```

## Configuration

Before using Jira Reporter, you need to configure it with your Jira OAuth credentials.

### Setting up OAuth in Jira

1. Generate an RSA key pair for OAuth
2. Configure an Application Link in Jira with OAuth
3. Obtain OAuth access tokens

For detailed instructions, see [Jira OAuth documentation](https://developer.atlassian.com/server/jira/platform/oauth/).

### Configure the Tool

```bash
uv run jira-reporter configure \
  --jira-url "https://jira.example.com" \
  --consumer-key "your-consumer-key" \
  --key-cert "path/to/private_key.pem" \
  --access-token "your-access-token" \
  --access-token-secret "your-access-token-secret"
```

You can also provide the private key content directly instead of a file path.

### View Configuration

```bash
uv run jira-reporter show-config
```

Configuration is stored in `~/.jira-reporter/config.yaml`

## Usage

### Generate Report for Single User

```bash
uv run jira-reporter report \
  --username john.doe \
  --start-date 2024-01-01 \
  --end-date 2024-01-31
```

### Generate Report for Multiple Users

```bash
uv run jira-reporter report \
  --username john.doe \
  --username jane.smith \
  --start-date 2024-01-01 \
  --end-date 2024-01-31
```

### Specify Output Format

#### Table Format (Default)

```bash
uv run jira-reporter report \
  --username john.doe \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --format table
```

Output:
```
=== Work Log Report for john.doe ===

+------------+--------+----------------------+
| Date       | Hours  | Issues               |
+============+========+======================+
| 2024-01-01 | 8.00   | PROJ-123, PROJ-456   |
| 2024-01-02 | 6.50   | PROJ-789             |
| 2024-01-03 | 7.25   | PROJ-123, PROJ-890   |
|            |        |                      |
| Total      | 21.75  |                      |
+------------+--------+----------------------+
```

#### CSV Format

```bash
uv run jira-reporter report \
  --username john.doe \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --format csv > report.csv
```

#### JSON Format

```bash
uv run jira-reporter report \
  --username john.doe \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --format json > report.json
```

#### YAML Format

```bash
uv run jira-reporter report \
  --username john.doe \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --format yaml > report.yaml
```

#### TSV Format

```bash
uv run jira-reporter report \
  --username john.doe \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --format tsv > report.tsv
```

## Development

### Running Tests

```bash
uv run pytest tests/ -v
```

### Running Tests with Coverage

```bash
uv run pytest tests/ --cov=jira_reporter --cov-report=html
```

## Project Structure

```
jira-reporter/
├── src/
│   └── jira_reporter/
│       ├── __init__.py
│       ├── cli.py           # CLI interface
│       ├── config.py        # Configuration management
│       ├── jira_client.py   # Jira API client
│       └── formatters.py    # Output formatters
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   └── test_formatters.py
├── pyproject.toml
├── README.md
└── .gitignore
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.