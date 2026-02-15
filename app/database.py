"""
Конфигурация базы данных и сессии.
"""

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
import os
from dotenv import load_dotenv


# Загрузка перменных окружения из .env файла
load_dotenv()

# URL подключения к базе данных
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL не задан!"
        "Создайте .env файл или установите переменную окружения."
    )

# Создание асинхронного движка
