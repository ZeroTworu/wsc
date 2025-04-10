from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.http.api.auth import auth_rout
from app.http.api.chat import chat_rout
from app.http.api.user import users_rout
from app.http.api.websocket import ws_rout

app = FastAPI(title='WS Chat Zero Two')

app.include_router(ws_rout)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_rout)
app.include_router(users_rout)
app.include_router(chat_rout)
