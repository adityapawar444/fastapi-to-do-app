from typing import Optional
from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db_session_for_request

from http_models.task import (
    TaskResponse,
    CreateTask,
    Updatetask,
    DeleteTask
)

from db_models.task import Task

router = APIRouter()

@router.get("/task", response_model=list[TaskResponse])
async def get_all_tasks(
    db: Session = Depends(get_db_session_for_request),
    search: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date_from: Optional[datetime] = None,
    due_date_to: Optional[datetime] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    limit: Optional[int] = None,
    offset: Optional[int] = 0
):
    query = db.query(Task).filter(Task.is_deleted == False)
    
    if search:
        query = query.filter((Task.title.ilike(f"%{search}%")) | (Task.description.ilike(f"%{search}%")))
    if title:
        query = query.filter(Task.title.ilike(f"%{title}%"))
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if due_date_from:
        query = query.filter(Task.due_date >= due_date_from)
    if due_date_to:
        query = query.filter(Task.due_date <= due_date_to)
    
    if sort_by and hasattr(Task, sort_by):
        query = query.order_by(
            getattr(Task, sort_by).asc() if sort_order == "asc" 
            else getattr(Task, sort_by).desc()
        )
    
    return query.offset(offset).limit(limit).all() if limit else query.offset(offset).all()

@router.get("/task/{id}", response_model=TaskResponse)
async def get_task_by_id(
    id: str,
    db: Session = Depends(get_db_session_for_request)
):
    task = db.query(
        Task
    ).filter(
        Task.id == id,
        Task.is_deleted == False
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/task", response_model=TaskResponse)
async def create_task(
    payload: CreateTask,
    db: Session = Depends(get_db_session_for_request)
):
    eod_today = payload.due_by
    if not eod_today:
        today = datetime.today()
        eod_today = datetime.combine(today.date(), time(23, 59, 59))

    
    allowed_priorities = ["urgent", "high", "medium", "low"]
    priority = payload.priority if payload.priority in allowed_priorities else "urgent"

    allowed_status = ["completed", "inprogress", "pending"]
    status = payload.status if payload.status in allowed_status else "pending"

    task = Task(
        title=payload.title,
        description=payload.description,
        due_by=eod_today,
        status=status,
        priority=priority # urgent, high, medium, low
    )
    try:
        db.add(task)
        db.flush()
        db.refresh(task)
        return task
    except:
        raise

@router.patch("/task/{id}", response_model=TaskResponse)
async def update_task(
    id: str,
    payload: Updatetask,
    db: Session = Depends(get_db_session_for_request)
):
    task: Task | None = db.query(
        Task
    ).filter(
        Task.id==id
    ).first()
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    db.flush()
    db.refresh(task)
    return task


@router.delete("/task/{id}", response_model=DeleteTask)
async def delete_task(
    id: str,
    db: Session = Depends(get_db_session_for_request)
):
    task: Task = db.query(
        Task
    ).filter(
        Task.id==id,
        Task.is_deleted==False
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = {
        "id": id,
        "is_deleted": True
    }
    for key, value in update_data.items():
        setattr(task, key, value)

    db.flush()
    db.refresh(task)
    return task
