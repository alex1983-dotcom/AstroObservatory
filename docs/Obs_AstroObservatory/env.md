```
# Настройки базы данных
# Для PostgreSQL:

DATABASE_URL=postgresql+asyncpg://user:password@localhost/astronomy_db

# Настройки приложения
APP_NAME=AstroObservatory
DEBUG=True

# Настройки безопасности
SECRET_KEY=your-secret-key-change-in-production-please-use-strong-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```