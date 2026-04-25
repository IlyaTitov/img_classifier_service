# 1. Используем ту версию, которая указана в проекте
FROM python:3.12-slim

# 2. Копируем uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 3. Системные зависимости (Добавил build-essential для сборки библиотек)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. Настройки UV для работы без виртуального окружения
ENV UV_SYSTEM_PYTHON=1
ENV UV_LINK_MODE=copy
ENV PYTHONPATH=/app/src

# 5. Копируем только файлы зависимостей
COPY pyproject.toml uv.lock ./

# 6. Устанавливаем зависимости
# Убираем --no-install-project, если хотим, чтобы сам проект тоже "собрался" 
# Либо оставляем, если важны только библиотеки
RUN uv sync --no-cache


# 7. Копируем остальной код
COPY . .

# Создаем папку для загрузок
RUN mkdir -p /app/uploads

# Запуск приложения
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]


