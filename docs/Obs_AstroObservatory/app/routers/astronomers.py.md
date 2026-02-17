```python
"""
Маршрут для работы с астрономами.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.astronomer import (
    Astronomer,
    AstronomerCreate,
    AstronomerUpdate,
    AstronomerRead
)


router = APIRouter(
    prefix="/astronomers",
    tags=["Астрономы"],
    responses={404: {"description": "Не найдено"}}
)


@router.post(
    "/",
    response_model=AstronomerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать астронома",
    description="Создает новую запись об астрономе"
)
async def create_astronomer(
    astronomer: AstronomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создание нового астронома"""

    # Проверка существования
    query = select(Astronomer).where(
        (Astronomer.first_name == astronomer.first_name) &
        (Astronomer.last_name == astronomer.last_name)
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Астроном {astronomer.first_name} {astronomer.last_name} уже существует"
        )

    db_astronomer = Astronomer(**astronomer.model_dump())
    db.add(db_astronomer)
    await db.commit()
    await db.refresh(db_astronomer)

    # Создание ответа с вычисляемыми полями
    response = AstronomerRead(**db_astronomer.model_dump())
    response.observation_count = len(db_astronomer.observations)
    response.observed_bodies_count = len(set(
        obs.celestial_body_id for obs in db_astronomer.observations
    )) if db_astronomer.observations else 0
    response.observed_bodies = [
        {
            "id": obs.celestial_body.id,
            "name": obs.celestial_body.name,
            "type": obs.celestial_body.type.value
        }
        for obs in db_astronomer.observations
    ] if db_astronomer.observations else []

    return response


@router.get(
    "/",
    response_model=List[AstronomerRead],
    summary="Получить список астрономов"
)
async def read_astronomers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка астрономов"""

    query = select(Astronomer)

    if search:
        query = query.where(
            (Astronomer.first_name.icontains(search)) |
            (Astronomer.last_name.icontains(search))
        )

    if is_active is not None:
        query = query.where(Astronomer.is_active == is_active)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    astronomers = result.scalars().all()

    # Преобразование в схемы с вычисляемыми полями
    response_list = []
    for astronomer in astronomers:
        astro_read = AstronomerRead(**astronomer.model_dump())
        astro_read.observation_count = len(astronomer.observations)
        astro_read.observed_bodies_count = len(set(
            obs.celestial_body_id for obs in astronomer.observations
        )) if astronomer.observations else 0
        astro_read.observed_bodies = [
            {
                "id": obs.celestial_body.id,
                "name": obs.celestial_body.name,
                "type": obs.celestial_body.type.value
            }
            for obs in astronomer.observations
        ] if astronomer.observations else []
        response_list.append(astro_read)

    return response_list


@router.get(
    "/{astronomer_id}",
    response_model=AstronomerRead,
    summary="Получить астронома по ID"
)
async def read_astronomer(
    astronomer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение астронома по ID"""

    query = select(Astronomer).where(Astronomer.id == astronomer_id)
    result = await db.execute(query)
    astronomer = result.scalar_one_or_none()

    if not astronomer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Астроном с ID {astronomer_id} не найден"
        )

    # Создание ответа с вычисляемыми полями
    response = AstronomerRead(**astronomer.model_dump())
    response.observation_count = len(astronomer.observations)
    response.observed_bodies_count = len(set(
        obs.celestial_body_id for obs in astronomer.observations
    )) if astronomer.observations else 0
    response.observed_bodies = [
        {
            "id": obs.celestial_body.id,
            "name": obs.celestial_body.name,
            "type": obs.celestial_body.type.value
        }
        for obs in astronomer.observations
    ] if astronomer.observations else []

    return response


@router.put(
    "/{astronomer_id}",
    response_model=AstronomerRead,
    summary="Обновить астронома"
)
async def update_astronomer(
    astronomer_id: int,
    astronomer_update: AstronomerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновление астронома"""

    query = select(Astronomer).where(Astronomer.id == astronomer_id)
    result = await db.execute(query)
    db_astronomer = result.scalar_one_or_none()

    if not db_astronomer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Астроном с ID {astronomer_id} не найден"
        )

    update_data = astronomer_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_astronomer, field, value)

    await db.commit()
    await db.refresh(db_astronomer)

    # Создание ответа
    response = AstronomerRead(**db_astronomer.model_dump())
    response.observation_count = len(db_astronomer.observations)
    response.observed_bodies_count = len(set(
        obs.celestial_body_id for obs in db_astronomer.observations
    )) if db_astronomer.observations else 0
    response.observed_bodies = [
        {
            "id": obs.celestial_body.id,
            "name": obs.celestial_body.name,
            "type": obs.celestial_body.type.value
        }
        for obs in db_astronomer.observations
    ] if db_astronomer.observations else []

    return response


@router.delete(
    "/{astronomer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить астронома"
)
async def delete_astronomer(
    astronomer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление астронома"""

    query = select(Astronomer).where(Astronomer.id == astronomer_id)
    result = await db.execute(query)
    db_astronomer = result.scalar_one_or_none()

    if not db_astronomer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Астроном с ID {astronomer_id} не найден"
        )

    await db.delete(db_astronomer)
    await db.commit()

    return None


@router.get(
    "/statistics",
    summary="Статистика по астрономам"
)
async def get_astronomer_statistics(db: AsyncSession = Depends(get_db)):
    """Получение статистики по астрономам"""

    # Общее количество
    total_query = select(func.count(Astronomer.id))
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # Количество активных
    active_query = select(func.count(Astronomer.id)).where(Astronomer.is_active == True)
    active_result = await db.execute(active_query)
    active = active_result.scalar()

    # Статистика по национальностям
    nationality_query = (
        select(Astronomer.nationality, func.count(Astronomer.id))
        .where(Astronomer.nationality.isnot(None))
        .group_by(Astronomer.nationality)
        .order_by(func.count(Astronomer.id).desc())
    )
    nationality_result = await db.execute(nationality_query)
    nationalities = {nat: count for nat, count in nationality_result.all()}

    return {
        "total": total,
        "active": active,
        "inactive": total - active,
        "by_nationality": nationalities
    }
```