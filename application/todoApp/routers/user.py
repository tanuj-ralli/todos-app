from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from passlib.context import CryptContext
from ..models import Users
from ..database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix='/api/user',
    tags=['User']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class PasswordUpdateRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


@router.get('/v1', status_code=status.HTTP_200_OK)
async def get_user_details(user: user_dependency, db: db_dependency):
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/v1/password/update", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, password_details: PasswordUpdateRequest):
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(password_details.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')
    user_model.hashed_password = bcrypt_context.hash(password_details.new_password)
    db.add(user_model)
    db.commit()
