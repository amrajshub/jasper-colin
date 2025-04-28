from datetime import timedelta
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database.models import HttpLogs, Task
from schema.tasks import TaskCreate, TaskFetchFilters, TaskResponse, TaskUpdate
from utils.cache import (
    make_cache_key,
    get_cached_response,
    set_cached_response,
    invalidate_cache_by_prefix,
)


async def create_task(db: AsyncSession, task: TaskCreate):
    db_task = Task(**task.model_dump())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def create_log(db: AsyncSession, log: HttpLogs):
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def get_tasks(db: AsyncSession, filters: TaskFetchFilters):
    key = await make_cache_key("tasks", **filters.model_dump(exclude_unset=True))
    count_key = await make_cache_key(
        "tasks:count", **filters.model_dump(exclude_unset=True)
    )
    cached_result = await get_cached_response(key)
    cached_total = await get_cached_response(count_key)

    if cached_result:
        cached_result = json.loads(cached_result)
        cached_result = [Task(**cr) for cr in cached_result]
        return cached_result, int(json.loads(cached_total))

    db_query = select(Task)
    if filters.status:
        db_query = db_query.filter(Task.status == filters.status)
    if filters.title:
        db_query = db_query = db_query.filter(Task.title.ilike(f"%{filters.title}%"))

    if filters.start_date:
        if not filters.end_date:
            filters.end_date = filters.start_date + timedelta(days=30)
        db_query = db_query = db_query.filter(
            Task.created_at >= filters.start_date, Task.created_at <= filters.end_date
        )

    count_query = select(func.count()).select_from(db_query.subquery())

    result = (
        (await db.execute(db_query.offset(filters.offset).limit(filters.limit)))
        .scalars()
        .all()
    )
    total = await db.scalar(count_query)

    await set_cached_response(
        key, [TaskResponse(**task.__dict__).model_dump() for task in result], ttl=300
    )
    await set_cached_response(count_key, total, ttl=300)
    return result, total


async def get_task(db: AsyncSession, task_id):
    key = f"task:{task_id}"

    cached = await get_cached_response(key)
    if cached:
        return Task(**json.loads(cached))

    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()

    if task:
        await set_cached_response(
            key, TaskResponse(**task.__dict__).model_dump(), ttl=300
        )

    return task


async def update_task(db: AsyncSession, task_id, task: TaskUpdate):
    db_task = await get_task(db, task_id)
    if not db_task:
        return None

    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)

    try:
        await db.commit()
        if db_task in db:
            await db.refresh(db_task)
        else:
            db_task = await get_task(db, task_id)
    except Exception as e:
        await db.rollback()
        raise e

    await invalidate_cache_by_prefix("tasks")
    return db_task


async def delete_task(db: AsyncSession, task_id):
    db_task = await get_task(db, task_id)
    if not db_task:
        return None

    await db.delete(db_task)
    await db.commit()
    await invalidate_cache_by_prefix("tasks")
    return db_task
