from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User
from app.models.resource import Resource, Endpoint
from app.schemas.resource import (
    ResourceCreate, ResourcesListResponse, ResourceResponse, 
    EndpointDiscoveryResponse, EndpointDiscovery, EndpointsUpdate,
    ResourceDetailResponse, EndpointInfo, StatsResponse, StatsDataPoint,
    EndpointsCreateRequest, EndpointsCreateResponse, EndpointResponse
)
from datetime import datetime, timedelta
import requests
import random

router = APIRouter()

def get_current_user(authorization: str = None, db: Session = Depends(get_db)):
    """Получение текущего пользователя из токена"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется аутентификация"
        )
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user

@router.get("/", response_model=ResourcesListResponse)
async def get_resources(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение всех ресурсов пользователя"""
    resources = db.query(Resource).filter(Resource.owner_id == current_user.id).all()
    
    resource_responses = []
    for resource in resources:
        # Подсчет метрик (в реальном приложении эти данные должны браться из БД)
        metrics = {
            "uptime24h": f"{random.uniform(95, 100):.2f}%",
            "avgResponseTime": random.randint(100, 500),
            "incidents24h": random.randint(0, 5),
            "lastCheck": datetime.utcnow()
        }
        
        resource_responses.append(ResourceResponse(
            id=resource.id,
            name=resource.name,
            url=str(resource.url),
            overallStatus=resource.overall_status,
            metrics=metrics
        ))
    
    return ResourcesListResponse(resources=resource_responses)

@router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource_data: ResourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Добавление нового сайта для мониторинга"""
    # Проверка существования ресурса с таким URL
    existing_resource = db.query(Resource).filter(
        Resource.url == str(resource_data.url),
        Resource.owner_id == current_user.id
    ).first()
    
    if existing_resource:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ресурс с таким URL уже существует"
        )
    
    # Создание нового ресурса
    resource = Resource(
        name=resource_data.name,
        url=str(resource_data.url),
        owner_id=current_user.id,
        overall_status="UNKNOWN"
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    
    # Создание ответа с метриками
    metrics = {
        "uptime24h": "0.00%",
        "avgResponseTime": 0,
        "incidents24h": 0,
        "lastCheck": datetime.utcnow()
    }
    
    return ResourceResponse(
        id=resource.id,
        name=resource.name,
        url=str(resource.url),
        overallStatus=resource.overall_status,
        metrics=metrics
    )

@router.post("/{resource_id}/endpoints/discover", response_model=EndpointDiscoveryResponse)
async def discover_endpoints(
    resource_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Автопарсинг эндпоинтов для сайта"""
    # Проверка существования ресурса
    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.owner_id == current_user.id
    ).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ресурс не найден"
        )
    
    # В реальном приложении здесь должен быть парсинг сайта
    # Для демонстрации возвращаем стандартные эндпоинты
    endpoints = [
        EndpointDiscovery(path="/", method="GET", isSelected=True),
        EndpointDiscovery(path="/api/health", method="GET", isSelected=True),
        EndpointDiscovery(path="/login", method="POST", isSelected=False),
        EndpointDiscovery(path="/api/status", method="GET", isSelected=False),
    ]
    
    return EndpointDiscoveryResponse(endpoints=endpoints)

@router.put("/{resource_id}/endpoints")
async def update_endpoints(
    resource_id: UUID,
    endpoints_data: EndpointsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Сохранение выбранных пользователем эндпоинтов и начало мониторинга"""
    # Проверка существования ресурса
    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.owner_id == current_user.id
    ).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ресурс не найден"
        )
    
    # Удаление существующих эндпоинтов
    db.query(Endpoint).filter(Endpoint.resource_id == resource_id).delete()
    
    # Создание новых эндпоинтов
    for endpoint_data in endpoints_data.endpoints:
        endpoint = Endpoint(
            resource_id=resource_id,
            path=endpoint_data.path,
            method=endpoint_data.method,
            current_status="UNKNOWN"
        )
        db.add(endpoint)
    
    # Обновление статуса ресурса
    resource.overall_status = "UP"
    db.commit()
    
    # Возвращаем обновленные данные ресурса
    updated_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    return {
        "id": updated_resource.id,
        "name": updated_resource.name,
        "url": str(updated_resource.url),
        "overallStatus": updated_resource.overall_status
    }

@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление ресурса и остановка всего его мониторинга"""
    # Проверка существования ресурса
    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.owner_id == current_user.id
    ).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ресурс не найден"
        )
    
    # Удаление ресурса (каскадное удаление эндпоинтов и логов)
    db.delete(resource)
    db.commit()

