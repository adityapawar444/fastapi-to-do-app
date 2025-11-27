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
    db: Session = Depends(get_db_session_for_request)
):
    return db.query(
        Task
    ).filter(
        Task.is_deleted==False
    ).all()


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
    task = Task(
        title=payload.title,
        description=payload.description,
        status="pending"
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
