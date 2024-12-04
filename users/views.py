from django.shortcuts import render, redirect
import uuid
import os
from users.models import User
from django.contrib.auth import login
from dotenv import load_dotenv

load_dotenv()



def home_view(request):
    # Если пользователь авторизован, отображаем главную страницу с именем пользователя
    if request.user.is_authenticated:
        return render(request, "home.html", {"user": request.user})

    # Если пользователь не авторизован, отображаем кнопку для авторизации
    bot_username = os.getenv("TELEGRAM_BOT_USERNAME")
    token = str(uuid.uuid4())
    request.session["login_token"] = token
    telegram_url = f"https://t.me/{bot_username}?start={token}"
    return render(request, "home.html", {"telegram_url": telegram_url})

def login_view(request):
    telegram_chat_id = request.GET.get("chat_id")
    if not telegram_chat_id:
        return redirect("users:home")  # Перенаправляем на главную по имени маршрута

    try:
        # Проверяем пользователя по telegram_chat_id
        user = User.objects.get(telegram_chat_id=telegram_chat_id)
        login(request, user)  # Авторизуем пользователя
        return redirect("users:home")  # Перенаправляем на страницу профиля
    except User.DoesNotExist:
        return redirect("users:home")  # Если пользователь не найден, на главную