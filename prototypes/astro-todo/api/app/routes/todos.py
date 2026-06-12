import uuid

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db
from app.schemas.todo import TodoCreate
from app.schemas.todo import TodoListResponse
from app.schemas.todo import TodoResponse
from app.schemas.todo import TodoUpdate
from app.services.todo_service import TodoService

router = APIRouter()


def get_service(db: AsyncSession = Depends(get_db)) -> TodoService:
    return TodoService(db)


@router.get("", response_model=TodoListResponse)
async def list_todos(service: TodoService = Depends(get_service)):
    return await service.list_todos()


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(payload: TodoCreate, service: TodoService = Depends(get_service)):
    return await service.create_todo(payload)


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: uuid.UUID, service: TodoService = Depends(get_service)):
    todo = await service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return TodoResponse.model_validate(todo)


@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: uuid.UUID, payload: TodoUpdate, service: TodoService = Depends(get_service)):
    todo = await service.update_todo(todo_id, payload)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.patch("/{todo_id}/toggle", response_model=TodoResponse)
async def toggle_todo(todo_id: uuid.UUID, service: TodoService = Depends(get_service)):
    todo = await service.toggle_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: uuid.UUID, service: TodoService = Depends(get_service)):
    deleted = await service.delete_todo(todo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Todo not found")
