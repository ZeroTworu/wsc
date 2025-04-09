from fastapi import FastAPI

from app.http.api.auth import auth_rout
from app.http.api.chat import chat_rout
from app.http.api.user import users_rout
from app.http.api.websocket import ws_rout

origins = [
    'http://localhost',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://127.0.0.1',
]

app = FastAPI(title='WS Chat Zero Two')

app.include_router(auth_rout)
app.include_router(ws_rout)
app.include_router(users_rout)
app.include_router(chat_rout)
