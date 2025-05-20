FROM node:20 AS frontend

WORKDIR /app
COPY ui/ ./

RUN yarn install --frozen-lockfile

RUN yarn global add vite

ARG VITE_API_BASE_URL
ARG VITE_WS_URL

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_WS_URL=$VITE_WS_URL

RUN echo "VITE_API_BASE_URL=$VITE_API_BASE_URL" > .env && \
    echo "VITE_WS_URL=$VITE_WS_URL" >> .env

RUN yarn build-only

FROM python:3.13 AS backend

RUN pip3 install poetry

WORKDIR /ws
COPY migrations/ ./migrations

ADD poetry.lock ./poetry.lock
ADD pyproject.toml ./pyproject.toml
ADD alembic.ini ./alembic.ini

COPY app/ ./app

RUN poetry install --only main --no-root

COPY --from=frontend /app/dist/ /ws/dist
ENV ALEMBIC_COMMAND="alembic upgrade head"
ENV UVICORN_COMMAND="uvicorn app.http.app:app --host 0.0.0.0"
CMD ["sh", "-c", "poetry run $ALEMBIC_COMMAND && poetry run $UVICORN_COMMAND"]
EXPOSE 8000