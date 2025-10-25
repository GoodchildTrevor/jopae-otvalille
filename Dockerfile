FROM python:3.12-slim

# Рабочая директория - корень проекта
WORKDIR /app

# Копируем ВСЁ
COPY . .

# Ставим зависимости
RUN pip install --upgrade pip && pip install --no-cache-dir .

# Добавляем путь к Python чтобы видел python_scripts
ENV PYTHONPATH=/app

# Запускаем
CMD ["python", "python_scripts/jopae_tg_bot.py"]
