```python
"""
Модель небесных тел (планеты, звезды, галактики).

Использует современный синтаксис SQLModel.
Содержит связи с другими моделями и вычисляемые свойства.
"""

from sqlmodel import SQLModel, Field, Relationship, Enum as SQLEnum, Index
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum as PyEnum

# Импорты для связей (избегаем циклических импортов)
if TYPE_CHECKING:
    from app.models.astronomer import Astronomer
    from app.models.observation import Observation


# Перечисление типов небесных тел
class BodyType(PyEnum):
    """Типы небесных тел"""
    PLANET = "planet"
    STAR = "star"
    GALAXY = "galaxy"
    NEBULA = "nebula"
    COMET = "comet"
    ASTEROID = "asteroid"
    BLACK_HOLE = "black_hole"


# Перечисление спектральных классов звезд
class SpectralClass(PyEnum):
    """
    Спектральные классы звезд (последовательность Гарвардская).

    Температурная шкала:
    - O: Самые горячие (>30000K)
    - B: Горячие (10000-30000K)
    - A: Белые (7500-10000K)
    - F: Желто-белые (6000-7500K)
    - G: Желтые (5200-6000K) - как наше Солнце
    - K: Оранжевые (3700-5200K)
    - M: Красные (<3700K)
    """
    O = "O"
    B = "B"
    A = "A"
    F = "F"
    G = "G"
    K = "K"
    M = "M"


class CelestialBodyBase(SQLModel):
    """
    Базовая модель небесного тела (для создания и обновления).
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Название небесного тела",
        index=True
    )

    type: BodyType = Field(
        ...,
        description="Тип небесного тела",
        sa_column=Field(sa_column=SQLEnum(BodyType))
    )

    description: Optional[str] = Field(
        default=None,
        description="Описание небесного тела"
    )

    # ========== Физические характеристики ==========

    mass: Optional[float] = Field(
        default=None,
        ge=0,
        description="Масса в массах Солнца (для звезд) или Земли (для планет)"
    )

    radius: Optional[float] = Field(
        default=None,
        ge=0,
        description="Радиус в радиусах Солнца или Земли"
    )

    temperature: Optional[float] = Field(
        default=None,
        ge=0,
        description="Температура поверхности в Кельвинах"
    )

    distance_from_earth: Optional[float] = Field(
        default=None,
        ge=0,
        description="Расстояние от Земли в световых годах"
    )

    # ========== Астрономические характеристики ==========

    spectral_class: Optional[SpectralClass] = Field(
        default=None,
        description="Спектральный класс (только для звезд)",
        sa_column=Field(sa_column=SQLEnum(SpectralClass))
    )

    absolute_magnitude: Optional[float] = Field(
        default=None,
        description="Абсолютная звёздная величина"
    )

    apparent_magnitude: Optional[float] = Field(
        default=None,
        description="Видимая звёздная величина"
    )

    # ========== Координаты в небесной сфере ==========

    right_ascension: Optional[float] = Field(
        default=None,
        ge=0,
        le=24,
        description="Прямое восхождение (часы, 0-24)"
    )

    declination: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
        description="Склонение (градусы, -90 до 90)"
    )

    # ========== Связи ==========

    parent_id: Optional[int] = Field(
        default=None,
        foreign_key="celestial_bodies.id",
        description="ID родительского небесного тела"
    )


class CelestialBody(CelestialBodyBase, table=True):
    """
    Модель небесного тела для базы данных.

    Структура:
    - Основная информация (название, тип, описание)
    - Физические характеристики (масса, радиус, температура)
    - Астрономические характеристики (звёздная величина, спектральный класс)
    - Координаты в небесной сфере
    - Связи с другими объектами (родитель, дети, наблюдения, наблюдатели)
    """

    __tablename__ = "celestial_bodies"

    # Первичный ключ
    id: int = Field(
        default=None,
        primary_key=True,
        index=True
    )

    # Временные метки
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        nullable=False
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        nullable=False
    )

    # ========== Связи с другими объектами ==========

    # Связь с родительским телом
    parent: Optional["CelestialBody"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "CelestialBody.id"}
    )

    # Связь с дочерними телами
    children: List["CelestialBody"] = Relationship(
        back_populates="parent"
    )

    # Связь с наблюдениями
    observations: List["Observation"] = Relationship(
        back_populates="celestial_body",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # Индексы
    __table_args__ = (
        Index("idx_type_distance", "type", "distance_from_earth"),
        Index("idx_magnitude", "apparent_magnitude"),
    )


class CelestialBodyCreate(CelestialBodyBase):
    """
    Схема для создания небесного тела.

    Наследует все поля от базовой модели.
    """
    pass


class CelestialBodyUpdate(SQLModel):
    """
    Схема для обновления небесного тела.

    Все поля опциональны, так как можно обновить только часть данных.
    """

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    type: Optional[BodyType] = None
    description: Optional[str] = None
    mass: Optional[float] = None
    radius: Optional[float] = None
    temperature: Optional[float] = None
    distance_from_earth: Optional[float] = None
    spectral_class: Optional[SpectralClass] = None
    absolute_magnitude: Optional[float] = None
    apparent_magnitude: Optional[float] = None
    right_ascension: Optional[float] = None
    declination: Optional[float] = None
    parent_id: Optional[int] = None


class CelestialBodyRead(CelestialBodyBase):
    """
    Схема для чтения небесного тела (полная информация).

    Используется для ответов из базы данных.
    """

    id: int
    created_at: datetime
    updated_at: datetime

    # Вычисляемые поля
    parent_name: Optional[str] = None
    children_count: int = 0
    observation_count: int = 0
    observers: Optional[List[dict]] = None
```

