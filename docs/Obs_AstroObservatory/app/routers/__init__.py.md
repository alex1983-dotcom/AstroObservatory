
```python
"""
Маршруты (routers) приложения.

Содержат все эндпоинты API.
"""

from app.routers.celestial_bodies import router as celestial_bodies_router
from app.routers.astronomers import router as astronomers_router
from app.routers.observations import router as observations_router
from app.routers.auth import router as auth_router

__all__ = [
    "celestial_bodies_router",
    "astronomers_router",
    "observations_router",
    "auth_router"
]
```