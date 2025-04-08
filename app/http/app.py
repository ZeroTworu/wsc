from fastapi import FastAPI

from app.http.api.auth import auth_rout

origins = [
    'http://localhost',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://127.0.0.1',
]

app = FastAPI(title='WS Chat Zero Two')

app.include_router(auth_rout)
