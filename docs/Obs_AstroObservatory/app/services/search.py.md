```python
"""
Сервис для расширенного поиска и фильтрации.
"""

from sqlmodel import select
from sqlmodel.sql.expression import Select
from typing import Optional
from datetime import datetime

from app.models.celestial_body import CelestialBody, BodyType, SpectralClass


def apply_celestial_body_filters(
    query: Select,
    name: Optional[str] = None,
    body_type: Optional[BodyType] = None,
    min_distance: Optional[float] = None,
    max_distance: Optional[float] = None,
    min_magnitude: Optional[float] = None,
    max_magnitude: Optional[float] = None,
    spectral_class: Optional[SpectralClass] = None
) -> Select:
    """
    Применяет фильтры поиска к запросу небесных тел.

    **Параметры:**
    - `query`: базовый запрос
    - `name`: поиск по названию
    - `body_type`: фильтр по типу
    - `min_distance`, `max_distance`: фильтр по расстоянию
    - `min_magnitude`, `max_magnitude`: фильтр по звёздной величине
    - `spectral_class`: фильтр по спектральному классу

    **Возвращает:**
    - Запрос с примененными фильтрами
    """

    # Поиск по названию
    if name:
        query = query.where(CelestialBody.name.icontains(name))

    # Фильтр по типу
    if body_type:
        query = query.where(CelestialBody.type == body_type)

    # Фильтр по расстоянию
    if min_distance is not None:
        query = query.where(CelestialBody.distance_from_earth >= min_distance)

    if max_distance is not None:
        query = query.where(CelestialBody.distance_from_earth <= max_distance)

    # Фильтр по звёздной величине
    if min_magnitude is not None:
        query = query.where(CelestialBody.apparent_magnitude >= min_magnitude)

    if max_magnitude is not None:
        query = query.where(CelestialBody.apparent_magnitude <= max_magnitude)

    # Фильтр по спектральному классу
    if spectral_class:
        query = query.where(CelestialBody.spectral_class == spectral_class)

    return query
```