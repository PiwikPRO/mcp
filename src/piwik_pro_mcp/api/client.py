"""
Main HTTP client for Piwik PRO API.
"""

import json
from typing import Any, Dict, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .auth import OAuth2Handler
from .config import Config
from .exceptions import (
    AuthenticationError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    PiwikProAPIError,
)
from .methods.analytics import AnalyticsAPI
from .methods.apps import AppsAPI
from .methods.cdp import CdpAPI
from .methods.container_settings import ContainerSettingsAPI
from .methods.tag_manager import TagManagerAPI
from .methods.tracker_settings import TrackerSettingsAPI


class PiwikProClient:
    """Main client for Piwik PRO API."""

    def __init__(
        self,
        host: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize Piwik PRO API client.

        Args:
            host: Piwik PRO instance hostname
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.config = Config(host=host, client_id=client_id, client_secret=client_secret)
        self.auth = OAuth2Handler(self.config)
        self.timeout = timeout

        # Set up session with retry strategy
        self.session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Initialize API modules directly
        self.apps = AppsAPI(self)
        self.cdp = CdpAPI(self)
        self.tag_manager = TagManagerAPI(self)
        self.container_settings = ContainerSettingsAPI(self)
        self.tracker_settings = TrackerSettingsAPI(self)
        self.analytics = AnalyticsAPI(self)

    def _get_headers(self, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Get request headers including authentication.

        Args:
            extra_headers: Additional headers to include

        Returns:
            Complete headers dictionary
        """
        headers = {
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
            "User-Agent": "piwik-pro-api-python/0.2.0",
        }

        # Add authentication headers
        headers.update(self.auth.get_auth_headers())

        # Add any extra headers
        if extra_headers:
            headers.update(extra_headers)

        return headers

    def _handle_error_response(self, response: requests.Response) -> None:
        """
        Handle error responses and raise appropriate exceptions.

        Args:
            response: HTTP response object

        Raises:
            PiwikProAPIError: Appropriate exception based on status code
        """
        status_code = response.status_code

        try:
            error_data = response.json()
        except (json.JSONDecodeError, ValueError):
            # Enhanced error message with status code and response text for debugging
            response_text = response.text or "No response body"
            error_data = {"errors": [{"title": f"HTTP {status_code}: {response_text}"}]}

        error_message = f"API request failed (HTTP {status_code})"
        error_message += f"Response:\n{error_data}"

        if status_code == 400:
            raise BadRequestError(error_message, status_code, error_data)
        elif status_code == 401:
            raise AuthenticationError(error_message, status_code, error_data)
        elif status_code == 403:
            raise ForbiddenError(error_message, status_code, error_data)
        elif status_code == 404:
            raise NotFoundError(error_message, status_code, error_data)
        elif status_code == 409:
            raise ConflictError(error_message, status_code, error_data)
        else:
            raise PiwikProAPIError(error_message, status_code, error_data)

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Union[Dict[str, Any], None]:
        """
        Make an authenticated API request.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            extra_headers: Additional headers

        Returns:
            Response data or None for 204 responses

        Raises:
            PiwikProAPIError: If the request fails
        """
        url = f"{self.config.base_url}{endpoint}"
        headers = self._get_headers(extra_headers)

        # Prepare request data
        json_data = None
        if data is not None:
            json_data = data

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=self.timeout,
            )

            # Handle successful responses
            if response.status_code == 204:
                return None

            if response.status_code in (200, 201, 202):
                try:
                    return response.json()
                except (json.JSONDecodeError, ValueError):
                    return {}

            # Handle error responses
            self._handle_error_response(response)
            # This line should never be reached as _handle_error_response always raises
            return None

        except requests.RequestException as e:
            raise PiwikProAPIError(f"Network error: {str(e)}")

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> dict[str, Any] | list | None:
        """Make a GET request."""
        return self.request("GET", endpoint, params=params, extra_headers=extra_headers)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Union[Dict[str, Any], None]:
        """Make a POST request."""
        return self.request("POST", endpoint, params=params, data=data, extra_headers=extra_headers)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Union[Dict[str, Any], None]:
        """Make a PUT request."""
        return self.request("PUT", endpoint, params=params, data=data, extra_headers=extra_headers)

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Union[Dict[str, Any], None]:
        """Make a PATCH request."""
        return self.request("PATCH", endpoint, params=params, data=data, extra_headers=extra_headers)

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Union[Dict[str, Any], None]:
        """Make a DELETE request."""
        return self.request("DELETE", endpoint, params=params, extra_headers=extra_headers)