@router.get("/{resource_id}", response_model=ResourceDetailResponse)
async def get_resource_detail(
    resource_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение детальной информации для личного кабинета ресурса"""
    # Проверка существования ресурса
    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.owner_id == current_user.id
    ).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ресурс не найден"
        )
    
    # Получение эндпоинтов
    endpoints = db.query(Endpoint).filter(Endpoint.resource_id == resource_id).all()
    
    endpoint_infos = []
    for endpoint in endpoints:
        endpoint_infos.append(EndpointInfo(
            id=endpoint.id,
            path=endpoint.path,
            method=endpoint.method,
            currentStatus=endpoint.current_status,
            incidents24h=endpoint.incidents_24h,
            lastResponseTime=endpoint.last_response_time
        ))
    
    return ResourceDetailResponse(
        id=resource.id,
        name=resource.name,
        url=str(resource.url),
        endpoints=endpoint_infos
    )

@router.get("/{resource_id}/stats", response_model=StatsResponse)
async def get_resource_stats(
    resource_id: UUID,
    period: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение данных для графика количества сбоев"""
    # Проверка существования ресурса
    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.owner_id == current_user.id
    ).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ресурс не найден"
        )
    
    # Валидация периода
    if period not in ["24h", "7d", "30d"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый период. Доступные значения: 24h, 7d, 30d"
        )
    
    # Генерация тестовых данных (в реальном приложении данные должны браться из БД)
    now = datetime.utcnow()
    data_points = []
    
    if period == "24h":
        hours = 24
        interval = timedelta(hours=1)
    elif period == "7d":
        hours = 168  # 7 дней * 24 часа
        interval = timedelta(hours=1)
    else:  # 30d
        hours = 720  # 30 дней * 24 часа
        interval = timedelta(hours=1)
    
    for i in range(hours):
        timestamp = now - timedelta(hours=hours-i-1)
        value = random.randint(0, 3)  # Случайное количество сбоев
        data_points.append(StatsDataPoint(timestamp=timestamp, value=value))
    
    return StatsResponse(period=period, data=data_points)

@router.post("/endpoints", response_model=EndpointsCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_endpoints(
    request_data: EndpointsCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание эндпоинтов для ресурса"""
    
    # Проверяем, что ресурс существует и принадлежит пользователю
    resource = db.query(Resource).filter(
        Resource.id == request_data.resource_id,
        Resource.owner_id == current_user.id
    ).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ресурс не найден или не принадлежит пользователю"
        )
    
    # Проверяем на дубликаты эндпоинтов (path + method)
    existing_endpoints = db.query(Endpoint).filter(
        Endpoint.resource_id == request_data.resource_id
    ).all()
    
    existing_combinations = {(ep.path, ep.method) for ep in existing_endpoints}
    
    created_endpoints = []
    created_count = 0
    
    for endpoint_data in request_data.endpoints:
        # Проверяем, не существует ли уже такой эндпоинт
        if (endpoint_data.path, endpoint_data.method) in existing_combinations:
            continue  # Пропускаем дубликаты
        
        # Создаем новый эндпоинт
        endpoint = Endpoint(
            resource_id=request_data.resource_id,
            path=endpoint_data.path,
            method=endpoint_data.method,
            current_status="UNKNOWN"
        )
        db.add(endpoint)
        db.flush()  # Получаем ID без коммита
        
        created_endpoints.append(EndpointResponse(
            id=endpoint.id,
            path=endpoint.path,
            method=endpoint.method,
            current_status=endpoint.current_status,
            incidents_24h=endpoint.incidents_24h,
            last_response_time=endpoint.last_response_time,
            created_at=endpoint.created_at
        ))
        
        created_count += 1
        existing_combinations.add((endpoint_data.path, endpoint_data.method))
    
    db.commit()
    
    return EndpointsCreateResponse(
        message=f"Создано {created_count} новых эндпоинтов",
        resource_id=request_data.resource_id,
        created_count=created_count,
        endpoints=created_endpoints
    )
