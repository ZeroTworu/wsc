.PHONY: lint isort infra app

lint:
	poetry run flake8 app/

isort:
	poetry run isort app/

infra:
	docker-compose -f docker/docker-compose.infra.yaml up --remove-orphans

app:
	uvicorn  app.http.app:app --reload