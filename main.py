import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from smart_home import control_device
from secrets import TELEGRAM_TOKEN, SMART_HOME_PASSWORD
from functions import (
    my_timer, time_kem, prank, what_weather, what_dey,
    print_heart, currency, calculation_materials
)
from timer_manager import add_timer
import config
import asyncio


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Словарь для хранения авторизованных пользователей
authorized_users = {}

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


def process_command_text(text: str, bot=None, chat_id=None, user_id=None, loop=None) -> str:
    """Обрабатывает текст команды и возвращает результат (без микрофона)"""
    text_lower = text.lower()
    text_split = text_lower.split(" ")

    # Управление устройствами
    if text_split[0] in ["включи", "выключи"] and len(text_split) > 1:
        device = " ".join(text_split[1:])
        action = text_split[0]
        return control_device(device, action)

    # Обработка команды "рассчитай"
    if text_split[0] == "рассчитай" and len(text_split) >= 2:
        mat = text_split[1]  # "стяжку" или "наливной"
        # Всё остальное — это входные данные
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
            message = my_timer(time_value, time_unit)
            if bot and chat_id and user_id and loop:
                add_timer(user_id, seconds, "Время вышло! ⏰", bot, chat_id, loop)
            return message

        elif time_unit in config.HOUR_FORMATS:
            seconds = int(time_value) * 60 * 60
            message = my_timer(time_value, time_unit)
            if bot and chat_id and user_id and loop:
                add_timer(user_id, seconds, "Время вышло! ⏰", bot, chat_id, loop)
            return message

        elif time_unit in config.SECOND_FORMATS:
            seconds = int(time_value)
            if seconds < 10:
                return f"❌ Минимум 10 секунд."
            message = my_timer(time_value, time_unit)
            if bot and chat_id and user_id and loop:
                add_timer(user_id, seconds, "Время вышло! ⏰", bot, chat_id, loop)
            return message
        else:
            return f"❌ Неизвестный формат: {time_unit}"

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
        "- курс доллар\евро\n"
        "- таймер 1 минута\n"
        "- расскажи анекдот\n"
        "- сколько время\n"
        "- какой сегодня день\n"
        "- включи\выключи свет в комнате\n"
        "- рассчитай стяжку\наливной 'площадь м*2' 'толщина см'\n"
        "*пример: рассчитай стяжку 40 2.5\n"
        "- сердце 1\n\n"
        "И я отвечу!"
    )


async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Начинает процесс авторизации для управления умным домом"""
    context.user_data['awaiting_auth'] = True
    await update.message.reply_text(
        "🔐 Введите пароль для управления умным домом:"
    )


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
    """Обрабатывает текстовые сообщения"""
    user_text = update.message.text
    user_id = update.effective_user.id

    # Если ожидаем авторизацию
    if context.user_data.get('awaiting_auth'):
        await handle_auth(update, context)
        return

    logger.info(f"Пользователь {user_id}: {user_text}")

    # Проверяем, относится ли команда к умному дому
    is_smart_home_command = any(trigger in user_text.lower() for trigger in ["включи", "выключи"])

    if is_smart_home_command and not authorized_users.get(user_id):
        await update.message.reply_text(
            "🔒 Управление умным домом требует авторизации.\n"
            "Используйте команду /auth для ввода пароля."
        )
        return

    response = process_command_text(
        user_text,
        bot=context.bot,
        chat_id=update.effective_chat.id,
        user_id=user_id,
        loop=asyncio.get_running_loop()
    )
    await update.message.reply_text(response)


def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("auth", auth))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == '__main__':
    main()