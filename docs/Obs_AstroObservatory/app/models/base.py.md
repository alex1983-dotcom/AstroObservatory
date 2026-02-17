```python
"""
Базовый миксин для всех моделей.

Добавляет временные метки к моделям.
"""

from sqlmodel import Field
from datetime import datetime, timezone
from typing import Optional


class TimestampMixin:
    """
    Миксин для автоматического добавления временных меток.

    Добавляет поля created_at и updated_at в модели.
    Эти поля автоматически заполняются при создании и обновлении записей.

    Пример использования:
        class Article(SQLModel, TimestampMixin, table=True):
            __tablename__ = "articles"
            id: int = Field(default=None, primary_key=True)
    """

    # Время создания записи
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"}
    )

    # Время последнего обновления записи
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP", "onupdate": "CURRENT_TIMESTAMP"}
    )
```
