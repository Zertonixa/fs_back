# FastAPI Monolith Template 🚀

Шаблон монолитного FastAPI-приложения с модульной архитектурой, продуманной структурой и поддержкой расширения.

---

## 📁 Структура проекта
```
├──.github/ # Директория для пайплайнов
│ └── workflows/
│   └── ci.yaml # CI-пайплайн
├── alembic/ # Alembic 
│ ├── versions/ # Миграции Alembic
│ └── env.py # Конфигурационный файл Alembic
├── infra/ # Описание контейнеров (следет выносит в отдельный repo)
│ ├── dev/
│ │ └── docker-compose.yaml # Конфигурация контейнеров
│ └── Dockerfile # Multistage build файл
├── src/
│ ├── adapters/ # имплементация портов (интерфейсов)
│ │ ├── celery/
│ │ ├── redis/
│ │ └── s3/
│ ├── api/
│ │ ├── lifespan.py # Настройка lifespan
│ │ └── main.py # Запуск приложения
│ ├── apps/ # Конкретные модули API (домены)
│ │ ├── api/ # API-интерфейсы и роутеры
│ │ │ └── v1/
│ │ │   └── endpoints/ # Эндпоинты приложения
│ │ ├── repository/ # Репозитории для работы с данными
│ │ │ └── sql/ # SQLAlchemy репозитории и интерфейсы
│ │ ├── schemas/ # Схемы для валидации и DTO
│ │ │ ├── dataclasses/ # Внутренние dataclass DTO
│ │ │ └── pydantic/ # Pydantic схемы для API
│ │ ├── models/ # SQLAlchemy модели
│ │ └── service/ # Бизнес-логика приложения
│ ├── core/ # Базовые модули и логика
│ │ ├── config/ # Конфигурация приложения
│ │ ├── constants/ # Глобальные константы
│ │ ├── db/ # Инициализация базы данных
│ │ ├── dependencies/ # FastAPI Depends
│ │ ├── exceptions/ # Кастомные исключения
│ │ └── logger/ # Инициализация логгера
│ └── tasks/ # фоновые задачи
├── tests/ # Тесты API
├── Makefile
├── pyproject.toml # Конфигурация проекта
├── pytest.ini # Конфигурация тестов
└── run.sh # Запуск приложения
```


---

## ⚙️ Возможности

- ✅ Структурированный модульный монолит
- ✅ Распределение ответственности (core, api, schemas, service)
- ✅ Pydantic + Dataclass разделение
- ✅ Асинхронный SQLAlchemy 2.0 стиль
- ✅ Расширяемый логгер
- ✅ `hint.py` в каждой важной директории

---

## 🚀 Быстрый старт

```bash
git clone https://github.com/qu1nqqy/fastapi_monolith_template.git my_project
cd my_project
uv sync
./run.sh 
```
Далее следует адаптировать шаблон под свой проект, удалив лишние модули или добавив необходимые.

Пример первого коммита:
```bash
chore(template): adaptation of template
```

---

## 📦 Зависимости

- uv
- FastAPI
- SQLAlchemy 2.0
- Pydantic
- Uvicorn
- logging
- pytest

---

## 🧙‍♂️ Автор

Created with ❤️ by qu1nqqy

