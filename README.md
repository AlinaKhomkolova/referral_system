# Phone Auth + Invite Code API

Этот проект реализует API для авторизации по номеру телефона и инвайт-системы. Пользователь проходит авторизацию,
получает уникальный инвайт-код и может активировать чужой код один раз. Также в профиле отображаются пользователи,
которых он пригласил.
___

### 📋 Содержание

1. [Функциональность](#функциональность)
2. [Стек технологий](#стек-технологий)
3. [Как развернуть проект](#как-развернуть-проект)
4. [Примеры API](#примеры-api)
5. [Тестирование через Postman](#тестирование-через-postman)
6. [Автор](#автор)

___

## Функциональность

- Авторизация по номеру телефона:
    - Этап 1: Ввод номера телефона.
    - Этап 2: Ввод кода авторизации (Код выводиться в консоль для имитации его отправления).
- Регистрация новых пользователей.
- Генерация случайного 6-значного инвайт-кода (цифры и символы).
- Возможность ввести чужой инвайт-код (один раз).
- Профиль пользователя:
    - Номер телефона.
    - Свой инвайт-код.
    - Введенный чужой инвайт-код (если был активирован).
    - Список пользователей, которые ввели код данного пользователя.

___

## Стек технологий

- Язык программирования: Python 3.12+
- Фреймворк: Django 5.2 + Django REST Framework (DRF)
- Авторизация: JWT (через djangorestframework-simplejwt)
- Документация API: drf-yasg (Swagger UI / ReDoc)
- Работа с номерами телефонов: django-phonenumber-field + phonenumbers
- Переменные окружения: python-dotenv
- База данных: PostgreSQL

___

## Как развернуть проект

### 1. Клонирование репозитория

```bash
git@github.com:AlinaKhomkolova/referral_system.git
cd referral_system
````

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Создание файла .env

Создайте файл .env на основе .env.sample и укажите необходимые параметры.

### 5. Создание супер пользователя

```bash
python manage.py csu
```

### 6. Применение миграций

```bash
python manage.py migrate
```

### 7. Запуск сервера

```bash
python manage.py runserver
```

___

## Примеры API

Вск запросы используют формат application/json

### Авторизация - этап 1 (Ввод номера)

#### POST api/auth/send-code/

```
{
  "phone": "+79123456789"
}
```

#### Ответ:

```
{
    "message": "Код отправлен по номеру: +79123456789"
}
```

### Авторизация - этап 2 (Ввод кода)

#### POST api/auth/verify/

```
{
  "phone": "+79123456789",
  "code": "1234"
}
```

#### Ответ:

```
{
    "user": {
        "id": 1,
        "phone": "+79123456789",
        "invite_code": "Z2MRHB",
        "activated_invite_code": null,
        "invited_users": []
    },
    "tokens": {
        "refresh": "Token",
        "access": "Token"
    }
}
```

### Получение профиля

#### GET api/profile/

Заголовок: Authorization: Bearer 'token'

#### Ответ:

```
{
    "id": 1,
    "phone": "+79123456789",
    "invite_code": "Z2MRHB",
    "activated_invite_code": null,
    "invited_users": [
    ]
}
```

### Активация инвайт-кода

#### PUT api/profile/set-invite/

Заголовок: Authorization: Bearer 'token'

```
{
  "invite_code": "D2MZJN"
}
```

#### Ответ:

```
{
    "status": "Код успешно активирован",
    "activated_invite_code": "D2MZJN"
}
```

___

## Тестирование через Postman

В репозитории лежит файл, который содержит коллекцию запросов для тестирования:
Postman/referral.postman_collection.json

Импортируй его в Postman.

___

## Автор

**Alina Khomkolova**

Python backend developer