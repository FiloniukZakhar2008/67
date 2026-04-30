FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry

# Копіюємо конфіги poetry
COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . /app/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]