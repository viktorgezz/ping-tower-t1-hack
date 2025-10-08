from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start - показывает Telegram ID"""
    telegram_id = message.from_user.id
    user_name = message.from_user.full_name

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Получить мой ID 📋")]],
        resize_keyboard=True
    )

    await message.answer(
        f"👋 Добро пожаловать в PingTower, {user_name}!\n\n"
        f"Ваш Telegram ID: `{telegram_id}`\n\n"
        f"Перейдите на сайт PingTower, введите этот ID в разделе уведомлений, "
        f"и вы будете получать оповещения о статусе ваших ресурсов прямо здесь!\n\n"
        f"Этот ID уникален и постоянен для вашего аккаунта Telegram.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.message(lambda message: message.text == "Получить мой ID 📋")
async def get_id_again(message: types.Message):
    """Повторная отправка ID по кнопке"""
    telegram_id = message.from_user.id
    user_name = message.from_user.full_name

    await message.answer(
        f"👤 {user_name}, ваш Telegram ID: `{telegram_id}`\n\n"
        f"Используйте его на сайте PingTower для подключения уведомлений.",
        parse_mode="Markdown"
    )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Справка по использованию бота"""
    help_text = (
        "🤖 PingTower Bot - помощь\n\n"
        "Команды:\n"
        "/start - Получить ваш Telegram ID\n"
        "/help - Показать эту справку\n\n"
        "Как использовать:\n"
        "1. Нажмите /start чтобы узнать ваш ID\n"
        "2. Перейдите на сайт PingTower\n"
        "3. В разделе уведомлений введите ваш Telegram ID\n"
        "4. Готово! Вы будете получать уведомления\n\n"
        "Для поддержки: support@pingtower.ru"
    )
    await message.answer(help_text)


@router.message(Command("status"))
async def cmd_status(message: types.Message):
    """Проверка статуса бота"""
    await message.answer("✅ Бот работает исправно! Вы будете получать уведомления после привязки на сайте.")