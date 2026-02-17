```python
"""
Маршрут для работы с небесными телами.

Содержит все CRUD операции и дополнительные методы.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.celestial_body import (
    CelestialBody,
    BodyType,
    SpectralClass,
    CelestialBodyCreate,
    CelestialBodyUpdate,
    CelestialBodyRead
)
from app.services.search import apply_celestial_body_filters


router = APIRouter(
    prefix="/celestial-bodies",
    tags=["Небесные тела"],
    responses={404: {"description": "Не найдено"}}
)


# ========== CRUD операции ==========

@router.post(
    "/",
    response_model=CelestialBodyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать небесное тело",
    description="Создает новую запись о небесном теле в базе данных"
)
async def create_celestial_body(
    body: CelestialBodyCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Создание нового небесного тела.

    **Параметры:**
    - `body`: данные о небесном теле

    **Возвращает:**
    - Созданное небесное тело с полной информацией
    """

    # Проверка существования тела с таким именем
    query = select(CelestialBody).where(CelestialBody.name == body.name)  # Запрос и условие запроса
    result = await db.execute(query)  # выполнить запрос
    existing = result.scalar_one_or_none()  # ???

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Небесное тело с именем '{body.name}' уже существует"
        )

    # Проверка существования родительского тела
    if body.parent_id:
        parent_query = select(CelestialBody).where(CelestialBody.id == body.parent_id)
        parent_result = await db.execute(parent_query)
        parent = parent_result.scalar_one_or_none()

        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Родительское тело с ID {body.parent_id} не найдено"
            )

    # Создание нового объекта
    db_body = CelestialBody(**body.model_dump())

    # Добавление в сессию
    db.add(db_body)

    # Фиксация изменений
    await db.commit()

    # Обновление объекта
    await db.refresh(db_body)

    # Создание ответа с вычисляемыми полями (Не понимаю) ????????
    response = CelestialBodyRead(**db_body.model_dump())  # ???
    response.parent_name = db_body.parent.name if db_body.parent else None  # ???
    response.children_count = len(db_body.children)  # ???
    response.observation_count = len(db_body.observations)  # ???
    response.observers = [
        {"id": obs.astronomer.id, "name": obs.astronomer.first_name + " " + obs.astronomer.last_name}
        for obs in db_body.observations
    ] if db_body.observations else []

    return response


@router.get(
    "/",
    response_model=List[CelestialBodyRead],
    summary="Получить список небесных тел",
    description="Возвращает список небесных тел с пагинацией и фильтрацией"
)
async def read_celestial_bodies(
    skip: int = Query(0, ge=0, description="Количество пропущенных записей"),
    limit: int = Query(10, ge=1, le=100, description="Количество записей"),
    search: Optional[str] = Query(None, description="Поиск по названию"),
    body_type: Optional[BodyType] = Query(None, description="Фильтр по типу"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка небесных тел с возможностью фильтрации.

    **Параметры:**
    - `skip`: количество пропущенных записей (для пагинации)
    - `limit`: количество записей на страницу
    - `search`: поиск по названию
    - `body_type`: фильтр по типу тела

    **Возвращает:**
    - Список небесных тел
    """

    # Создание базового запроса
    query = select(CelestialBody)

    # Применение фильтров
    if search:
        query = query.where(CelestialBody.name.icontains(search))

    if body_type:
        query = query.where(CelestialBody.type == body_type)

    # Применение пагинации
    query = query.offset(skip).limit(limit)

    # Выполнение запроса
    result = await db.execute(query)
    bodies = result.scalars().all()

    # Преобразование в схемы с вычисляемыми полями
    response_list = []
    for body in bodies:
        body_read = CelestialBodyRead(**body.model_dump())
        body_read.parent_name = body.parent.name if body.parent else None
        body_read.children_count = len(body.children)
        body_read.observation_count = len(body.observations)
        body_read.observers = [
            {"id": obs.astronomer.id, "name": f"{obs.astronomer.first_name} {obs.astronomer.last_name}"}
            for obs in body.observations
        ] if body.observations else []
        response_list.append(body_read)

    return response_list


@router.get(
    "/{body_id}",
    response_model=CelestialBodyRead,
    summary="Получить небесное тело по ID",
    description="Возвращает подробную информацию о небесном теле"
)
async def read_celestial_body(
    body_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получение небесного тела по ID.

    **Параметры:**
    - `body_id`: ID небесного тела

    **Возвращает:**
    - Подробная информация о небесном теле
    """

    # Получение тела по ID
    query = select(CelestialBody).where(CelestialBody.id == body_id)
    result = await db.execute(query)
    body = result.scalar_one_or_none()

    if not body:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Небесное тело с ID {body_id} не найдено"
        )

    # Создание ответа с вычисляемыми полями
    response = CelestialBodyRead(**body.model_dump())
    response.parent_name = body.parent.name if body.parent else None
    response.children_count = len(body.children)
    response.observation_count = len(body.observations)
    response.observers = [
        {"id": obs.astronomer.id, "name": f"{obs.astronomer.first_name} {obs.astronomer.last_name}"}
        for obs in body.observations
    ] if body.observations else []

    return response


@router.put(
    "/{body_id}",
    response_model=CelestialBodyRead,
    summary="Обновить небесное тело",
    description="Обновляет информацию о небесном теле"
)
async def update_celestial_body(
    body_id: int,
    body_update: CelestialBodyUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление небесного тела.

    **Параметры:**
    - `body_id`: ID небесного тела
    - `body_update`: данные для обновления

    **Возвращает:**
    - Обновленное небесное тело
    """

    # Получение существующего тела
    query = select(CelestialBody).where(CelestialBody.id == body_id)
    result = await db.execute(query)
    db_body = result.scalar_one_or_none()

    if not db_body:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Небесное тело с ID {body_id} не найдено"
        )

    # Обновление полей
    update_data = body_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_body, field, value)

    await db.commit()
    await db.refresh(db_body)

    # Создание ответа
    response = CelestialBodyRead(**db_body.model_dump())
    response.parent_name = db_body.parent.name if db_body.parent else None
    response.children_count = len(db_body.children)
    response.observation_count = len(db_body.observations)
    response.observers = [
        {"id": obs.astronomer.id, "name": f"{obs.astronomer.first_name} {obs.astronomer.last_name}"}
        for obs in db_body.observations
    ] if db_body.observations else []

    return response


@router.delete(
    "/{body_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить небесное тело",
    description="Удаляет небесное тело из базы данных"
)
async def delete_celestial_body(
    body_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление небесного тела.

    **Параметры:**
    - `body_id`: ID небесного тела

    **Возвращает:**
    - 204 No Content при успешном удалении
    """

    query = select(CelestialBody).where(CelestialBody.id == body_id)
    result = await db.execute(query)
    db_body = result.scalar_one_or_none()

    if not db_body:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Небесное тело с ID {body_id} не найдено"
        )

    # Удаление объекта
    await db.delete(db_body)
    await db.commit()

    return None


# ========== Расширенные методы ==========

@router.get(
    "/statistics",
    summary="Статистика по небесным телам",
    description="Возвращает статистику по типам небесных тел"
)
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """
    Получение статистики по небесным телам.

    **Возвращает:**
    - Количество тел по типам
    - Общее количество
    - Статистика по расстояниям
    """

    # Подсчет количества по типам
    query = (
        select(CelestialBody.type, func.count(CelestialBody.id))
        .group_by(CelestialBody.type)
    )

    result = await db.execute(query)
    type_counts = {type_.value: count for type_, count in result.all()}

    # Общее количество
    total_query = select(func.count(CelestialBody.id))
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # Статистика по расстояниям
    distance_query = select(
        func.avg(CelestialBody.distance_from_earth),
        func.min(CelestialBody.distance_from_earth),
        func.max(CelestialBody.distance_from_earth)
    ).where(CelestialBody.distance_from_earth.isnot(None))

    distance_result = await db.execute(distance_query)
    avg_dist, min_dist, max_dist = distance_result.first()

    return {
        "total": total,
        "by_type": type_counts,
        "distance_statistics": {
            "average": avg_dist,
            "minimum": min_dist,
            "maximum": max_dist
        }
    }
```