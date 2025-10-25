import sqlite3
from python_scripts.config.consts import DB_PATH


def init_db() -> None:
    """
    Инициализирует базу данных SQLite и создает таблицу 'subscribers', если она не существует.
    Таблица содержит:
        - chat_id (INTEGER PRIMARY KEY): уникальный идентификатор чата Telegram
        - subscribed_at (TIMESTAMP): время подписки, по умолчанию CURRENT_TIMESTAMP
    Raises:
        sqlite3.Error: если произошла ошибка базы данных при подключении или создании таблицы
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                chat_id INTEGER PRIMARY KEY,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Failed to initialize database or create 'subscribers' table: {e}") from e
    finally:
        if conn:
            conn.close()


def add_subscriber(chat_id: int) -> None:
    """
    Добавляет нового подписчика в базу данных.
    Операция идемпотентна благодаря ограничению PRIMARY KEY и использованию
    INSERT OR IGNORE - дублирующиеся chat_id игнорируются.
    Args:
        chat_id: уникальный идентификатор чата Telegram
    Raises:
        TypeError: если chat_id не является целым числом
        sqlite3.Error: если произошла ошибка базы данных при вставке
    """
    if not isinstance(chat_id, int):
        raise TypeError(f"Expected chat_id to be int, got {type(chat_id).__name__}")

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO subscribers (chat_id) VALUES (?)", (chat_id,))
        conn.commit()
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Failed to add subscriber with chat_id={chat_id}: {e}") from e
    finally:
        if conn:
            conn.close()


def get_all_subscribers() -> list[int]:
    """
    Получает список всех идентификаторов чатов подписчиков из базы данных.
    Returns:
        list[int]: список уникальных идентификаторов чатов Telegram текущих подписчиков
    Raises:
        sqlite3.Error: если произошла ошибка базы данных при выполнении запроса
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM subscribers")
        chat_ids = [row[0] for row in cursor.fetchall()]
        return chat_ids
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Failed to fetch subscribers from database: {e}") from e
    finally:
        if conn:
            conn.close()


def remove_subscriber(chat_id: int) -> None:
    """
    Удаляет подписчика из базы данных.
    Args:
        chat_id: идентификатор чата Telegram для отписки
    Raises:
        sqlite3.Error: если произошла ошибка базы данных при удалении
    """
    if not isinstance(chat_id, int):
        raise TypeError(f"Expected chat_id to be int, got {type(chat_id).__name__}")

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subscribers WHERE chat_id = ?", (chat_id,))
        conn.commit()
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Failed to remove subscriber with chat_id={chat_id}: {e}") from e
    finally:
        if conn:
            conn.close()
