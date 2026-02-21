
# 🏘️ Community Service

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-7-red?logo=redis)
![Kafka](https://img.shields.io/badge/Kafka-3.7-black?logo=apachekafka)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)

**Микросервис управления сообществами, участниками, контентом, подписками и донатами.**

</div>

---

## 📋 Оглавление

- [Обзор](#-обзор)
- [Возможности](#-возможности)
- [Быстрый старт](#-быстрый-старт)
- [Конфигурация](#-конфигурация)
- [Структура проекта](#-структура-проекта)
- [API Reference](#-api-reference)
- [Модели данных](#-модели-данных)
- [Event System](#-event-system)
- [Кэширование](#-кэширование)
- [Безопасность](#-безопасность)
- [Тестирование](#-тестирование)
- [Деплой и масштабирование](#-деплой-и-масштабирование)
- [Мониторинг](#-мониторинг)
- [FAQ](#-faq)

---

## 🔍 Обзор

Community Service — автономный REST API микросервис, отвечающий за полный жизненный
цикл сообществ в платформе. Stateless, горизонтально масштабируемый, event-driven.

### Схема инфраструктуры

```
                    ┌──────────────┐
                    │    Nginx     │ :80
                    │  (LB/Proxy) │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────┴─────┐ ┌───┴─────┐ ┌────┴────┐
        │  App :8000 │ │App :8000│ │App :8000│
        │ (Worker 1) │ │(Worker 2)│ │(Worker 3)│
        └──┬──┬──┬───┘ └──┬──┬───┘ └──┬──┬───┘
           │  │  │        │  │        │  │
     ┌─────┘  │  └────────┘  │  ┌─────┘  │
     │        │              │  │         │
┌────┴───┐ ┌──┴───┐    ┌────┴──┴┐   ┌────┴───┐
│Postgres│ │Redis │    │ Kafka  │   │ MinIO  │
│  :5432 │ │:6379 │    │ :9092  │   │ :9000  │
└────────┘ └──────┘    └────────┘   └────────┘
```

---

## ✨ Возможности

| Модуль | Описание |
|---|---|
| **Сообщества** | CRUD, поиск, публичные / приватные / ограниченные |
| **Участники** | Вступление, выход, бан, мут, назначение ролей |
| **Роли и права** | Гибкая RBAC-система с массивом разрешений |
| **Посты** | Публикация, модерация, закрепление, медиа |
| **Каналы** | Тематические каналы внутри сообщества |
| **События** | Мероприятия с расписанием |
| **Подписки** | Уровни подписки с тарификацией |
| **Донаты** | Приём пожертвований |
| **Аналитика** | Дашборд по сообществу, постам, участникам |

---

## 🚀 Быстрый старт

### Вариант 1 — Docker (рекомендуется)

```bash
# Сгенерировать проект
python generate_project.py

cd community-service

# Поднять всё
docker-compose up --build -d

# Проверить
curl http://localhost:8000/health
```

Swagger UI доступен по адресу `http://localhost:8000/api/docs` (при `DEBUG=true`).

### Вариант 2 — Локальная разработка

```bash
cd community-service

python -m venv venv
source venv/bin/activate        # Linux / Mac
# venv\Scripts\activate         # Windows

pip install -r requirements.txt

# Поднять БД и Redis
docker-compose up -d postgres redis

# Миграции
alembic revision --autogenerate -m "initial"
alembic upgrade head

# Запуск
python main.py
```

---

## ⚙️ Конфигурация

Все параметры читаются из `.env`. Шаблон — `.env.example`.

### Application

| Переменная | По умолчанию | Описание |
|---|---|---|
| `APP_NAME` | community-service | Имя сервиса |
| `APP_PORT` | 8000 | Порт |
| `DEBUG` | false | Включает Swagger |
| `WORKERS_COUNT` | 4 | Gunicorn workers |

### PostgreSQL

| Переменная | По умолчанию | Описание |
|---|---|---|
| `DATABASE_URL` | postgresql+asyncpg://... | Connection string |
| `DB_POOL_SIZE` | 20 | Размер пула |
| `DB_MAX_OVERFLOW` | 10 | Доп. соединения |

### Redis

| Переменная | По умолчанию | Описание |
|---|---|---|
| `REDIS_URL` | redis://localhost:6379/0 | Connection string |
| `CACHE_DEFAULT_TTL` | 300 | TTL по умолчанию, сек |
| `CACHE_ANALYTICS_TTL` | 600 | TTL аналитики, сек |

### JWT

| Переменная | По умолчанию | Описание |
|---|---|---|
| `JWT_SECRET_KEY` | change-me | Секрет подписи |
| `JWT_ALGORITHM` | HS256 | Алгоритм |

### Event Broker

| Переменная | По умолчанию | Описание |
|---|---|---|
| `EVENT_BROKER_TYPE` | kafka | `kafka` или `rabbitmq` |
| `KAFKA_BOOTSTRAP_SERVERS` | localhost:9092 | Серверы Kafka |
| `RABBITMQ_URL` | amqp://guest:guest@... | URL RabbitMQ |

### S3 / MinIO

| Переменная | По умолчанию | Описание |
|---|---|---|
| `S3_ENDPOINT` | http://localhost:9000 | Endpoint |
| `S3_ACCESS_KEY` | minioadmin | Ключ доступа |
| `S3_SECRET_KEY` | minioadmin | Секретный ключ |
| `S3_BUCKET` | community-media | Бакет |

---

## 📁 Структура проекта

```
community-service/
├── main.py                        # Точка входа
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── .env / .env.example
│
├── app/
│   ├── core/                      # Конфиг, JWT, RBAC, ошибки, логи
│   ├── domain/                    # SQLAlchemy-модели, enums
│   ├── schemas/                   # Pydantic DTO (request / response)
│   ├── repositories/              # Доступ к данным (базовый CRUD + специализация)
│   ├── services/                  # Бизнес-логика
│   ├── api/                       # Роутеры, middleware, dependencies
│   │   └── v1/                    # Версия API
│   ├── events/                    # Event publishing (Kafka / RabbitMQ)
│   ├── infrastructure/            # Redis, S3, DI-контейнер
│   └── db/                        # AsyncEngine, SessionFactory
│
├── migrations/                    # Alembic
├── docker/                        # entrypoint.sh, nginx.conf
└── tests/
```

---

## 📡 API Reference

**Base URL:** `http://localhost:8000/api/v1`

### Аутентификация

Защищённые endpoints требуют заголовок:

```
Authorization: Bearer <jwt_token>
```

JWT payload:

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "roles": ["admin"],
  "permissions": ["community.create", "post.create"],
  "is_superadmin": false
}
```

### Communities

| Метод | Путь | Описание | Auth |
|---|---|---|---|
| `GET` | `/communities` | Список (поиск, пагинация) | — |
| `GET` | `/communities/{id}` | Получить | — |
| `POST` | `/communities` | Создать | ✅ |
| `PUT` | `/communities/{id}` | Обновить | ✅ owner |
| `DELETE` | `/communities/{id}` | Удалить | ✅ owner |

<details>
<summary>Примеры</summary>

```bash
# Создать
curl -X POST http://localhost:8000/api/v1/communities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Python Devs","community_type":"public"}'

# Список с поиском
curl "http://localhost:8000/api/v1/communities?search=python&page=1&page_size=10"
```

Ответ:
```json
{
  "items": [{ "id": "...", "name": "Python Devs", "slug": "python-devs-a1b2c3d4", ... }],
  "total": 1, "page": 1, "page_size": 10, "pages": 1
}
```
</details>

### Members

| Метод | Путь | Описание | Auth |
|---|---|---|---|
| `GET` | `/communities/{id}/members` | Список | — |
| `POST` | `/communities/{id}/members` | Вступить | ✅ |
| `PUT` | `/communities/{id}/members/{user_id}` | Обновить | ✅ |
| `DELETE` | `/communities/{id}/members/{user_id}` | Удалить / выйти | ✅ |

### Roles

| Метод | Путь | Описание | Auth |
|---|---|---|---|
| `GET` | `/communities/{id}/roles` | Список | — |
| `POST` | `/communities/{id}/roles` | Создать | ✅ |
| `PUT` | `/communities/{id}/roles/{role_id}` | Обновить | ✅ |
| `DELETE` | `/communities/{id}/roles/{role_id}` | Удалить | ✅ |

### Posts

| Метод | Путь | Описание | Auth |
|---|---|---|---|
| `GET` | `/communities/{id}/posts` | Список | — |
| `GET` | `/posts/{id}` | Получить | — |
| `POST` | `/communities/{id}/posts` | Создать | ✅ |
| `PUT` | `/posts/{id}` | Обновить | ✅ author |
| `DELETE` | `/posts/{id}` | Удалить | ✅ author |

### Channels

| Метод | Путь | Описание | Auth |
|---|---|---|---|
| `GET` | `/communities/{id}/channels` | Список | — |
| `POST` | `/communities/{id}/channels` | Создать | ✅ |
| `PUT` | `/channels/{id}` | Обновить | ✅ |
| `DELETE` | `/channels/{id}` | Удалить | ✅ |

### Events

| Метод | Путь | Описание | Auth |
|---|---|---|---|
| `GET` | `/communities/{id}/events` | Список | — |
| `GET` | `/events/{id}` | Получить | — |
| `POST` | `/communities/{id}/events` | Создать | ✅ |
| `PUT` | `/events/{id}` | Обновить | ✅ |
| `DELETE` | `/events/{id}` | Удалить | ✅ |

### Subscriptions

| Метод | Путь | Описание | Auth |
|---|---|---|---|
| `GET` | `/communities/{id}/subscriptions` | Уровни подписок | — |
| `POST` | `/communities/{id}/subscriptions` | Оформить | ✅ |

### Donations

| Метод | Путь | Описание | Auth |
|---|---|---|---|
| `GET` | `/communities/{id}/donations` | Список | — |
| `POST` | `/communities/{id}/donations` | Сделать донат | ✅ |

### Analytics

| Метод | Путь | Описание | Auth |
|---|---|---|---|
| `GET` | `/communities/{id}/analytics` | Аналитика сообщества | ✅ |
| `GET` | `/posts/{id}/analytics` | Аналитика поста | ✅ |
| `GET` | `/members/{id}/analytics` | Аналитика участника | ✅ |

### Health

```
GET /health → {"status":"healthy","service":"community-service","version":"1.0.0"}
```

---

## 📊 Модели данных

### ER-диаграмма

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Community   │────<│    Member    │>────│      Role        │
│              │     │              │  M2M│                  │
│ id (UUID)    │     │ id (UUID)    │     │ id (UUID)        │
│ name         │     │ community_id │     │ community_id     │
│ slug (uniq)  │     │ user_id      │     │ name             │
│ type         │     │ status       │     │ permissions_list │
│ status       │     │ is_owner     │     │ is_default       │
│ owner_id     │     │ nickname     │     │ priority         │
│ member_count │     │ joined_at    │     └──────────────────┘
│ post_count   │     └──────────────┘
└──────┬───────┘
       │
       ├──< Post         (community_id, channel_id, author_id, content, status, media_urls[])
       ├──< Channel      (community_id, name, type, position)
       ├──< Event        (community_id, creator_id, title, starts_at, ends_at, status)
       ├──< SubLevel     (community_id, name, price, duration_days, features)
       │       └──< Subscription  (level_id, user_id, community_id, status, starts_at, expires_at)
       └──< Donation     (community_id, donor_id, amount, currency, message, is_anonymous)
```

Все первичные ключи — **UUID v4**.

---

## 📨 Event System

### События

| Событие | Триггер |
|---|---|
| `community.created` | Создание сообщества |
| `community.updated` | Обновление |
| `community.deleted` | Удаление |
| `member.joined` | Вступление участника |
| `member.left` | Выход / удаление |
| `post.created` | Публикация поста |
| `post.updated` | Обновление |
| `post.deleted` | Удаление |
| `donation.received` | Получение доната |
| `subscription.started` | Оформление подписки |
| `subscription.ended` | Окончание подписки |
| `event.created` | Создание мероприятия |
| `event.updated` | Обновление |
| `event.deleted` | Удаление |

### Формат

```json
{
  "event_id": "550e8400-...",
  "event_type": "community.created",
  "timestamp": "2024-01-01T12:00:00Z",
  "service": "community-service",
  "payload": { "community_id": "...", "owner_id": "...", "name": "..." },
  "metadata": {}
}
```

### Переключение брокера

```env
EVENT_BROKER_TYPE=kafka      # или rabbitmq
```

Если брокер недоступен — сервис продолжает работать, события логируются.

---

## 💨 Кэширование

### Что кэшируется

| Данные | TTL | Ключ |
|---|---|---|
| Сообщество по ID | 5 мин | `community:{id}` |
| Список сообществ | 5 мин | `communities:list:{page}:{size}` |
| Роли сообщества | 5 мин | `community:{id}:roles` |
| Аналитика сообщества | 10 мин | `community:{id}:analytics` |
| Аналитика поста | 10 мин | `post:{id}:analytics` |
| Top donors | 5 мин | `community:{id}:top_donors` |

### Инвалидация

- При записи (create / update / delete) — точечное удаление ключа
- Pattern-based удаление связанных списков
- Если Redis недоступен — запросы идут напрямую в PostgreSQL

---

## 🔒 Безопасность

### JWT

Токен проверяется в middleware. Результат → `request.state.user` (`UserContext`).

### RBAC

17 разрешений, привязанных к ролям:

```
community.create / update / delete / view
member.manage / kick / ban
role.manage
post.create / update / delete / moderate
channel.manage
event.manage
subscription.manage
analytics.view
donation.view
```

- **Владелец** сообщества (`is_owner=True`) — все разрешения автоматически
- **Суперадмин** (`is_superadmin=True` в JWT) — обходит все проверки
- Разрешения хранятся как `ARRAY(String)` в таблице `roles`

### Валидация

- Все входные данные валидируются через Pydantic v2
- SQLAlchemy — параметризованные запросы (защита от SQL-инъекций)
- Ограничение длины полей через `Field(max_length=...)`

---

## 🧪 Тестирование

```bash
# Все тесты
pytest tests/ -v

# С покрытием
pytest tests/ --cov=app --cov-report=html
```

### Фикстуры

| Фикстура | Описание |
|---|---|
| `client` | Неавторизованный HTTP-клиент |
| `auth_client` | Авторизованный (JWT-токен) |

---

## 🚢 Деплой и масштабирование

### Горизонтальное масштабирование

```bash
docker-compose up --scale community-app=5 -d
```

Nginx балансирует нагрузку (`least_conn`).

### Production-настройки

```env
DEBUG=false
WORKERS_COUNT=4            # 2 * CPU + 1
DB_POOL_SIZE=20
JWT_SECRET_KEY=<длинный случайный ключ>
```

### Docker

- Multi-stage build (builder → runtime)
- Непривилегированный пользователь (`appuser`)
- Health check встроен
- Entrypoint: миграции → Gunicorn + Uvicorn workers

---

## 📊 Мониторинг

### Structured Logging

Каждый лог — JSON:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "message": "Сообщество создано",
  "service": "community-service",
  "user_id": "...",
  "community_id": "...",
  "action": "community_created",
  "duration_ms": 45.2,
  "request_id": "abc-123"
}
```

### Заголовки ответа

```
X-Request-ID: abc-123-def
X-Response-Time: 45.2ms
```

---

## ❓ FAQ

### Как добавить новую сущность?

1. Модель → `app/domain/models.py`
2. Схемы → `app/schemas/`
3. Репозиторий → `app/repositories/`
4. Сервис → `app/services/`
5. Router → `app/api/v1/`
6. Контейнер → `app/infrastructure/container.py`
7. Подключить роутер → `app/api/v1/router.py`
8. Миграция → `alembic revision --autogenerate -m "add ..."`

### Как переключиться на RabbitMQ?

```env
EVENT_BROKER_TYPE=rabbitmq
```

### Как отключить Swagger?

```env
DEBUG=false
```

### Как подключить внешний Auth Service?

Заменить декодирование в `app/core/security.py` на HTTP-вызов к Auth Service.

---

<div align="center">

**Community Service v1.0.0**

</div>
```
