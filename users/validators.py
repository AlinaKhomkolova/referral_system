from phonenumbers import NumberParseException
from phonenumbers import parse as parse_number, is_valid_number

from rest_framework.exceptions import ValidationError


def validate_phone(value):
    """Валидация телефона через phonenumbers"""
    if not value:
        return

    try:
        number = value.as_e164

        if not number.startswith('+7'):
            raise ValidationError({"phone": ["Номер должен быть российским (+7)."]})

        # Парсинг и проверка валидности
        parsed = parse_number(number)
        if not is_valid_number(parsed):
            raise ValidationError({"phone": ["Неверный формат номера."]})

        national_number = parsed.national_number

        if str(national_number)[0] != '9':
            raise ValidationError(
                {"phone": ["Неверный формат номера."]}
            )

    except NumberParseException:
        raise ValidationError({"phone": ["Не удалось распознать номер."]})
