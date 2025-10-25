FROM python:3.12-slim

# Устанавливаем рабочую директорию в папку python_scripts
WORKDIR /app/python_scripts

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock* /app/

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip && pip install --no-cache-dir /app

# Копируем исходный код
COPY . /app

# Запускаем бота
CMD ["python", "jopae_tg_bot.py"]
