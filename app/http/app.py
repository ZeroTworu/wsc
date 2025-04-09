from fastapi import FastAPI

from app.http.api.auth import auth_rout
from app.http.api.chat import chat_rout
from app.http.api.user import users_rout
from app.http.api.websocket import ws_rout
from fastapi.middleware.cors import CORSMiddleware

origins = [
    'http://localhost',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://127.0.0.1',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

app = FastAPI(title='WS Chat Zero Two')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_rout)
app.include_router(ws_rout)
app.include_router(users_rout)
app.include_router(chat_rout)
