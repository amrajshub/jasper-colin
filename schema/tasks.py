from database.models import StatusEnum
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from typing import List, Optional
from enum import Enum
from datetime import date, datetime


class TaskFetchFilters(BaseModel):
    limit: int = Field(10)
    offset: int = Field(0)
    status: StatusEnum = StatusEnum.pending
    title: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class TaskCreate(TaskBase):
    status: StatusEnum = StatusEnum.pending


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[StatusEnum] = None


class TaskResponse(TaskBase):
    id: UUID
    title: Optional[str]
    status: StatusEnum
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True

    @field_validator("created_at", mode="before")
    def format_created_at(cls, value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    @field_validator("updated_at", mode="before")
    def format_updated_at(cls, value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value


class TaskListResponse(BaseModel):
    data: List[TaskResponse]
    count: int
