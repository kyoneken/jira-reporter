"""Jira API client with OAuth authentication."""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from jira import JIRA
from jira.exceptions import JIRAError
from .config import Config


class JiraClient:
    """Client for interacting with Jira API."""
    
    def __init__(self, config: Config):
        """Initialize Jira client.
        
        Args:
            config: Configuration object containing Jira and OAuth settings
        """
        self.config = config
        self.jira = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Jira using OAuth authentication."""
        jira_url = self.config.get_jira_url()
        oauth_config = self.config.get_oauth_config()
        
        if not jira_url:
            raise ValueError("Jira URL not configured. Please run 'jira-reporter configure' first.")
        
        if not oauth_config:
            raise ValueError("OAuth configuration not found. Please run 'jira-reporter configure' first.")
        
        # OAuth authentication
        oauth_dict = {
            'access_token': oauth_config.get('access_token'),
            'access_token_secret': oauth_config.get('access_token_secret'),
            'consumer_key': oauth_config.get('consumer_key'),
            'key_cert': oauth_config.get('key_cert')
        }
        
        try:
            self.jira = JIRA(server=jira_url, oauth=oauth_dict)
        except JIRAError as e:
            raise ValueError(f"Failed to connect to Jira: {e}")
    
    def get_user_worklogs(
        self,
        username: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get work logs for a specific user within a date range.
        
        Args:
            username: Jira username
            start_date: Start date for work logs
            end_date: End date for work logs
            
        Returns:
            List of work log entries
        """
        worklogs = []
        
        # Build JQL query to find issues worked on by the user in the date range
        jql = f'worklogAuthor = "{username}" AND worklogDate >= "{start_date.strftime("%Y-%m-%d")}" AND worklogDate <= "{end_date.strftime("%Y-%m-%d")}"'
        
        try:
            # Search for issues
            issues = self.jira.search_issues(jql, maxResults=1000)
            
            # For each issue, get work logs
            for issue in issues:
                issue_worklogs = self.jira.worklogs(issue.key)
                
                for worklog in issue_worklogs:
                    # Filter work logs by author and date range
                    worklog_author = worklog.author.name if hasattr(worklog.author, 'name') else str(worklog.author)
                    if worklog_author == username:
                        # Parse worklog date
                        worklog_date = datetime.strptime(worklog.started[:10], "%Y-%m-%d")
                        
                        if start_date <= worklog_date <= end_date:
                            worklogs.append({
                                'issue_key': issue.key,
                                'issue_summary': issue.fields.summary,
                                'date': worklog_date,
                                'time_spent': worklog.timeSpentSeconds,
                                'comment': getattr(worklog, 'comment', '')
                            })
        except JIRAError as e:
            raise ValueError(f"Failed to fetch work logs: {e}")
        
        return worklogs
    
    def aggregate_worklogs_by_day(
        self,
        worklogs: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Aggregate work logs by day.
        
        Args:
            worklogs: List of work log entries
            
        Returns:
            Dictionary with dates as keys and aggregated data as values
        """
        aggregated = {}
        
        for worklog in worklogs:
            date_str = worklog['date'].strftime("%Y-%m-%d")
            
            if date_str not in aggregated:
                aggregated[date_str] = {
                    'date': worklog['date'],
                    'total_seconds': 0,
                    'issues': set()
                }
            
            aggregated[date_str]['total_seconds'] += worklog['time_spent']
            aggregated[date_str]['issues'].add(worklog['issue_key'])
        
        # Convert sets to lists for serialization
        for date_str in aggregated:
            aggregated[date_str]['issues'] = sorted(list(aggregated[date_str]['issues']))
            aggregated[date_str]['total_hours'] = aggregated[date_str]['total_seconds'] / 3600
        
        return aggregated
