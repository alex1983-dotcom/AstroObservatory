```python
"""
Конфигурация базы данных и сессии.

Использует SQLModel (SQLAlchemy 2.0 + Pydantic в одном пакете).
"""

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# URL подключения к базе данных
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "❌ DATABASE_URL не задан! "
        "Создайте .env файл или установите переменную окружения."
    )

# Создание асинхронного движка (engine)
engine = create_async_engine(
    DATABASE_URL,
    echo=True,           # Показывать SQL запросы в консоли
    future=True,         # Использовать новый стиль SQLAlchemy 2.0
    poolclass=NullPool   # Отключает пул соединений (для тестов)
)

# Создание фабрики сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


# Dependency для получения сессии базы данных
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения асинхронной сессии базы данных.

    Использует контекстный менеджер для гарантии закрытия сессии.
    Даже если произойдет ошибка, сессия будет закрыта.

    Пример использования в маршруте:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Функция для инициализации базы данных (создание таблиц)
async def init_db():
    """
    Инициализация базы данных: создание всех таблиц.

    ВАЖНО: В продакшене используйте Alembic для миграций!
    """
    from app.models import (
        celestial_body,
        astronomer,
        observation,
        user
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```