FROM python:3.12-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы pyproject.toml и (если есть) poetry.lock
COPY pyproject.toml poetry.lock* /app/

# Обновляем pip и устанавливаем зависимости из pyproject.toml
RUN pip install --upgrade pip && pip install --no-cache-dir .

# Копируем оставшийся исходный код в рабочую директорию
COPY . /app

# Создаём файл БД, чтобы volume не сломался при первом запуске
RUN touch subscriptions.db

# Указываем команду запуска главного модуля
CMD ["python", "python_scripts/jopae_tg_bot.py"]
