```python
"""
Модель пользователей для аутентификации.
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from pydantic import EmailStr, field_validator


class UserBase(SQLModel):
    """
    Базовая модель пользователя.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Имя пользователя",
        unique=True,
        index=True
    )

    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        unique=True
    )

    full_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Полное имя"
    )


class User(UserBase, table=True):
    """
    Модель пользователя для базы данных.
    """

    __tablename__ = "users"

    id: int = Field(
        default=None,
        primary_key=True,
        index=True
    )

    hashed_password: str = Field(
        ..., # Что это?
        description="Хешированный пароль"
    )

    is_active: bool = Field(
        default=True,
        description="Активен ли пользователь"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        nullable=False
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        nullable=False
    )


class UserCreate(UserBase):
    """
    Схема для создания пользователя.
    """

    password: str = Field(
        ...,
        min_length=8,
        description="Пароль (минимум 8 символов)"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Валидация пароля"""
        if len(v) < 8:
            raise ValueError("Пароль должен быть минимум 8 символов")
        if not any(c.isupper() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return v


class UserUpdate(SQLModel):
    """
    Схема для обновления пользователя.
    """

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(default=None, max_length=100)
    password: Optional[str] = Field(default=None, min_length=8)


class UserRead(UserBase):
    """
    Схема для чтения пользователя.
    """

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserLogin(SQLModel):
    """
    Схема для входа в систему.
    """

    username: str = Field(..., description="Имя пользователя или email")
    password: str = Field(..., description="Пароль")
```