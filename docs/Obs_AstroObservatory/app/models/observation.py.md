```python
"""
Модель наблюдений астрономов за небесными телами.

Промежуточная таблица для связи многие-ко-многим.
"""

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, TYPE_CHECKING
from datetime import datetime

# Импорты для связей
if TYPE_CHECKING:
    from app.models.astronomer import Astronomer
    from app.models.celestial_body import CelestialBody


class ObservationBase(SQLModel):
    """
    Базовая модель наблюдения.
    """

    astronomer_id: int = Field(
        ...,
        ge=1,
        foreign_key="astronomers.id",
        description="ID астронома"
    )

    celestial_body_id: int = Field(
        ...,
        ge=1,
        foreign_key="celestial_bodies.id",
        description="ID небесного тела"
    )

    observation_date: datetime = Field(
        ...,
        description="Дата и время наблюдения"
    )

    location: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Место наблюдения (обсерватория)"
    )

    equipment: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Используемое оборудование"
    )

    duration_hours: Optional[float] = Field(
        default=None,
        ge=0,
        description="Продолжительность наблюдения в часах"
    )

    weather_conditions: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Погодные условия"
    )

    notes: Optional[str] = Field(
        default=None,
        description="Заметки и комментарии"
    )

    data_collected: Optional[str] = Field(
        default=None,
        description="Научные данные"
    )


class Observation(ObservationBase, table=True):
    """
    Модель наблюдения для базы данных.

    Связывает астронома с небесным телом и содержит детали наблюдения.
    Это промежуточная таблица для связи многие-ко-многим.
    """

    __tablename__ = "observations"

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

    # Связи
    astronomer: "Astronomer" = Relationship(back_populates="observations")
    celestial_body: "CelestialBody" = Relationship(back_populates="observations")

    __table_args__ = (
        Index("idx_observation_date", "observation_date"),
        Index("idx_astronomer_celestial", "astronomer_id", "celestial_body_id"),
    )


class ObservationCreate(ObservationBase):
    """Схема для создания наблюдения"""
    pass


class ObservationUpdate(SQLModel):
    """Схема для обновления наблюдения"""

    location: Optional[str] = Field(default=None, max_length=200)
    equipment: Optional[str] = Field(default=None, max_length=200)
    duration_hours: Optional[float] = Field(default=None, ge=0)
    weather_conditions: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None
    data_collected: Optional[str] = None


class ObservationRead(ObservationBase):
    """Схема для чтения наблюдения"""

    id: int
    created_at: datetime
    updated_at: datetime

    # Дополнительная информация
    astronomer_name: Optional[str] = None
    celestial_body_name: Optional[str] = None
```