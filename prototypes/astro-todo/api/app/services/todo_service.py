import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoListResponse, TodoResponse, TodoUpdate


class TodoService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_todos(self) -> TodoListResponse:
        result = await self.db.execute(select(Todo).order_by(Todo.created_at.desc()))
        todos = result.scalars().all()
        total = len(todos)
        completed = sum(1 for t in todos if t.completed)
        return TodoListResponse(
            items=[TodoResponse.model_validate(t) for t in todos],
            total=total,
            pending=total - completed,
            completed=completed,
        )

    async def get_todo(self, todo_id: uuid.UUID) -> Optional[Todo]:
        result = await self.db.execute(select(Todo).where(Todo.id == todo_id))
        return result.scalar_one_or_none()

    async def create_todo(self, payload: TodoCreate) -> TodoResponse:
        todo = Todo(**payload.model_dump())
        self.db.add(todo)
        await self.db.flush()
        await self.db.refresh(todo)
        return TodoResponse.model_validate(todo)

    async def update_todo(self, todo_id: uuid.UUID, payload: TodoUpdate) -> Optional[TodoResponse]:
        todo = await self.get_todo(todo_id)
        if not todo:
            return None
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(todo, field, value)
        await self.db.flush()
        await self.db.refresh(todo)
        return TodoResponse.model_validate(todo)

    async def delete_todo(self, todo_id: uuid.UUID) -> bool:
        todo = await self.get_todo(todo_id)
        if not todo:
            return False
        await self.db.delete(todo)
        return True

    async def toggle_todo(self, todo_id: uuid.UUID) -> Optional[TodoResponse]:
        todo = await self.get_todo(todo_id)
        if not todo:
            return None
        todo.completed = not todo.completed
        await self.db.flush()
        await self.db.refresh(todo)
        return TodoResponse.model_validate(todo)
