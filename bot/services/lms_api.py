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

    async def get_learners(self) -> list[dict]:
        """Get enrolled students and groups."""
        client = await self._get_client()
        response = await client.get("/learners/")
        response.raise_for_status()
        return response.json()

    async def get_scores(self, lab: str) -> list[dict]:
        """Get score distribution (4 buckets) for a lab."""
        client = await self._get_client()
        response = await client.get(f"/analytics/scores?lab={lab}")
        response.raise_for_status()
        return response.json()

    async def get_pass_rates(self, lab: str) -> list[dict]:
        """Get per-task average scores and attempt counts for a lab."""
        client = await self._get_client()
        response = await client.get(f"/analytics/pass-rates?lab={lab}")
        response.raise_for_status()
        return response.json()

    async def get_timeline(self, lab: str) -> list[dict]:
        """Get submissions per day for a lab."""
        client = await self._get_client()
        response = await client.get(f"/analytics/timeline?lab={lab}")
        response.raise_for_status()
        return response.json()

    async def get_groups(self, lab: str) -> list[dict]:
        """Get per-group scores and student counts for a lab."""
        client = await self._get_client()
        response = await client.get(f"/analytics/groups?lab={lab}")
        response.raise_for_status()
        return response.json()

    async def get_top_learners(self, lab: str, limit: int = 10) -> list[dict]:
        """Get top N learners by score for a lab."""
        client = await self._get_client()
        response = await client.get(f"/analytics/top-learners?lab={lab}&limit={limit}")
        response.raise_for_status()
        return response.json()

    async def get_completion_rate(self, lab: str) -> dict:
        """Get completion rate percentage for a lab."""
        client = await self._get_client()
        response = await client.get(f"/analytics/completion-rate?lab={lab}")
        response.raise_for_status()
        return response.json()

    async def trigger_sync(self) -> dict:
        """Refresh data from autochecker."""
        client = await self._get_client()
        response = await client.post("/pipeline/sync")
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Global instance
lms_client = LMSAPIClient()
