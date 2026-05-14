FROM python:3.11

WORKDIR /app

# Спочатку копіюємо лише файли залежностей (це прискорює збірку)
COPY pyproject.toml poetry.lock ./

# Встановлюємо poetry та залежності
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# КРИТИЧНИЙ КРОК: Копіюємо ВЕСЬ інший код проекту в контейнер
COPY . .

# Команда запуску (переконайся, що main.py лежить у корені папки 67)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]