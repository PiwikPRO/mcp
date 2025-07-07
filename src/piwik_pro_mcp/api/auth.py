"""
OAuth2 authentication for Piwik PRO API client.
"""

import time
from typing import Dict, Optional

import requests

from .config import Config
from .exceptions import AuthenticationError


class OAuth2Handler:
    """Handles OAuth2 client credentials authentication."""

    def __init__(self, config: Config):
        """
        Initialize OAuth2 handler.

        Args:
            config: Configuration instance
        """
        self.config = config
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._token_buffer = 60  # Refresh token 60 seconds before expiry

    def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.

        Returns:
            Valid access token

        Raises:
            AuthenticationError: If authentication fails
        """
        if self._is_token_valid():
            assert self._access_token is not None, "Token should be valid"
            return self._access_token

        return self._refresh_token()

    def _is_token_valid(self) -> bool:
        """Check if current token is valid and not expired."""
        if not self._access_token:
            return False

        return time.time() < (self._token_expires_at - self._token_buffer)

    def _refresh_token(self) -> str:
        """
        Refresh the access token using client credentials.

        Returns:
            New access token

        Raises:
            AuthenticationError: If authentication fails
        """
        data = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        try:
            response = requests.post(
                self.config.token_url,
                data=data,
                headers=headers,
                timeout=30,
            )

            if response.status_code != 200:
                raise AuthenticationError(
                    f"Failed to authenticate: {response.status_code} - {response.text}",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else {},
                )

            token_data = response.json()

            self._access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 1800)
            self._token_expires_at = time.time() + expires_in

            assert self._access_token is not None, "Token should be set"
            return self._access_token

        except requests.RequestException as e:
            raise AuthenticationError(f"Network error during authentication: {str(e)}")
        except KeyError as e:
            raise AuthenticationError(f"Invalid token response format: missing {str(e)}")

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.

        Returns:
            Dictionary with Authorization header
        """
        token = self.get_access_token()
        return {"Authorization": f"Bearer {token}"}
