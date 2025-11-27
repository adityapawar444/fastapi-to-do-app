from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        orm_model = True


class CreateTask(BaseModel):
    title: str
    description: str

    class Config:
        extra = "forbid"


class Updatetask(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

    class Config:
        extra = "forbid"


class DeleteTask(BaseModel):
    id: str
    is_deleted: bool

    class Config:
        orm_model = True


