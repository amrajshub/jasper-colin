import json
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from schema.tasks import (
    TaskCreate,
    TaskFetchFilters,
    TaskListResponse,
    TaskUpdate,
    TaskResponse,
)
from utils.crud import *
from database.session import get_db
from uuid import UUID

from utils.keycloak import check_privilege

# from utils.cache import get_cached_response, set_cached_response, make_cache_key
# from utils.cache import invalidate_cache_by_prefix

router = APIRouter()


@router.get("/health-check")  # better health check
async def health_check(
    db: AsyncSession = Depends(get_db), _: bool = Depends(check_privilege("admin"))
):
    db.execute("SELECT 1")
    return {"status": "ok"}


@router.post("/create/", response_model=TaskResponse)
async def create(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(check_privilege("user")),
):
    task_obj = await create_task(db, task)
    return task_obj


@router.get("/fetch-all/", response_model=TaskListResponse)
async def get_all(
    filters: Annotated[TaskFetchFilters, Query()],
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(check_privilege("user")),
):
    tasks, total_count = await get_tasks(db, filters)
    task_responses = [TaskResponse(**task.__dict__) for task in tasks]
    return dict(data=task_responses, count=total_count)


@router.get("/fetch/{task_id}", response_model=TaskResponse)
async def get(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(check_privilege("user")),
):
    if not task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Task Id missing"
        )
    task = await get_task(db=db, task_id=task_id)
    return task


@router.put("/update/{task_id}", response_model=TaskResponse)
async def update(
    task_id: UUID,
    task: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(check_privilege("user")),
):
    import ipdb

    ipdb.set_trace()
    updated = await update_task(db, task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/delete/{task_id}")
async def delete(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(check_privilege("user")),
):
    deleted = await delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}
