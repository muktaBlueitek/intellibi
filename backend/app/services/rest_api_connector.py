"""REST API connector for fetching data from external HTTP endpoints."""

from typing import Dict, Any, Optional, List
import pandas as pd
import httpx

from app.models.datasource import DataSource


class RestApiConnector:
    """Service for fetching data from REST API endpoints."""

    def __init__(self, timeout: float = 30.0):
        """Initialize the REST API connector."""
        self.timeout = timeout

    def _build_headers(
        self,
        connection_config: Optional[Dict[str, Any]],
        api_key: Optional[str],
        datasource: DataSource,
    ) -> Dict[str, str]:
        """Build HTTP headers from connection config and datasource."""
        headers: Dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # Add custom headers from connection_config
        if connection_config:
            custom_headers = connection_config.get("headers") or connection_config.get("custom_headers")
            if isinstance(custom_headers, dict):
                headers.update({str(k): str(v) for k, v in custom_headers.items()})
            elif isinstance(custom_headers, list):
                for h in custom_headers:
                    if isinstance(h, dict) and "name" in h and "value" in h:
                        headers[h["name"]] = str(h["value"])

        # Add auth header
        auth_type = (connection_config or {}).get("auth_type", "bearer")
        api_key_value = api_key or (connection_config or {}).get("api_key")

        if api_key_value:
            if auth_type == "bearer":
                headers["Authorization"] = f"Bearer {api_key_value}"
            elif auth_type == "api_key":
                key_header = (connection_config or {}).get("api_key_header", "X-API-Key")
                headers[key_header] = api_key_value
            elif auth_type == "basic":
                # Basic auth: API key can be "user:pass" format
                import base64
                creds = base64.b64encode(api_key_value.encode()).decode()
                headers["Authorization"] = f"Basic {creds}"

        return headers

    def fetch_data(
        self,
        datasource: DataSource,
        limit: Optional[int] = None,
        data_path: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch data from a REST API endpoint and return as pandas DataFrame.

        Supports:
        - JSON array response: [{"a": 1}, {"a": 2}]
        - JSON object with nested array: {"data": [...], "results": [...]}
          Use data_path to specify path, e.g. "data" or "results.items"
        """
        url = datasource.api_url
        if not url:
            raise ValueError("API URL is required for REST API data source")

        connection_config = datasource.connection_config or {}
        headers = self._build_headers(
            connection_config, datasource.api_key, datasource
        )

        # Resolve data_path from config if not provided
        if not data_path:
            data_path = connection_config.get("data_path")

        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

        # Extract array from response
        if data_path:
            for part in data_path.split("."):
                data = data.get(part) if isinstance(data, dict) else None
                if data is None:
                    raise ValueError(f"Data path '{data_path}' not found in response")

        if not isinstance(data, list):
            if isinstance(data, dict):
                # Single object - wrap in list
                data = [data]
            else:
                raise ValueError(
                    "REST API response must be a JSON array or object with array at data_path"
                )

        df = pd.json_normalize(data)
        if df.empty:
            return df

        if limit:
            df = df.head(limit)

        return df

    def test_connection(
        self,
        url: str,
        auth_type: str = "bearer",
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        data_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Test connection to a REST API endpoint.
        Returns success status and sample of data if available.
        """
        try:
            request_headers: Dict[str, str] = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            if headers:
                request_headers.update(headers)

            if api_key:
                if auth_type == "bearer":
                    request_headers["Authorization"] = f"Bearer {api_key}"
                elif auth_type == "api_key":
                    request_headers["X-API-Key"] = api_key

            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=request_headers)
                response.raise_for_status()
                data = response.json()

            # Validate we can extract array
            if data_path:
                for part in data_path.split("."):
                    data = data.get(part) if isinstance(data, dict) else None
                    if data is None:
                        return {
                            "success": False,
                            "message": f"Data path '{data_path}' not found in response",
                        }

            if not isinstance(data, list) and not isinstance(data, dict):
                return {
                    "success": False,
                    "message": "Response is not JSON array or object",
                }

            if isinstance(data, dict) and not data_path:
                # Allow object without path - we'll treat as single record
                pass

            row_count = len(data) if isinstance(data, list) else 1
            return {
                "success": True,
                "message": "Connection successful",
                "row_count": row_count,
            }

        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "message": f"HTTP {e.response.status_code}: {str(e)}",
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "message": f"Request failed: {str(e)}",
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
            }
