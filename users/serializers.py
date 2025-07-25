from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from .models import User
from .validators import validate_phone


class SendCodeSerializer(serializers.Serializer):
    """Отправка кода подтверждения"""
    phone = PhoneNumberField()

    class Meta:
        model = User
        fields = ['phone', ]

    def validate(self, attrs):
        phone = attrs.get('phone')

        # Валидация номера телефона
        if phone:
            validate_phone(phone)
        return attrs


class VerifyCodeSerializer(serializers.Serializer):
    """Верификация кода"""
    phone = PhoneNumberField()
    code = serializers.CharField(max_length=4)


class ProfileSerializer(serializers.ModelSerializer):
    """Профиль пользователя"""
    invited_users = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'phone', 'invite_code',
            'activated_invite_code', 'invited_users'
        ]

    def to_representation(self, instance):
        """преобразование PhoneNumber в строку"""
        data = super().to_representation(instance)
        data['phone'] = str(instance.phone)
        return data

    def get_invited_users(self, obj):
        # Преобразование каждого номера телефона в строку
        return [str(user.phone) for user in obj.invited_users.all()]


class SetInviteSerializer(serializers.Serializer):
    """Активация инвайт-кода"""
    invite_code = serializers.CharField(max_length=6)

    def validate_invite_code(self, value):
        if not User.objects.filter(invite_code=value).exists():
            raise serializers.ValidationError('Инвайт-код не существует')
        return value
