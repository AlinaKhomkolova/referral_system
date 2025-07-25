import random
import time

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    SendCodeSerializer,
    VerifyCodeSerializer,
    ProfileSerializer,
    SetInviteSerializer
)


class SendVerificationCodeView(generics.CreateAPIView):
    """Отправка кода подтверждения"""
    serializer_class = SendCodeSerializer
    throttle_classes = [UserRateThrottle]

    @swagger_auto_schema(
        request_body=SendCodeSerializer,
        responses={
            200: 'Код отправлен',
            400: 'Ошибка валидации'
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Имитация задержки 1-2 секунды
        time.sleep(random.uniform(1, 2))

        phone = serializer.validated_data['phone']
        user, created = User.objects.get_or_create(phone=phone)

        # Генерация кода подтверждения
        if not user.verification_code or user.code_expires_at < timezone.now():
            user.verification_code = f"{random.randint(1000, 9999)}"
            user.code_expires_at = timezone.now() + timezone.timedelta(minutes=2)
            user.save(update_fields=['verification_code', 'code_expires_at'])

        # Имитация отправки смс
        print(f'\n\n----- Новый пользователь создан -----\n'
              f'Номер телефона: {user.phone}\n'
              f'Инвайт-код: {user.invite_code}\n'
              f'Код подтверждения: {user.verification_code}\n'
              f'Время истечения кода: {user.code_expires_at}\n'
              f'--------------------------------------\n\n'
              )
        user.save()

        return Response({
            'message': f'Код отправлен по номеру: {phone}'
        }, status=status.HTTP_200_OK)


class VerifyCodeView(generics.CreateAPIView):
    """Верификация кода"""
    serializer_class = VerifyCodeSerializer

    @swagger_auto_schema(
        request_body=VerifyCodeSerializer,
        responses={
            200: 'Успешная верификация',
            400: 'Ошибка валидации/неправильный код',
            404: 'Пользователь не найден'
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        # Проверка кода и времени
        if (user.verification_code == code
                and user.code_expires_at > timezone.now()):

            # Генерация инвайт кода при первой авторизации
            if not user.invite_code:
                user.invite_code = user.generate_invite_code()
                user.save()

            # Генерация токенов
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": ProfileSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Неверный код или истек срок действия'}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveAPIView):
    """Получение профиля"""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        responses={
            200: 'Данные профиля',
            401: 'Не авторизован'
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class SetInviteCodeView(generics.UpdateAPIView):
    """Активация инвайт-кода"""
    serializer_class = SetInviteSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    http_method_names = ['put']

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        request_body=SetInviteSerializer,
        responses={
            200: 'Инвайт-код активирован',
            400: 'Ошибка валидации/код уже активирован',
            404: 'Инвайт-код не существует'
        }
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        invite_code = serializer.validated_data['invite_code']

        try:
            inviter = User.objects.get(invite_code=invite_code)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'invite_code': ['Инвайт код не существует']})

        user = self.get_object()
        if user.activated_invite_code:
            raise serializers.ValidationError({'invite_code': ['Инвайт код уже активирован']})

        user.activated_invite_code = invite_code
        user.invited_by = inviter
        user.save()

        return Response({
            'status': 'success',
            'activated_invite_code': invite_code
        }, status=200)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({
            'status': 'Код успешно активирован',
            'activated_invite_code': self.get_object().activated_invite_code
        }, status=status.HTTP_200_OK)
