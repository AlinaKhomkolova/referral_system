from django.urls import path

from .apps import UsersConfig
from .views import (
    SendVerificationCodeView,
    VerifyCodeView,
    ProfileView,
    SetInviteCodeView
)

User = UsersConfig.name

urlpatterns = [
    # отправка кода подтверждения
    path('auth/send-code/', SendVerificationCodeView.as_view()),
    # верификация кода и получение токена
    path('auth/verify/', VerifyCodeView.as_view()),
    # получение данных профиля
    path('profile/', ProfileView.as_view()),
    # активация чужого инвайт кода
    path('profile/set-invite/', SetInviteCodeView.as_view()),
]
