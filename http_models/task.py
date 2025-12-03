from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class PriorityEnum(str, Enum):
    urgent = "urgent"
    high = "high"
    medium = "medium"
    low = "low"

class StatusEnum(str, Enum):
    pending = "pending"
    inprogress = "inprogress"
    completed = "completed"



class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    priority: PriorityEnum 
    status: StatusEnum
    due_by: Optional[datetime] # Col added later using migration
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        orm_model = True


class CreateTask(BaseModel):
    title: str
    description: str
    priority: PriorityEnum = PriorityEnum.medium
    status: StatusEnum = StatusEnum.pending
    due_by: Optional[datetime] = None

    class Config:
        extra = "forbid"


class Updatetask(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None
    due_by: Optional[datetime] = None


    class Config:
        extra = "forbid"


class DeleteTask(BaseModel):
    id: str
    is_deleted: bool

    class Config:
        orm_model = True

TaskResponse.model_rebuild()
