"""OAuth authentication flow for Jira."""

import webbrowser
from typing import Tuple, Optional
from requests_oauthlib import OAuth1Session
from pathlib import Path


class JiraOAuthFlow:
    """Handles OAuth 1.0a three-legged authentication flow for Jira."""
    
    # OAuth endpoints for Jira
    REQUEST_TOKEN_URL = '/plugins/servlet/oauth/request-token'
    AUTHORIZE_URL = '/plugins/servlet/oauth/authorize'
    ACCESS_TOKEN_URL = '/plugins/servlet/oauth/access-token'
    
    def __init__(self, jira_url: str, consumer_key: str, private_key: str):
        """Initialize OAuth flow.
        
        Args:
            jira_url: Base URL of Jira instance
            consumer_key: OAuth consumer key
            private_key: RSA private key (PEM format string or path to file)
        """
        self.jira_url = jira_url.rstrip('/')
        self.consumer_key = consumer_key
        
        # Load private key
        if Path(private_key).exists():
            with open(private_key, 'r') as f:
                self.private_key = f.read()
        else:
            self.private_key = private_key
    
    def get_request_token(self) -> Tuple[str, str]:
        """Get request token from Jira.
        
        Returns:
            Tuple of (oauth_token, oauth_token_secret)
        """
        oauth = OAuth1Session(
            self.consumer_key,
            rsa_key=self.private_key,
            signature_method='RSA-SHA1'
        )
        
        request_token_url = f"{self.jira_url}{self.REQUEST_TOKEN_URL}"
        
        try:
            response = oauth.fetch_request_token(request_token_url)
            oauth_token = response.get('oauth_token')
            oauth_token_secret = response.get('oauth_token_secret')
            
            if not oauth_token or not oauth_token_secret:
                raise ValueError("Failed to get request token from Jira")
            
            return oauth_token, oauth_token_secret
        except Exception as e:
            raise ValueError(f"Failed to get request token: {e}")
    
    def get_authorization_url(self, oauth_token: str) -> str:
        """Get authorization URL for user to visit.
        
        Args:
            oauth_token: Request token
            
        Returns:
            Authorization URL
        """
        return f"{self.jira_url}{self.AUTHORIZE_URL}?oauth_token={oauth_token}"
    
    def get_access_token(
        self,
        oauth_token: str,
        oauth_token_secret: str,
        oauth_verifier: str
    ) -> Tuple[str, str]:
        """Exchange verifier for access token.
        
        Args:
            oauth_token: Request token
            oauth_token_secret: Request token secret
            oauth_verifier: Verification code from user authorization
            
        Returns:
            Tuple of (access_token, access_token_secret)
        """
        oauth = OAuth1Session(
            self.consumer_key,
            rsa_key=self.private_key,
            resource_owner_key=oauth_token,
            resource_owner_secret=oauth_token_secret,
            verifier=oauth_verifier,
            signature_method='RSA-SHA1'
        )
        
        access_token_url = f"{self.jira_url}{self.ACCESS_TOKEN_URL}"
        
        try:
            response = oauth.fetch_access_token(access_token_url)
            access_token = response.get('oauth_token')
            access_token_secret = response.get('oauth_token_secret')
            
            if not access_token or not access_token_secret:
                raise ValueError("Failed to get access token from Jira")
            
            return access_token, access_token_secret
        except Exception as e:
            raise ValueError(f"Failed to get access token: {e}")
    
    def perform_oauth_dance(self, auto_open_browser: bool = True) -> Tuple[str, str]:
        """Perform complete OAuth dance with user interaction.
        
        Args:
            auto_open_browser: Whether to automatically open browser
            
        Returns:
            Tuple of (access_token, access_token_secret)
        """
        # Step 1: Get request token
        oauth_token, oauth_token_secret = self.get_request_token()
        
        # Step 2: Get authorization URL and direct user
        auth_url = self.get_authorization_url(oauth_token)
        
        print("\n" + "="*70)
        print("JIRA OAUTH AUTHORIZATION")
        print("="*70)
        print("\nPlease visit the following URL to authorize this application:")
        print(f"\n  {auth_url}\n")
        
        if auto_open_browser:
            print("Opening browser automatically...")
            webbrowser.open(auth_url)
        else:
            print("Copy and paste the URL above into your browser.")
        
        print("\nAfter authorization, you will receive a verification code.")
        print("="*70 + "\n")
        
        # Step 3: Get verifier from user
        oauth_verifier = input("Enter the verification code: ").strip()
        
        if not oauth_verifier:
            raise ValueError("Verification code is required")
        
        # Step 4: Exchange verifier for access token
        print("\nExchanging verification code for access token...")
        access_token, access_token_secret = self.get_access_token(
            oauth_token,
            oauth_token_secret,
            oauth_verifier
        )
        
        print("✓ Successfully obtained access token!\n")
        
        return access_token, access_token_secret
