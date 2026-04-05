import threading
import asyncio
from datetime import datetime, timedelta

user_tasks = {}


def add_timer(user_id: int, seconds: int, message: str, bot, chat_id: int, loop: asyncio.AbstractEventLoop):
    """Добавляет таймер для пользователя"""
    if user_id not in user_tasks:
        user_tasks[user_id] = []

    task = {
        "end_time": datetime.now() + timedelta(seconds=seconds),
        "message": message,
        "bot": bot,
        "chat_id": chat_id,
        "loop": loop
    }
    user_tasks[user_id].append(task)

    # Запускаем проверку в отдельном потоке
    threading.Thread(target=_check_timer, args=(user_id, task), daemon=True).start()


def _check_timer(user_id: int, task: dict):
    """Проверяет, не пора ли отправить сообщение"""
    wait_seconds = (task["end_time"] - datetime.now()).total_seconds()
    if wait_seconds > 0:
        import time
        time.sleep(wait_seconds)

    # Отправляем сообщение через главный event loop
    try:
        asyncio.run_coroutine_threadsafe(
            task["bot"].send_message(chat_id=task["chat_id"], text=f"⏰ {task['message']}"),
            task["loop"]
        )
    except Exception as e:
        print(f"Ошибка отправки: {e}")

    # Удаляем задачу из списка
    if user_id in user_tasks:
        try:
            user_tasks[user_id].remove(task)
        except ValueError:
            pass