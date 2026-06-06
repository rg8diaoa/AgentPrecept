"""Todo API — agent-compass 演示项目

这是一个最小可用示例，展示 agent-compass 方法论如何落地。
配合 docs/ 中的文档体系使用。
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Todo API", version="1.0.0")

# 内存存储（演示用）
tasks_db: dict[str, "Task"] = {}


class TaskCreate(BaseModel):
    title: str
    priority: str = "P2"


class Task(BaseModel):
    id: str
    title: str
    priority: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(req: TaskCreate):
    import uuid
    task = Task(id=str(uuid.uuid4())[:8], title=req.title, priority=req.priority)
    tasks_db[task.id] = task
    return task


@app.get("/tasks", response_model=List[Task])
def list_tasks():
    return list(tasks_db.values())


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, req: TaskCreate):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks_db[task_id].title = req.title
    tasks_db[task_id].priority = req.priority
    return tasks_db[task_id]


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]
