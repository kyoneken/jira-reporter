"""Output formatters for work log data."""

import json
import csv
import yaml
from io import StringIO
from typing import Dict, Any, List
from tabulate import tabulate


class Formatter:
    """Base class for output formatters."""
    
    def format(self, username: str, data: Dict[str, Dict[str, Any]]) -> str:
        """Format work log data.
        
        Args:
            username: Username for the report
            data: Aggregated work log data
            
        Returns:
            Formatted string
        """
        raise NotImplementedError


class TableFormatter(Formatter):
    """Format work logs as a human-readable table."""
    
    def format(self, username: str, data: Dict[str, Dict[str, Any]]) -> str:
        """Format work log data as a table."""
        if not data:
            return f"No work logs found for user: {username}\n"
        
        # Prepare table data
        headers = ["Date", "Hours", "Issues"]
        rows = []
        total_hours = 0
        
        # Sort by date
        for date_str in sorted(data.keys()):
            entry = data[date_str]
            hours = entry['total_hours']
            issues = ", ".join(entry['issues'])
            rows.append([date_str, f"{hours:.2f}", issues])
            total_hours += hours
        
        # Add total row
        rows.append(["", "", ""])
        rows.append(["Total", f"{total_hours:.2f}", ""])
        
        # Format table
        table = tabulate(rows, headers=headers, tablefmt="grid")
        
        return f"\n=== Work Log Report for {username} ===\n\n{table}\n"


class CSVFormatter(Formatter):
    """Format work logs as CSV."""
    
    def format(self, username: str, data: Dict[str, Dict[str, Any]]) -> str:
        """Format work log data as CSV."""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Username", "Date", "Hours", "Issues"])
        
        # Write data rows
        for date_str in sorted(data.keys()):
            entry = data[date_str]
            hours = entry['total_hours']
            issues = "; ".join(entry['issues'])
            writer.writerow([username, date_str, f"{hours:.2f}", issues])
        
        # Calculate and write total
        total_hours = sum(entry['total_hours'] for entry in data.values())
        writer.writerow([username, "Total", f"{total_hours:.2f}", ""])
        
        return output.getvalue()


class TSVFormatter(Formatter):
    """Format work logs as TSV."""
    
    def format(self, username: str, data: Dict[str, Dict[str, Any]]) -> str:
        """Format work log data as TSV."""
        output = StringIO()
        writer = csv.writer(output, delimiter='\t')
        
        # Write header
        writer.writerow(["Username", "Date", "Hours", "Issues"])
        
        # Write data rows
        for date_str in sorted(data.keys()):
            entry = data[date_str]
            hours = entry['total_hours']
            issues = "; ".join(entry['issues'])
            writer.writerow([username, date_str, f"{hours:.2f}", issues])
        
        # Calculate and write total
        total_hours = sum(entry['total_hours'] for entry in data.values())
        writer.writerow([username, "Total", f"{total_hours:.2f}", ""])
        
        return output.getvalue()


class JSONFormatter(Formatter):
    """Format work logs as JSON."""
    
    def format(self, username: str, data: Dict[str, Dict[str, Any]]) -> str:
        """Format work log data as JSON."""
        # Prepare output data
        output_data = {
            "username": username,
            "work_logs": []
        }
        
        total_hours = 0
        for date_str in sorted(data.keys()):
            entry = data[date_str]
            hours = entry['total_hours']
            output_data["work_logs"].append({
                "date": date_str,
                "hours": round(hours, 2),
                "issues": entry['issues']
            })
            total_hours += hours
        
        output_data["total_hours"] = round(total_hours, 2)
        
        return json.dumps(output_data, indent=2)


class YAMLFormatter(Formatter):
    """Format work logs as YAML."""
    
    def format(self, username: str, data: Dict[str, Dict[str, Any]]) -> str:
        """Format work log data as YAML."""
        # Prepare output data
        output_data = {
            "username": username,
            "work_logs": []
        }
        
        total_hours = 0
        for date_str in sorted(data.keys()):
            entry = data[date_str]
            hours = entry['total_hours']
            output_data["work_logs"].append({
                "date": date_str,
                "hours": round(hours, 2),
                "issues": entry['issues']
            })
            total_hours += hours
        
        output_data["total_hours"] = round(total_hours, 2)
        
        return yaml.dump(output_data, default_flow_style=False, sort_keys=False)


def get_formatter(format_type: str) -> Formatter:
    """Get formatter instance based on format type.
    
    Args:
        format_type: One of 'table', 'csv', 'tsv', 'json', 'yaml'
        
    Returns:
        Formatter instance
    """
    formatters = {
        'table': TableFormatter,
        'csv': CSVFormatter,
        'tsv': TSVFormatter,
        'json': JSONFormatter,
        'yaml': YAMLFormatter
    }
    
    formatter_class = formatters.get(format_type.lower())
    if not formatter_class:
        raise ValueError(f"Unknown format type: {format_type}")
    
    return formatter_class()
