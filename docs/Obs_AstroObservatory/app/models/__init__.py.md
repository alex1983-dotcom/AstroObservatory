```python
"""
Модули моделей базы данных.

SQLModel объединяет SQLAlchemy модели и Pydantic схемы в одном классе.
"""

from app.models.base import TimestampMixin
from app.models.celestial_body import CelestialBody, BodyType, SpectralClass
from app.models.astronomer import Astronomer
from app.models.observation import Observation
from app.models.user import User

__all__ = [
    "TimestampMixin",
    "CelestialBody",
    "BodyType",
    "SpectralClass",
    "Astronomer",
    "Observation",
    "User"
]
```

