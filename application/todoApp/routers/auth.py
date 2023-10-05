from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from enum import Enum
from datetime import timedelta, datetime
from ..database import SessionLocal
from ..models import Users


router = APIRouter(
    prefix='/api/auth',
    tags=['Auth']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/api/auth/v1/token')

SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05j2a23c2fa12702fe3'
ALGORITHM = 'HS256'


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class UserRole(Enum):
    ADMIN = 0
    USER = 1


class UserRequest(BaseModel):
    email: str = Field(min_length=3, max_length=100)
    username: str = Field(min_length=3, max_length=100)
    first_name: str = Field(min_length=3, max_length=100)
    last_name: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=3, max_length=100)
    role: UserRole

    class Config:
        json_schema_extra = {
            'example': {
                'email': 'rohan@gmail.com',
                'username': 'rohan.last',
                'first_name': 'Rohan',
                'last_name': 'Last',
                'password': 'paffworld',
                'role': UserRole.USER,
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/v1", status_code=status.HTTP_201_CREATED)
async def add_user(db: db_dependency, user_details: UserRequest):
    user_model = Users(
        email=user_details.email,
        username=user_details.username,
        first_name=user_details.first_name,
        last_name=user_details.last_name,
        hashed_password=bcrypt_context.hash(user_details.password),
        role=user_details.role.name,
    )
    db.add(user_model)
    db.commit()


@router.get("/v1", status_code=status.HTTP_200_OK)
async def get_all_users(db: db_dependency):
    return db.query(Users).all()


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user, Token expired.')


@router.post("/v1/token", response_model=Token)
async def get_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=1))

    return {'access_token': token, 'token_type': 'bearer'}
