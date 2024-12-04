from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, Application
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
import os
from dotenv import load_dotenv
from django.urls import reverse

load_dotenv()

User = get_user_model()


async def start(update: Update, context):
    token = context.args[0] if context.args else None

    if not token:
        await update.message.reply_text("Токен не указан!")
        return

    try:
        user, created = await sync_to_async(User.objects.get_or_create)(
            token=token,
            defaults={
                "telegram_chat_id": update.message.chat_id,
                "first_name": update.message.chat.first_name,
                "last_name": update.message.chat.last_name,
                "username": update.message.chat.username,
            },
        )

        if not created:
            # Если пользователь уже существует, обновляем данные
            user.telegram_chat_id = update.message.chat_id
            user.first_name = update.message.chat.first_name
            user.last_name = update.message.chat.last_name
            user.username = update.message.chat.username
            await sync_to_async(user.save)()

        # Генерируем ссылку для входа на сайт
        site_url = os.getenv("SITE_URL")
        login_url = f"{site_url}{reverse('users:login')}?chat_id={user.telegram_chat_id}"

        # Отправляем сообщение с кнопкой для входа на сайт
        keyboard = [
            [InlineKeyboardButton("Войти на сайт", url=login_url)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Вы успешно авторизовались! Перейдите на сайт для завершения.",
            reply_markup=reply_markup,
        )
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")


async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("auth:"):
        token = query.data.split(":")[1]
        try:
            user = await sync_to_async(User.objects.get)(token=token)

            # Генерация ссылки для возврата на сайт
            site_url = os.getenv("SITE_URL")
            profile_url = f"{site_url}{reverse('profile')}"

            await query.edit_message_text(
                f"Вы успешно авторизовались. [Вернуться на сайт]({profile_url})",
                parse_mode="Markdown",
            )
        except User.DoesNotExist:
            await query.edit_message_text("Ошибка: Пользователь не найден.")
    elif query.data == "cancel":
        await query.edit_message_text("Авторизация отменена.")


def run_telegram_bot():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN не задан в .env файле")

    application = Application.builder().token(bot_token).build()

    # Обработчики команд и кнопок
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    application.run_polling()