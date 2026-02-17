```python
"""
Главный файл приложения FastAPI.

Содержит конфигурацию и подключение маршрутов.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from app.database import init_db
from app.routers import (
    celestial_bodies_router,
    astronomers_router,
    observations_router,
    auth_router
)


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Lifespan context manager для управления жизненным циклом приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления жизненным циклом приложения.

    Выполняется при запуске и остановке приложения.
    """
    # Код при запуске приложения
    logger.info("🚀 Запуск приложения Astronomy API...")

    # Инициализация базы данных
    try:
        await init_db()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации базы данных: {e}")

    yield  # Приложение работает

    # Код при остановке приложения
    logger.info("👋 Приложение остановлено")


# Создание приложения FastAPI
app = FastAPI(
    title="Astronomy API",
    description="""
    API для управления базой данных астрономических объектов.

    ## Функциональность:
    - Управление небесными телами (планеты, звезды, галактики)
    - Управление информацией об астрономах
    - Запись и анализ наблюдений
    - Расширенный поиск и фильтрация
    - Аутентификация пользователей

    ## Технологии:
    - FastAPI 0.109.0
    - SQLModel (SQLAlchemy 2.0 + Pydantic)
    - PostgreSQL / SQLite
    """,
    version="1.0.0",
    contact={
        "name": "Astronomy API Team",
        "email": "admin@astronomy-api.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Настройка CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключение маршрутов
app.include_router(celestial_bodies_router)
app.include_router(astronomers_router)
app.include_router(observations_router)
app.include_router(auth_router)


# Корневой эндпоинт
@app.get(
    "/",
    summary="Корневой эндпоинт",
    description="Возвращает информацию о приложении"
)
async def root():
    """Корневой эндпоинт приложения"""
    return {
        "message": "🔭 Astronomy API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }


# Эндпоинт здоровья приложения
@app.get(
    "/health",
    summary="Проверка здоровья",
    description="Проверяет работоспособность приложения и базы данных"
)
async def health_check():
    """Проверка здоровья приложения"""
    from app.database import engine
    
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        database_status = "healthy"
    except Exception as e:
        database_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if database_status == "healthy" else "unhealthy",
        "database": database_status,
        "timestamp": datetime.utcnow().isoformat()
    }


# Обработчик ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Обработчик ошибок валидации запросов.

    Возвращает понятные сообщения об ошибках валидации.
    """
    logger.error(f"Ошибка валидации: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Ошибка валидации данных",
            "errors": exc.errors(),
            "body": exc.body
        }
    )


# Обработчик HTTP ошибок
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Обработчик HTTP ошибок"""
    logger.error(f"HTTP ошибка {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )


# Обработчик неожиданных ошибок
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Обработчик неожиданных ошибок"""
    logger.error(f"Неожиданная ошибка: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Внутренняя ошибка сервера",
            "message": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```