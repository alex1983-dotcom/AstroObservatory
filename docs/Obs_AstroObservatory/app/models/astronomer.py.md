
---

```python
"""
Модель астрономов.

Содержит информацию об ученых и их достижениях.
"""

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime

# Импорты для связей
if TYPE_CHECKING:
    from app.models.observation import Observation
    from app.models.celestial_body import CelestialBody


class AstronomerBase(SQLModel):
    """
    Базовая модель астронома.
    """

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Имя астронома"
    )

    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Фамилия астронома"
    )

    birth_date: Optional[date] = Field(
        default=None,
        description="Дата рождения"
    )

    death_date: Optional[date] = Field(
        default=None,
        description="Дата смерти"
    )

    nationality: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Национальность"
    )

    biography: Optional[str] = Field(
        default=None,
        description="Биография"
    )

    achievements: Optional[str] = Field(
        default=None,
        description="Научные достижения"
    )

    notable_discoveries: Optional[str] = Field(
        default=None,
        description="Известные открытия"
    )

    academic_degree: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Академическая степень"
    )

    institution: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Место работы"
    )

    is_active: bool = Field(
        default=True,
        description="Активен ли астроном (жив/работает)"
    )


class Astronomer(AstronomerBase, table=True):
    """
    Модель астронома для базы данных.
    """

    __tablename__ = "astronomers"

    id: int = Field(
        default=None,
        primary_key=True,
        index=True
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        nullable=False
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        nullable=False
    )

    # Связь с наблюдениями
    observations: List["Observation"] = Relationship(
        back_populates="astronomer",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    __table_args__ = (
        Index("idx_astronomer_name", "first_name", "last_name"),
    )


class AstronomerCreate(AstronomerBase):
    """Схема для создания астронома"""
    pass


class AstronomerUpdate(SQLModel):
    """Схема для обновления астронома"""

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    nationality: Optional[str] = None
    biography: Optional[str] = None
    achievements: Optional[str] = None
    notable_discoveries: Optional[str] = None
    academic_degree: Optional[str] = None
    institution: Optional[str] = None
    is_active: Optional[bool] = None


class AstronomerRead(AstronomerBase):
    """Схема для чтения астронома"""

    id: int
    created_at: datetime
    updated_at: datetime

    # Вычисляемые поля
    observation_count: int = 0
    observed_bodies_count: int = 0
    observed_bodies: Optional[List[dict]] = None
```

---
