"""LMS API client service."""

import httpx

from config import settings


class LMSAPIClient:
    """Client for the LMS API."""

    def __init__(self):
        self.base_url = settings.lms_api_base_url
        self.api_key = settings.lms_api_key
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with auth headers."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30.0,
            )
        return self._client

    async def health_check(self) -> bool:
        """Check if the backend is accessible."""
        try:
            client = await self._get_client()
            response = await client.get("/items/")
            return response.status_code == 200
        except Exception:
            return False

    async def get_items(self) -> list[dict]:
        """Get all items (labs/tasks)."""
        client = await self._get_client()
        response = await client.get("/items/")
        response.raise_for_status()
        return response.json()

    async def get_analytics(self) -> dict | None:
        """Get analytics data."""
        client = await self._get_client()
        try:
            response = await client.get("/analytics/summary/")
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return None

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Global instance
lms_client = LMSAPIClient()
