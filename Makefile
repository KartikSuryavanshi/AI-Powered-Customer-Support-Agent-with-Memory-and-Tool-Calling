install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

bootstrap:
	python scripts/bootstrap_data.py

run-api:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

run-ui:
	streamlit run app.py --server.port 8501

test:
	pytest

docker-up:
	docker compose up --build

docker-down:
	docker compose down
