"""LLM API client service for intent routing with tool calling."""

import json
import sys
from typing import Any

import httpx

from config import settings


# Tool schemas for all 9 backend endpoints
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks. Use this to discover what labs are available.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled students and their groups. Use to answer questions about enrollment or student count.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-03'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average pass rates and attempt counts for a lab. Use to compare task difficulty or find the hardest task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-03'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a lab. Use to see activity patterns over time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-03'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a lab. Use to compare group performance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-03'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab. Use to show leaderboard or best students.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-03'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return, default 10"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab. Use to see how many students finished the lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-03'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Refresh data from autochecker. Use when user asks to update or sync the latest submissions.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


class LLMAPIClient:
    """Client for the LLM API (Qwen Code proxy) with tool calling support."""

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

    def _debug(self, message: str) -> None:
        """Print debug message to stderr."""
        print(message, file=sys.stderr)

    async def route(self, message: str, lms_client: Any) -> str:
        """
        Route a user message through the LLM tool calling loop.

        Flow:
        1. Send message + tool definitions to LLM
        2. LLM returns tool calls (or text response)
        3. Execute tool calls via lms_client
        4. Feed results back to LLM
        5. LLM produces final answer

        Args:
            message: User's message
            lms_client: LMSAPIClient instance for executing tool calls

        Returns:
            Final response to send to user
        """
        client = await self._get_client()

        system_prompt = (
            "You are a helpful assistant for a Learning Management System (LMS). "
            "You have access to tools that let you fetch data about labs, students, scores, and submissions. "
            "When the user asks a question, use the available tools to get the data they need. "
            "If you need data from multiple tools, call them one at a time and reason across results. "
            "After getting tool results, synthesize them into a clear, helpful answer. "
            "Include specific numbers and lab names when available. "
            "If the user's message is a greeting or casual chat, respond naturally without using tools. "
            "If you don't understand the question, ask for clarification or suggest what you can help with."
        )

        messages: list[dict] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]

        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            try:
                response = await client.post(
                    "/chat/completions",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "tools": TOOL_SCHEMAS,
                        "tool_choice": "auto",  # Let LLM decide whether to use tools
                        "max_tokens": 1000,
                    },
                )
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                self._debug(f"[error] LLM API error: {e}")
                return f"Sorry, I encountered an error processing your request: {type(e).__name__}"

            assistant_message = data["choices"][0]["message"]

            # Check if LLM wants to call tools
            tool_calls = assistant_message.get("tool_calls", [])

            if not tool_calls:
                # LLM returned a text response — we're done
                return assistant_message.get("content", "I don't have a response for that.")

            # Add assistant message with tool calls to conversation
            messages.append(assistant_message)

            # Execute each tool call
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])
                tool_call_id = tool_call["id"]

                self._debug(f"[tool] LLM called: {function_name}({function_args})")

                # Execute the tool via lms_client
                try:
                    if function_name == "get_items":
                        result = await lms_client.get_items()
                    elif function_name == "get_learners":
                        result = await lms_client.get_learners()
                    elif function_name == "get_scores":
                        result = await lms_client.get_scores(function_args.get("lab", ""))
                    elif function_name == "get_pass_rates":
                        result = await lms_client.get_pass_rates(function_args.get("lab", ""))
                    elif function_name == "get_timeline":
                        result = await lms_client.get_timeline(function_args.get("lab", ""))
                    elif function_name == "get_groups":
                        result = await lms_client.get_groups(function_args.get("lab", ""))
                    elif function_name == "get_top_learners":
                        result = await lms_client.get_top_learners(
                            function_args.get("lab", ""),
                            function_args.get("limit", 10)
                        )
                    elif function_name == "get_completion_rate":
                        result = await lms_client.get_completion_rate(function_args.get("lab", ""))
                    elif function_name == "trigger_sync":
                        result = await lms_client.trigger_sync()
                    else:
                        result = {"error": f"Unknown tool: {function_name}"}

                    self._debug(f"[tool] Result: {len(result) if isinstance(result, list) else 'object'} items")
                except Exception as e:
                    self._debug(f"[tool] Error executing {function_name}: {e}")
                    result = {"error": str(e)}

                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": json.dumps(result, ensure_ascii=False),
                })

            self._debug(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM")

        # If we hit max iterations, return what we have
        return "I'm still processing your request. Please try again."

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Global instance
llm_client = LLMAPIClient()
