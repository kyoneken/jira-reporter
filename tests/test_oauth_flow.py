"""Tests for OAuth flow."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from jira_reporter.oauth_flow import JiraOAuthFlow


@pytest.fixture
def mock_oauth_session():
    """Mock OAuth1Session."""
    with patch('jira_reporter.oauth_flow.OAuth1Session') as mock:
        yield mock


def test_oauth_flow_init():
    """Test OAuth flow initialization."""
    flow = JiraOAuthFlow(
        jira_url="https://jira.example.com",
        consumer_key="test-key",
        private_key="test-private-key"
    )
    
    assert flow.jira_url == "https://jira.example.com"
    assert flow.consumer_key == "test-key"
    assert flow.private_key == "test-private-key"


def test_oauth_flow_init_strips_trailing_slash():
    """Test OAuth flow initialization strips trailing slash from URL."""
    flow = JiraOAuthFlow(
        jira_url="https://jira.example.com/",
        consumer_key="test-key",
        private_key="test-private-key"
    )
    
    assert flow.jira_url == "https://jira.example.com"


def test_get_authorization_url():
    """Test getting authorization URL."""
    flow = JiraOAuthFlow(
        jira_url="https://jira.example.com",
        consumer_key="test-key",
        private_key="test-private-key"
    )
    
    auth_url = flow.get_authorization_url("test-token")
    assert auth_url == "https://jira.example.com/plugins/servlet/oauth/authorize?oauth_token=test-token"


def test_get_request_token_success(mock_oauth_session):
    """Test successful request token retrieval."""
    # Setup mock
    mock_session = MagicMock()
    mock_session.fetch_request_token.return_value = {
        'oauth_token': 'request-token',
        'oauth_token_secret': 'request-secret'
    }
    mock_oauth_session.return_value = mock_session
    
    flow = JiraOAuthFlow(
        jira_url="https://jira.example.com",
        consumer_key="test-key",
        private_key="test-private-key"
    )
    
    token, secret = flow.get_request_token()
    
    assert token == 'request-token'
    assert secret == 'request-secret'
    mock_session.fetch_request_token.assert_called_once()


def test_get_request_token_failure(mock_oauth_session):
    """Test request token retrieval failure."""
    # Setup mock
    mock_session = MagicMock()
    mock_session.fetch_request_token.side_effect = Exception("Connection error")
    mock_oauth_session.return_value = mock_session
    
    flow = JiraOAuthFlow(
        jira_url="https://jira.example.com",
        consumer_key="test-key",
        private_key="test-private-key"
    )
    
    with pytest.raises(ValueError, match="Failed to get request token"):
        flow.get_request_token()


def test_get_access_token_success(mock_oauth_session):
    """Test successful access token retrieval."""
    # Setup mock
    mock_session = MagicMock()
    mock_session.fetch_access_token.return_value = {
        'oauth_token': 'access-token',
        'oauth_token_secret': 'access-secret'
    }
    mock_oauth_session.return_value = mock_session
    
    flow = JiraOAuthFlow(
        jira_url="https://jira.example.com",
        consumer_key="test-key",
        private_key="test-private-key"
    )
    
    token, secret = flow.get_access_token(
        "request-token",
        "request-secret",
        "verifier-code"
    )
    
    assert token == 'access-token'
    assert secret == 'access-secret'
    mock_session.fetch_access_token.assert_called_once()


def test_get_access_token_failure(mock_oauth_session):
    """Test access token retrieval failure."""
    # Setup mock
    mock_session = MagicMock()
    mock_session.fetch_access_token.side_effect = Exception("Invalid verifier")
    mock_oauth_session.return_value = mock_session
    
    flow = JiraOAuthFlow(
        jira_url="https://jira.example.com",
        consumer_key="test-key",
        private_key="test-private-key"
    )
    
    with pytest.raises(ValueError, match="Failed to get access token"):
        flow.get_access_token("request-token", "request-secret", "bad-verifier")


def test_perform_oauth_dance_success(mock_oauth_session):
    """Test successful OAuth dance."""
    # Setup mocks
    mock_session1 = MagicMock()
    mock_session1.fetch_request_token.return_value = {
        'oauth_token': 'request-token',
        'oauth_token_secret': 'request-secret'
    }
    
    mock_session2 = MagicMock()
    mock_session2.fetch_access_token.return_value = {
        'oauth_token': 'access-token',
        'oauth_token_secret': 'access-secret'
    }
    
    mock_oauth_session.side_effect = [mock_session1, mock_session2]
    
    flow = JiraOAuthFlow(
        jira_url="https://jira.example.com",
        consumer_key="test-key",
        private_key="test-private-key"
    )
    
    # Mock user input and browser
    with patch('builtins.input', return_value='verifier-code'), \
         patch('webbrowser.open'):
        
        token, secret = flow.perform_oauth_dance(auto_open_browser=False)
        
        assert token == 'access-token'
        assert secret == 'access-secret'


def test_perform_oauth_dance_empty_verifier(mock_oauth_session):
    """Test OAuth dance with empty verifier."""
    # Setup mock
    mock_session = MagicMock()
    mock_session.fetch_request_token.return_value = {
        'oauth_token': 'request-token',
        'oauth_token_secret': 'request-secret'
    }
    mock_oauth_session.return_value = mock_session
    
    flow = JiraOAuthFlow(
        jira_url="https://jira.example.com",
        consumer_key="test-key",
        private_key="test-private-key"
    )
    
    # Mock user input with empty verifier
    with patch('builtins.input', return_value=''), \
         patch('webbrowser.open'):
        
        with pytest.raises(ValueError, match="Verification code is required"):
            flow.perform_oauth_dance(auto_open_browser=False)
