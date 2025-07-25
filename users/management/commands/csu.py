import sys

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает суперпользователя с автоматическим паролем'

    def handle(self, *args, **options):
        try:
            user = User.objects.create_superuser(
                phone='+79123456789',
                password='1234'
            )
            self.stdout.write(self.style.SUCCESS(f'Создан суперпользователь:'))
            self.stdout.write(f'Телефон: {user.phone}')
            self.stdout.write(f'Пароль: {user.password}')
            self.stdout.write(f'Инвайт-код: {user.invite_code}')
        except Exception as e:
            self.stderr.write(f'Ошибка: {e}')
            sys.exit(1)
