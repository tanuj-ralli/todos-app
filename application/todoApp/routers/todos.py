from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from ..database import SessionLocal
from ..models import Todos
from .auth import get_current_user

router = APIRouter(
    prefix='/api/todos',
    tags=['Todos']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodosRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=1, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'A new Todo',
                'description': 'Created by Tanuj',
                'priority': 5,
                'complete': False,
            }
        }


@router.get("/v1", status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency, db: db_dependency):
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get("/v1/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=404, detail='Todos not found')


@router.post("/v1", status_code=status.HTTP_201_CREATED)
async def add_to_todos(user: user_dependency, db: db_dependency, new_todo: TodosRequest):
    db.add(Todos(**new_todo.dict(), owner_id=user.get('id')))
    db.commit()


@router.put("/v1/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_to_todos(user: user_dependency, db: db_dependency, updated_todo: TodosRequest, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    todo_model.title = updated_todo.title
    todo_model.description = updated_todo.description
    todo_model.complete = updated_todo.complete
    todo_model.priority = updated_todo.priority
    db.add(todo_model)
    db.commit()


@router.delete("/v1/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_to_todos(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()
    db.commit()
