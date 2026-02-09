from __future__ import annotations

from dataclasses import dataclass

import httpx

API_BASE = "https://api.cursor.com/v0/agents"


@dataclass
class AgentResponse:
    agent_id: str
    agent_url: str


@dataclass
class AgentStatus:
    status: str
    agent_url: str
    pr_url: str = ""


class CursorClientError(Exception):
    pass


class CursorClient:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._http = httpx.Client(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

    def launch_agent(
        self,
        prompt: str,
        repository: str,
        ref: str = "main",
    ) -> AgentResponse:
        payload = {
            "prompt": {"text": prompt},
            "source": {
                "repository": repository,
                "ref": ref,
            },
            "target": {
                "autoCreatePr": True,
            },
        }
        try:
            resp = self._http.post(API_BASE, json=payload)
        except httpx.RequestError as e:
            raise CursorClientError(f"Failed to reach Cloud Agents API: {e}")

        if resp.status_code == 401:
            raise CursorClientError("Invalid CURSOR_API_KEY")
        if resp.status_code == 429:
            raise CursorClientError("Rate limited, try again later")
        if resp.status_code >= 500:
            raise CursorClientError("Cloud Agents API unavailable")
        if resp.status_code >= 400:
            raise CursorClientError(
                f"Cloud Agents API error {resp.status_code}: {resp.text}"
            )

        data = resp.json()
        agent_id = data.get("id", "")
        return AgentResponse(
            agent_id=agent_id,
            agent_url=f"https://cursor.com/agents/{agent_id}",
        )

    def get_status(self, agent_id: str) -> AgentStatus:
        try:
            resp = self._http.get(f"{API_BASE}/{agent_id}")
        except httpx.RequestError as e:
            raise CursorClientError(f"Failed to reach Cloud Agents API: {e}")

        if resp.status_code == 404:
            raise CursorClientError("Agent not found")
        if resp.status_code >= 400:
            raise CursorClientError(
                f"Cloud Agents API error {resp.status_code}: {resp.text}"
            )

        data = resp.json()
        status = data.get("status", "unknown")
        pr_url = ""
        if "pullRequest" in data:
            pr_data = data["pullRequest"]
            if isinstance(pr_data, dict):
                pr_url = pr_data.get("url", "")
            elif isinstance(pr_data, str):
                pr_url = pr_data

        return AgentStatus(
            status=status,
            agent_url=f"https://cursor.com/agents/{agent_id}",
            pr_url=pr_url,
        )

    def close(self) -> None:
        self._http.close()
