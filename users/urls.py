from django.urls import path

from .apps import UsersConfig
from .views import login_view, home_view

app_name = UsersConfig.name

urlpatterns = [
    path("", home_view, name="home"),  # Главная страница
    path("login/", login_view, name="login"),  # Логин
]