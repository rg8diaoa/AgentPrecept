"""
TC-TASK-01：正常创建任务
  给定 无前置条件
  当   POST /tasks {"title": "Buy milk"}
  则   返回 201 + id + title + priority
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task():
    """TC-TASK-01：正常创建任务"""
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert "id" in data


def test_list_tasks():
    """TC-TASK-02：列出任务"""
    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B"})
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_delete_task():
    """TC-TASK-03：删除任务"""
    create_resp = client.post("/tasks", json={"title": "Delete me"})
    task_id = create_resp.json()["id"]
    delete_resp = client.delete(f"/tasks/{task_id}")
    assert delete_resp.status_code == 204
