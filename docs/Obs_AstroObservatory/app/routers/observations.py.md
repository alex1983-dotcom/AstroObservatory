```python
"""
Маршрут для работы с наблюдениями.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.observation import (
    Observation,
    ObservationCreate,
    ObservationUpdate,
    ObservationRead
)
from app.models.astronomer import Astronomer
from app.models.celestial_body import CelestialBody


router = APIRouter(
    prefix="/observations",
    tags=["Наблюдения"],
    responses={404: {"description": "Не найдено"}}
)


@router.post(
    "/",
    response_model=ObservationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать наблюдение"  # Заголовок для Swagger
)
async def create_observation(
    observation: ObservationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создание нового наблюдения"""

    # Проверка существования астронома
    astronomer_query = select(Astronomer).where(Astronomer.id == observation.astronomer_id)
    astronomer_result = await db.execute(astronomer_query) 
    astronomer = astronomer_result.scalar_one_or_none()

    if not astronomer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Астроном с ID {observation.astronomer_id} не найден"
        )

    # Проверка существования небесного тела
    body_query = select(CelestialBody).where(CelestialBody.id == observation.celestial_body_id)
    body_result = await db.execute(body_query)  # выполняем запрос
    celestial_body = body_result.scalar_one_or_none()  # Берем одну запись или None

    if not celestial_body:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Небесное тело с ID {observation.celestial_body_id} не найдено"
        )

    # Проверка дубликата наблюдения
    duplicate_query = select(Observation).where(
        (Observation.astronomer_id == observation.astronomer_id) &
        (Observation.celestial_body_id == observation.celestial_body_id) &
        (func.date(Observation.observation_date) == func.date(observation.observation_date))
    )
    duplicate_result = await db.execute(duplicate_query)
    duplicate = duplicate_result.scalar_one_or_none()

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Астроном уже проводил наблюдение этого тела в эту дату"
        )

    db_observation = Observation(**observation.model_dump())
    db.add(db_observation)
    await db.commit()
    await db.refresh(db_observation)

    # Создание ответа с дополнительной информацией
    response = ObservationRead(**db_observation.model_dump())
    response.astronomer_name = f"{astronomer.first_name} {astronomer.last_name}"
    response.celestial_body_name = celestial_body.name

    return response


@router.get(
    "/",
    response_model=List[ObservationRead],
    summary="Получить список наблюдений"
)
async def read_observations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    astronomer_id: Optional[int] = Query(None),
    celestial_body_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка наблюдений с фильтрацией"""

    query = select(Observation)

    if astronomer_id:
        query = query.where(Observation.astronomer_id == astronomer_id)

    if celestial_body_id:
        query = query.where(Observation.celestial_body_id == celestial_body_id)

    query = query.order_by(Observation.observation_date.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    observations = result.scalars().all()

    # Преобразование в схемы с дополнительной информацией
    response_list = []
    for obs in observations:
        obs_read = ObservationRead(**obs.model_dump())
        
        # Получение связанных данных
        astro_query = select(Astronomer).where(Astronomer.id == obs.astronomer_id)
        astro_result = await db.execute(astro_query)
        astronomer = astro_result.scalar_one_or_none()
        
        body_query = select(CelestialBody).where(CelestialBody.id == obs.celestial_body_id)
        body_result = await db.execute(body_query)
        celestial_body = body_result.scalar_one_or_none()
        
        obs_read.astronomer_name = f"{astronomer.first_name} {astronomer.last_name}" if astronomer else None
        obs_read.celestial_body_name = celestial_body.name if celestial_body else None
        
        response_list.append(obs_read)

    return response_list


@router.get(
    "/{observation_id}",
    response_model=ObservationRead,
    summary="Получить наблюдение по ID"
)
async def read_observation(
    observation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение наблюдения по ID"""

    query = select(Observation).where(Observation.id == observation_id)
    result = await db.execute(query)
    observation = result.scalar_one_or_none()

    if not observation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Наблюдение с ID {observation_id} не найдено"
        )

    # Создание ответа с дополнительной информацией
    response = ObservationRead(**observation.model_dump())
    
    astro_query = select(Astronomer).where(Astronomer.id == observation.astronomer_id)
    astro_result = await db.execute(astro_query)
    astronomer = astro_result.scalar_one_or_none()
    
    body_query = select(CelestialBody).where(CelestialBody.id == observation.celestial_body_id)
    body_result = await db.execute(body_query)
    celestial_body = body_result.scalar_one_or_none()
    
    response.astronomer_name = f"{astronomer.first_name} {astronomer.last_name}" if astronomer else None
    response.celestial_body_name = celestial_body.name if celestial_body else None

    return response


@router.put(
    "/{observation_id}",
    response_model=ObservationRead,
    summary="Обновить наблюдение"
)
async def update_observation(
    observation_id: int,
    observation_update: ObservationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновление наблюдения"""

    query = select(Observation).where(Observation.id == observation_id)
    result = await db.execute(query)
    db_observation = result.scalar_one_or_none()

    if not db_observation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Наблюдение с ID {observation_id} не найдено"
        )

    update_data = observation_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_observation, field, value)

    await db.commit()
    await db.refresh(db_observation)

    # Создание ответа
    response = ObservationRead(**db_observation.model_dump())
    
    astro_query = select(Astronomer).where(Astronomer.id == db_observation.astronomer_id)
    astro_result = await db.execute(astro_query)
    astronomer = astro_result.scalar_one_or_none()
    
    body_query = select(CelestialBody).where(CelestialBody.id == db_observation.celestial_body_id)
    body_result = await db.execute(body_query)
    celestial_body = body_result.scalar_one_or_none()
    
    response.astronomer_name = f"{astronomer.first_name} {astronomer.last_name}" if astronomer else None
    response.celestial_body_name = celestial_body.name if celestial_body else None

    return response


@router.delete(
    "/{observation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить наблюдение"
)
async def delete_observation(
    observation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление наблюдения"""

    query = select(Observation).where(Observation.id == observation_id)
    result = await db.execute(query)
    db_observation = result.scalar_one_or_none()

    if not db_observation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Наблюдение с ID {observation_id} не найдено"
        )

    await db.delete(db_observation)
    await db.commit()

    return None


@router.get(
    "/statistics",
    summary="Статистика по наблюдениям"
)
async def get_observation_statistics(db: AsyncSession = Depends(get_db)):
    """Получение статистики по наблюдениям"""

    # Общее количество наблюдений
    total_query = select(func.count(Observation.id))
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # Топ-5 астрономов по количеству наблюдений
    top_astronomers_query = (
        select(
            Astronomer.id,
            Astronomer.first_name,
            Astronomer.last_name,
            func.count(Observation.id).label('count')
        )
        .join(Observation)
        .group_by(Astronomer.id, Astronomer.first_name, Astronomer.last_name)
        .order_by(func.count(Observation.id).desc())
        .limit(5)
    )
    top_astronomers_result = await db.execute(top_astronomers_query)
    top_astronomers = [
        {
            "id": id_,
            "name": f"{first_name} {last_name}",
            "observation_count": count
        }
        for id_, first_name, last_name, count in top_astronomers_result.all()
    ]

    # Топ-5 небесных тел по количеству наблюдений
    top_bodies_query = (
        select(
            CelestialBody.id,
            CelestialBody.name,
            func.count(Observation.id).label('count')
        )
        .join(Observation)
        .group_by(CelestialBody.id, CelestialBody.name)
        .order_by(func.count(Observation.id).desc())
        .limit(5)
    )
    top_bodies_result = await db.execute(top_bodies_query)
    top_bodies = [
        {"id": id_, "name": name, "observation_count": count}
        for id_, name, count in top_bodies_result.all()
    ]

    return {
        "total_observations": total,
        "top_astronomers": top_astronomers,
        "top_celestial_bodies": top_bodies
    }
```