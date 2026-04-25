# 1. Используем ту версию, которая указана в проекте
FROM python:3.12-slim

# 2. Копируем uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 3. Системные зависимости (OpenCV + Postgres)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 4. Копируем только файлы зависимостей
COPY pyproject.toml uv.lock ./

# 5. Устанавливаем зависимости
# Используем флаг --system, чтобы uv не создавал .venv внутри контейнера
RUN uv sync --system --no-install-project --no-cache

# 6. Копируем остальной код
COPY . .

# Создаем папку для загрузок
RUN mkdir -p /app/uploads

# Указываем пути
ENV PYTHONPATH=/app/src
ENV UV_SYSTEM_PYTHON=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
