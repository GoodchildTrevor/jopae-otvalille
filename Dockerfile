FROM python:3.12-slim

WORKDIR /app

# Копируем pyproject.toml и сборочные файлы
COPY pyproject.toml ./

# Устанавливаем зависимости БЕЗ обновления pip
RUN pip install --no-cache-dir .

# Копируем весь код
COPY . .

# Создаём БД
RUN touch subscriptions.db

CMD ["python", "python_scripts/jopae_tg_bot.py"]
