from pydantic import BaseModel


class Task(BaseModel):
    """Task 数据模型 — 与 src/main.py 中的 Task 一致"""
    id: str
    title: str
    priority: str
