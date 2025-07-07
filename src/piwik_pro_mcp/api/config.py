"""
Configuration management for Piwik PRO API client.
"""

import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Configuration class for Piwik PRO API client."""

    def __init__(
        self,
        host: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """
        Initialize configuration.

        Args:
            host: Piwik PRO instance hostname (e.g., 'example.piwik.pro')
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
        """
        # Initialize as Optional, but validation will ensure they're not None
        self.host: Optional[str] = host or os.getenv("PIWIK_PRO_HOST")
        self.client_id: Optional[str] = client_id or os.getenv("PIWIK_PRO_CLIENT_ID")
        self.client_secret: Optional[str] = client_secret or os.getenv("PIWIK_PRO_CLIENT_SECRET")

        # Validate required configuration
        self._validate()

    def _validate(self) -> None:
        """Validate that all required configuration is present."""
        if not self.host:
            raise ValueError("Host is required. Set PIWIK_PRO_HOST environment variable or pass host parameter.")

        if not self.client_id:
            raise ValueError(
                "Client ID is required. Set PIWIK_PRO_CLIENT_ID environment variable or pass client_id parameter."
            )

        if not self.client_secret:
            raise ValueError(
                "Client secret is required. Set PIWIK_PRO_CLIENT_SECRET environment variable "
                "or pass client_secret parameter."
            )

        # Ensure host has proper format
        if not self.host.startswith(("http://", "https://")):
            self.host = f"https://{self.host}"

    @property
    def base_url(self) -> str:
        """Get the base URL for API requests."""
        assert self.host is not None, "Host should be validated during initialization"
        return self.host.rstrip("/")

    @property
    def token_url(self) -> str:
        """Get the OAuth2 token endpoint URL."""
        return f"{self.base_url}/auth/token"
