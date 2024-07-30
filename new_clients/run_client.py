import httpx
import time
from typing import List, Dict, Any, Optional


class RunService:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.Client(base_url=base_url, headers={"Authorization": f"Bearer {api_key}"})

    def create_run(self, assistant_id: str, thread_id: str, instructions: Optional[str] = "",
                   meta_data: Optional[Dict[str, Any]] = {}) -> Dict[str, Any]:
        run_data = {
            "id": f"run_{assistant_id}_{thread_id}",  # Ensure this id is unique if required by your API
            "assistant_id": assistant_id,
            "thread_id": thread_id,
            "instructions": instructions,
            "meta_data": meta_data,
            "cancelled_at": None,
            "completed_at": None,
            "created_at": int(time.time()),
            "expires_at": int(time.time()) + 3600,  # Set to 1 hour later
            "failed_at": None,
            "incomplete_details": None,
            "last_error": None,
            "max_completion_tokens": 1000,
            "max_prompt_tokens": 500,
            "model": "gpt-4",
            "object": "run",
            "parallel_tool_calls": False,
            "required_action": None,
            "response_format": "text",
            "started_at": None,
            "status": "pending",
            "tool_choice": "none",
            "tools": [],
            "truncation_strategy": {},
            "usage": None,
            "temperature": 0.7,
            "top_p": 0.9,
            "tool_resources": {}
        }
        response = self.client.post("/v1/runs", json=run_data)
        print(f"Request payload: {run_data}")  # Add this line to log the request payload
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")
        response.raise_for_status()
        return response.json()

    def retrieve_run(self, run_id: str) -> Dict[str, Any]:
        response = self.client.get(f"/v1/runs/{run_id}")
        response.raise_for_status()
        return response.json()

    def update_run(self, run_id: str, **updates) -> Dict[str, Any]:
        response = self.client.put(f"/v1/runs/{run_id}", json=updates)
        response.raise_for_status()
        return response.json()

    def list_runs(self, limit: int = 20, order: str = "asc") -> List[Dict[str, Any]]:
        params = {
            "limit": limit,
            "order": order
        }
        response = self.client.get("/v1/runs", params=params)
        response.raise_for_status()
        return response.json()

    def delete_run(self, run_id: str) -> Dict[str, Any]:
        response = self.client.delete(f"/v1/runs/{run_id}")
        response.raise_for_status()
        return response.json()

    def generate(self, run_id: str, model: str, prompt: str, stream: bool = False) -> Dict[str, Any]:
        run = self.retrieve_run(run_id)
        response = self.client.post(
            "/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": stream,
                "context": run["meta_data"].get("context", []),
                "temperature": run["temperature"],
                "top_p": run["top_p"]
            }
        )
        response.raise_for_status()
        return response.json()

    def chat(self, run_id: str, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        run = self.retrieve_run(run_id)
        response = self.client.post(
            "/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": stream,
                "context": run["meta_data"].get("context", []),
                "temperature": run["temperature"],
                "top_p": run["top_p"]
            }
        )
        response.raise_for_status()
        return response.json()
