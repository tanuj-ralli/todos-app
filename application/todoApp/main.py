from fastapi import FastAPI
from .database import engine, Base
from .routers import auth, todos, user

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(todos.router)
