from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.adapter import get_database_sync_adapter
from app.http.api.auth import auth_rout
from app.http.api.chat import chat_rout
from app.http.api.user import users_rout
from app.http.api.websocket import ws_rout


@asynccontextmanager
async def lifespan(app: FastAPI):
    adapter = get_database_sync_adapter()
    await adapter.init_data()
    yield


app = FastAPI(title='WS Chat Zero Two', lifespan=lifespan)

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

app.mount('/', StaticFiles(directory='dist', html=True), name='frontend')
