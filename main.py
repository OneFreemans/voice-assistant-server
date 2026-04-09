import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from smart_home import control_device
from config_secrets import TELEGRAM_TOKEN, SMART_HOME_PASSWORD, DEEPSEEK_API_KEY
from functions import (
    my_timer, time_kem, prank, what_weather, what_dey,
    print_heart, currency, calculation_materials
)
import config
import aiohttp
import asyncio
import json
from datetime import datetime


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Словарь для хранения авторизованных пользователей
authorized_users = {}


# Файл для статистики
STATS_FILE = "/tmp/stats.json"


def update_stats():
    """Обновляет статистику сообщений"""
    stats = {"total_messages": 0, "last_message_time": None}
    try:
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
    except:
        pass
    stats["total_messages"] += 1
    stats["last_message_time"] = datetime.now().isoformat()
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)


# словарь для хранения команд
COMMANDS = {
    "таймер": (my_timer, 2, True),
    "сколько время": (time_kem, 0, False),
    "расскажи анекдот": (prank, 0, False),
    "погода": (what_weather, 0, False),
    "курс": (currency, 1, False),
    "какой сегодня день": (what_dey, 0, False),
    "сердце": (print_heart, 1, False),
    "включи": (control_device, 1, False),
    "выключи": (control_device, 1, False),
    "рассчитай": (calculation_materials, 1, False),
}


async def get_ai_response(user_message: str) -> str:
    """Отправляет запрос к DeepSeek API и возвращает ответ."""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты — полезный, вежливый и дружелюбный ассистент по имени Олег. Отвечай на русском языке."},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                else:
                    error_text = await response.text()
                    logger.error(f"DeepSeek API error: {response.status} - {error_text}")
                    return "❌ Извини, я не могу ответить сейчас. Попробуй позже."
    except Exception as e:
        logger.error(f"DeepSeek connection error: {e}")
        return "❌ Не удалось подключиться к нейросети. Проверь интернет или API-ключ."


def process_command_text(text: str, update: Update = None, context: ContextTypes.DEFAULT_TYPE = None) -> str:
    """Обрабатывает текст команды и возвращает результат"""
    text_lower = text.lower()
    text_split = text_lower.split(" ")

    # Управление устройствами
    if text_split[0] in ["включи", "выключи"] and len(text_split) > 1:
        device = " ".join(text_split[1:])
        action = text_split[0]
        return control_device(device, action)

    # Обработка команды "рассчитай"
    if text_split[0] == "рассчитай" and len(text_split) >= 2:
        mat = text_split[1]
        input_text = " ".join(text_split[2:]) if len(text_split) > 2 else ""
        if not input_text:
            return "❌ Укажите параметры. Пример: рассчитай стяжку площадь 25 слой 5"
        return calculation_materials(mat, input_text)

    # Обработка таймера
    if text_split[0] == "таймер" and len(text_split) >= 3:
        time_value = text_split[1]
        time_unit = text_split[2]

        if time_unit in config.MINUTE_FORMATS:
            seconds = int(time_value) * 60

        elif time_unit in config.HOUR_FORMATS:
            seconds = int(time_value) * 60 * 60

        elif time_unit in config.SECOND_FORMATS:
            seconds = int(time_value)

            if seconds < 10:
                return f"❌ Минимум 10 секунд."

        else:
            return f"❌ Неизвестный формат: {time_unit}"

        message = my_timer(time_value, time_unit)

        # Запускаем таймер в фоне
        if update and context:
            async def timer_coro():
                await asyncio.sleep(seconds)
                await context.bot.send_message(chat_id=update.effective_chat.id, text="⏰ Время вышло! ⏰")

            asyncio.create_task(timer_coro())

        return message

    # Команды с пробелами
    if text_lower in COMMANDS:
        func, min_args, need_timer = COMMANDS[text_lower]
        return func()

    # Обычные команды с аргументами
    trigger = text_split[0]
    if trigger in COMMANDS:
        func, min_args, need_timer = COMMANDS[trigger]

        if len(text_split) > min_args:
            if min_args == 1:
                return func(text_split[1])

            elif min_args == 2:
                return func(text_split[1], text_split[2])

            else:
                return func()

    return f"Я не знаю команду - {text_lower}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение при команде /start"""
    await update.message.reply_text(
        "👋 Привет! Я ассистент Олег.\n\n"
        "📝 Отправь мне команду, например:\n\n"
        "- погода\n"
        "- курс доллар\\евро\n"
        "- таймер 1 минута\n"
        "- расскажи анекдот\n"
        "- сколько время\n"
        "- какой сегодня день\n"
        "- включи\\выключи свет в комнате\n"
        "- рассчитай стяжку\\наливной 'площадь м²' 'толщина см'\n"
        "*пример: рассчитай стяжку 40 2.5\n"
        "- сердце 1\n\n"
        "*Так же можете пообщаться с мной на любые темы"
    )


async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Начинает процесс авторизации для управления умным домом"""
    context.user_data['awaiting_auth'] = True
    await update.message.reply_text("🔐 Введите пароль для управления умным домом:")


async def handle_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Проверяет пароль и авторизует пользователя"""
    user_id = update.effective_user.id
    password = update.message.text

    if password == SMART_HOME_PASSWORD:
        authorized_users[user_id] = True
        await update.message.reply_text("✅ Доступ к умному дому разрешён.")

    else:
        await update.message.reply_text("❌ Неверный пароль.")

    context.user_data['awaiting_auth'] = False


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    user_id = update.effective_user.id

    # Проверка на авторизацию для умного дома
    if context.user_data.get('awaiting_auth'):
        await handle_auth(update, context)
        return

    # Проверка, является ли сообщение командой из COMMANDS
    is_known_command = False
    for cmd in COMMANDS.keys():
        if user_text.lower().startswith(cmd):
            is_known_command = True
            break

    # Обновляем статистику
    update_stats()
    logger.info(f"Пользователь {user_id}: {user_text}")

    # Если это команда умного дома и пользователь НЕ авторизован
    if any(trigger in user_text.lower() for trigger in ["включи", "выключи"]):
        if not authorized_users.get(user_id):
            await update.message.reply_text("🔒 Управление умным домом требует авторизации.\nИспользуйте команду /auth.")
            return
        response = process_command_text(user_text, update, context)
        await update.message.reply_text(response)

    # Если это известная команда (погода, курс и т.д.)
    elif is_known_command:
        response = process_command_text(user_text, update, context)
        await update.message.reply_text(response)

    # Если это просто сообщение (болталка)
    else:
        await update.message.chat.send_action(action="typing")
        ai_response = await get_ai_response(user_text)
        await update.message.reply_text(ai_response)


def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("auth", auth))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == '__main__':
    main()