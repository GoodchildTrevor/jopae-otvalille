FROM python:3.12-slim

COPY . .
ENV PYTHONPATH=/app

RUN pip install --no-cache-dir -e .  # или без установки, если не нужно

RUN touch subscriptions.db

CMD ["python", "python_scripts/jopae_tg_bot.py"]
