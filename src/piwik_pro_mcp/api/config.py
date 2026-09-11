"""
Configuration management for Piwik PRO API client.
"""

import logging
import os

from dotenv import load_dotenv

from piwik_pro_mcp.common.settings import allow_insecure_host

logger = logging.getLogger(__name__)

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Configuration class for Piwik PRO API client."""

    def __init__(
        self,
        host: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ):
        """
        Initialize configuration.

        Args:
            host: Piwik PRO instance hostname (e.g., 'example.piwik.pro')
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
        """
        # Initialize as Optional, but validation will ensure they're not None
        self.host: str | None = host or os.getenv("PIWIK_PRO_HOST")
        self.client_id: str | None = client_id or os.getenv("PIWIK_PRO_CLIENT_ID")
        self.client_secret: str | None = client_secret or os.getenv("PIWIK_PRO_CLIENT_SECRET")

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
        elif self.host.startswith("http://"):
            if not allow_insecure_host():
                raise ValueError(
                    "Insecure HTTP host is not allowed. Use HTTPS (scheme-less host or https://), "
                    "or set PIWIK_PRO_ALLOW_INSECURE_HOST=1 to opt in to plaintext API connections."
                )
            logger.warning(
                "PIWIK_PRO_HOST uses HTTP; API credentials and data will be sent over an unencrypted connection."
            )

    @property
    def base_url(self) -> str:
        """Get the base URL for API requests."""
        assert self.host is not None, "Host should be validated during initialization"
        return self.host.rstrip("/")

    @property
    def token_url(self) -> str:
        """Get the OAuth2 token endpoint URL."""
        return f"{self.base_url}/auth/token"
