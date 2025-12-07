"""Tests for formatters."""

import pytest
from datetime import datetime
from jira_reporter.formatters import (
    get_formatter,
    TableFormatter,
    CSVFormatter,
    TSVFormatter,
    JSONFormatter,
    YAMLFormatter
)


@pytest.fixture
def sample_data():
    """Sample aggregated work log data."""
    return {
        "2024-01-01": {
            "date": datetime(2024, 1, 1),
            "total_seconds": 28800,
            "total_hours": 8.0,
            "issues": ["PROJ-123", "PROJ-456"]
        },
        "2024-01-02": {
            "date": datetime(2024, 1, 2),
            "total_seconds": 14400,
            "total_hours": 4.0,
            "issues": ["PROJ-789"]
        }
    }


def test_get_formatter_table():
    """Test getting table formatter."""
    formatter = get_formatter("table")
    assert isinstance(formatter, TableFormatter)


def test_get_formatter_csv():
    """Test getting CSV formatter."""
    formatter = get_formatter("csv")
    assert isinstance(formatter, CSVFormatter)


def test_get_formatter_tsv():
    """Test getting TSV formatter."""
    formatter = get_formatter("tsv")
    assert isinstance(formatter, TSVFormatter)


def test_get_formatter_json():
    """Test getting JSON formatter."""
    formatter = get_formatter("json")
    assert isinstance(formatter, JSONFormatter)


def test_get_formatter_yaml():
    """Test getting YAML formatter."""
    formatter = get_formatter("yaml")
    assert isinstance(formatter, YAMLFormatter)


def test_get_formatter_invalid():
    """Test getting invalid formatter raises error."""
    with pytest.raises(ValueError):
        get_formatter("invalid")


def test_table_formatter(sample_data):
    """Test table formatter output."""
    formatter = TableFormatter()
    output = formatter.format("testuser", sample_data)
    
    assert "testuser" in output
    assert "2024-01-01" in output
    assert "2024-01-02" in output
    assert "8.00" in output
    assert "4.00" in output
    assert "12.00" in output  # Total


def test_table_formatter_empty():
    """Test table formatter with empty data."""
    formatter = TableFormatter()
    output = formatter.format("testuser", {})
    assert "No work logs found" in output


def test_csv_formatter(sample_data):
    """Test CSV formatter output."""
    formatter = CSVFormatter()
    output = formatter.format("testuser", sample_data)
    
    assert "Username,Date,Hours,Issues" in output
    assert "testuser,2024-01-01,8.00" in output
    assert "testuser,2024-01-02,4.00" in output
    assert "testuser,Total,12.00" in output


def test_tsv_formatter(sample_data):
    """Test TSV formatter output."""
    formatter = TSVFormatter()
    output = formatter.format("testuser", sample_data)
    
    assert "Username\tDate\tHours\tIssues" in output
    assert "testuser\t2024-01-01\t8.00" in output
    assert "testuser\t2024-01-02\t4.00" in output


def test_json_formatter(sample_data):
    """Test JSON formatter output."""
    import json
    
    formatter = JSONFormatter()
    output = formatter.format("testuser", sample_data)
    
    data = json.loads(output)
    assert data["username"] == "testuser"
    assert data["total_hours"] == 12.0
    assert len(data["work_logs"]) == 2


def test_yaml_formatter(sample_data):
    """Test YAML formatter output."""
    import yaml
    
    formatter = YAMLFormatter()
    output = formatter.format("testuser", sample_data)
    
    data = yaml.safe_load(output)
    assert data["username"] == "testuser"
    assert data["total_hours"] == 12.0
    assert len(data["work_logs"]) == 2
