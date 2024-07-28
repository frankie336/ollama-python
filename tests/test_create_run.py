from starlette.testclient import TestClient
from api.app import create_test_app

app = create_test_app()
client = TestClient(app)

def test_create_run():
    # Test data for run
    run_data = {
        "id": "run_AmfLi6P7o09cAJC37NRu83WJ",
        "assistant_id": "asst_u9reKnPLer57WEX6HO11URx3",
        "cancelled_at": None,
        "completed_at": None,
        "created_at": 1722130419,
        "expires_at": 1722131019,
        "failed_at": None,
        "incomplete_details": None,
        "instructions": "Your name is Q. If anyone asks, “just Q”.",
        "last_error": None,
        "max_completion_tokens": None,
        "max_prompt_tokens": None,
        "meta_data": {},  # updated field name
        "model": "gpt-4-turbo-2024-04-09",
        "object": "thread.run",
        "parallel_tool_calls": True,
        "required_action": None,
        "response_format": "auto",
        "started_at": None,
        "status": "queued",
        "thread_id": "thread_yLwwRNXcnzn86nEjsk0dFrql",
        "tool_choice": "auto",
        "tools": [
            {"type": "code_interpreter"},
            {"type": "file_search", "file_search": None}
        ],
        "truncation_strategy": {"type": "auto", "last_messages": None},
        "usage": None,
        "temperature": 1.01,
        "top_p": 1.0,
        "tool_resources": {}
    }

    # Create run
    run_response = client.post("/v1/runs", json=run_data)
    assert run_response.status_code == 200
    run = run_response.json()
    assert run["id"] == run_data["id"]
    assert run["assistant_id"] == run_data["assistant_id"]

def test_get_run():
    run_id = "run_AmfLi6P7o09cAJC37NRu83WJ"
    run_response = client.get(f"/v1/runs/{run_id}")
    assert run_response.status_code == 200
    run = run_response.json()
    assert run["id"] == run_id
