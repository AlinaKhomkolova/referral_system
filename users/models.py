import random
import string

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from referral_system.settings import NULLABLE


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Телефон обязателен')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        user = self.create_user(phone, password, **extra_fields)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    phone = PhoneNumberField(
        region='RU',
        unique=True,
        verbose_name='Номер телефона'
    )
    verification_code = models.CharField(
        max_length=4,
        **NULLABLE,
        verbose_name='Код подтверждения'
    )
    code_expires_at = models.DateTimeField(
        **NULLABLE,
        verbose_name='Время истечения кода'
    )
    invite_code = models.CharField(
        max_length=6,
        unique=True,
        **NULLABLE,
        verbose_name='Инвайт-код пользователя'
    )
    activated_invite_code = models.CharField(
        max_length=6,
        **NULLABLE,
        verbose_name='Активированный инвайт-код'
    )
    invited_by = models.ForeignKey(
        'self',
        **NULLABLE,
        on_delete=models.SET_NULL,
        related_name='invited_users',
        verbose_name='Приглашенные пользователи'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания пользователя"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.phone)

    def generate_invite_code(self):
        while True:
            code = ''.join(random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            ))
            if not User.objects.filter(invite_code=code).exists():
                return code

    @property
    def invited_users(self):
        return User.objects.filter(invited_by=self)

    def save(self, *args, **kwargs):
        # Генерация инвайт кода при первой авторизации
        if not self.invite_code and self.pk:
            self.invite_code = self.generate_invite_code()
        super().save(*args, **kwargs)
