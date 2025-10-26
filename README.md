# Jopae otvalille

Начало работы
-----------

1. **Создайте ТГ-бота** `@BotFather <https://t.me/BotFather>` и получите персональный токен.
2. **Настройте переменные окружения**:

   ```bash
    touch .env
    nano .env
    OPEN_WEATHER = ***
    AMBEE = ***

    JOPAE_BOT = ***

    TIMEZONE = ***

    LAT =  ***
    LON =  ***
    ```
3. **Запустите контейнер**:
    ```bash
    docker compose up --d --build
   ```

Использование
-------------

**Команды бота:**

- `/start` - Подписаться на ежедневные сообщения
- `/stop` - Отписаться от рассылки
- `/help` - Показать справку по командам
- `/test` - Отправить тестовое сообщение

* Free software: MIT license

Features
--------

* TODO
*
