"""LLM API client service for intent routing."""

import httpx

from config import settings


class LLMAPIClient:
    """Client for the LLM API (Qwen Code proxy)."""

    def __init__(self):
        self.base_url = settings.llm_api_base_url
        self.api_key = settings.llm_api_key
        self.model = settings.llm_api_model
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with auth headers."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=60.0,
            )
        return self._client

    async def classify_intent(self, message: str) -> str:
        """
        Classify user intent using LLM.

        Returns intent category: 'start', 'help', 'health', 'labs', 'scores', or 'unknown'.
        """
        client = await self._get_client()

        system_prompt = (
            "You are an intent classifier for a Telegram bot. "
            "Classify the user's message into one of these categories: "
            "start, help, health, labs, scores, unknown. "
            "Respond with ONLY the category name."
        )

        try:
            response = await client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message},
                    ],
                    "max_tokens": 10,
                },
            )
            response.raise_for_status()
            data = response.json()
            intent = data["choices"][0]["message"]["content"].strip().lower()
            return intent if intent in {"start", "help", "health", "labs", "scores"} else "unknown"
        except Exception:
            return "unknown"

    async def answer_question(self, message: str, context: str = "") -> str:
        """
        Answer a natural language question using LLM.

        Args:
            message: User's question
            context: Optional context data (e.g., available labs, user scores)

        Returns:
            AI-generated response
        """
        client = await self._get_client()

        system_prompt = (
            "You are a helpful assistant for a Learning Management System. "
            "Answer student questions about labs, scores, and submissions. "
            "Be concise and helpful."
        )

        user_message = message
        if context:
            user_message = f"Context: {context}\n\nQuestion: {message}"

        try:
            response = await client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    "max_tokens": 500,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Sorry, I couldn't process that request. Error: {type(e).__name__}"

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Global instance
llm_client = LLMAPIClient()
