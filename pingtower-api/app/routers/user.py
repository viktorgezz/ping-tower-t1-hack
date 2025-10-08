from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User, UserSelectedEndpoint
from app.models.notification import NotificationChannel, AlertRule, NotificationLog
from app.models.resource import Endpoint
from app.schemas.user import (
    UserProfile, UserProfileUpdate, NotificationChannelsResponse, 
    NotificationChannelCreate, AlertRulesResponse, AlertRuleCreate, 
    AlertRuleUpdate, NotificationLogsResponse, NotificationLogsQueryParams,
    SaveSelectedEndpointsRequest, SelectedEndpointsResponse, UserSelectedEndpointResponse
)

router = APIRouter()

def get_current_user(authorization: str = None, db: Session = Depends(get_db)):
    """Получение текущего пользователя из токена"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Требуется аутентификация"
        )
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )
    
    return user

@router.get("/profile", response_model=UserProfile)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение информации профиля пользователя"""
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        emailVerified=current_user.email_verified
    )

@router.put("/profile", response_model=UserProfile)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление информации профиля пользователя"""
    current_user.name = profile_data.name
    db.commit()
    db.refresh(current_user)
    
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        emailVerified=current_user.email_verified
    )

@router.get("/notification-channels", response_model=NotificationChannelsResponse)
async def get_notification_channels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение всех каналов уведомлений пользователя"""
    channels = db.query(NotificationChannel).filter(
        NotificationChannel.user_id == current_user.id
    ).all()
    
    channel_list = []
    for channel in channels:
        channel_list.append({
            "id": channel.id,
            "type": channel.type,
            "value": channel.value,
            "verified": channel.verified
        })
    
    return NotificationChannelsResponse(channels=channel_list)

@router.post("/notification-channels", response_model=dict, status_code=201)
async def create_notification_channel(
    channel_data: NotificationChannelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Добавление нового канала уведомлений"""
    # Проверка существования канала с таким значением
    existing_channel = db.query(NotificationChannel).filter(
        NotificationChannel.user_id == current_user.id,
        NotificationChannel.type == channel_data.type,
        NotificationChannel.value == channel_data.value
    ).first()
    
    if existing_channel:
        raise HTTPException(
            status_code=400,
            detail="Канал уведомлений с таким значением уже существует"
        )
    
    # Создание нового канала
    channel = NotificationChannel(
        user_id=current_user.id,
        type=channel_data.type,
        value=channel_data.value,
        verified=False  # По умолчанию не верифицирован
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    
    return {
        "id": channel.id,
        "type": channel.type,
        "value": channel.value,
        "verified": channel.verified
    }

@router.delete("/notification-channels/{channel_id}", status_code=204)
async def delete_notification_channel(
    channel_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление канала уведомлений"""
    channel = db.query(NotificationChannel).filter(
        NotificationChannel.id == channel_id,
        NotificationChannel.user_id == current_user.id
    ).first()
    
    if not channel:
        raise HTTPException(
            status_code=404,
            detail="Канал уведомлений не найден"
        )
    
    db.delete(channel)
    db.commit()

@router.get("/alert-rules", response_model=AlertRulesResponse)
async def get_alert_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение всех правил оповещений пользователя"""
    rules = db.query(AlertRule).filter(
        AlertRule.user_id == current_user.id
    ).all()
    
    rule_list = []
    for rule in rules:
        rule_list.append({
            "id": rule.id,
            "name": rule.name,
            "isActive": rule.is_active,
            "conditions": rule.conditions,
            "channels": rule.channels,
            "delay": rule.delay,
            "repeatInterval": rule.repeat_interval
        })
    
    return AlertRulesResponse(rules=rule_list)

@router.post("/alert-rules", response_model=dict, status_code=201)
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание нового правила оповещений"""
    # Проверка существования каналов
    channel_ids = rule_data.channels
    existing_channels = db.query(NotificationChannel).filter(
        NotificationChannel.id.in_(channel_ids),
        NotificationChannel.user_id == current_user.id
    ).all()
    
    if len(existing_channels) != len(channel_ids):
        raise HTTPException(
            status_code=400,
            detail="Один или несколько каналов уведомлений не найдены"
        )
    
    # Создание нового правила
    rule = AlertRule(
        user_id=current_user.id,
        name=rule_data.name,
        is_active=rule_data.is_active,
        conditions=rule_data.conditions,
        channels=rule_data.channels,
        delay=rule_data.delay,
        repeat_interval=rule_data.repeat_interval
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    return {
        "id": rule.id,
        "name": rule.name,
        "isActive": rule.is_active,
        "conditions": rule.conditions,
        "channels": rule.channels,
        "delay": rule.delay,
        "repeatInterval": rule.repeat_interval
    }

@router.put("/alert-rules/{rule_id}", response_model=dict)
async def update_alert_rule(
    rule_id: UUID,
    rule_data: AlertRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Изменение существующего правила оповещений"""
    rule = db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.user_id == current_user.id
    ).first()
    
    if not rule:
        raise HTTPException(
            status_code=404,
            detail="Правило оповещений не найдено"
        )
    
    # Проверка существования каналов
    channel_ids = rule_data.channels
    existing_channels = db.query(NotificationChannel).filter(
        NotificationChannel.id.in_(channel_ids),
        NotificationChannel.user_id == current_user.id
    ).all()
    
    if len(existing_channels) != len(channel_ids):
        raise HTTPException(
            status_code=400,
            detail="Один или несколько каналов уведомлений не найдены"
        )
    
    # Обновление правила
    rule.name = rule_data.name
    rule.is_active = rule_data.is_active
    rule.conditions = rule_data.conditions
    rule.channels = rule_data.channels
    rule.delay = rule_data.delay
    rule.repeat_interval = rule_data.repeat_interval
    
    db.commit()
    db.refresh(rule)
    
    return {
        "id": rule.id,
        "name": rule.name,
        "isActive": rule.is_active,
        "conditions": rule.conditions,
        "channels": rule.channels,
        "delay": rule.delay,
        "repeatInterval": rule.repeat_interval
    }

@router.delete("/alert-rules/{rule_id}", status_code=204)
async def delete_alert_rule(
    rule_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление правила оповещений"""
    rule = db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.user_id == current_user.id
    ).first()
    
    if not rule:
        raise HTTPException(
            status_code=404,
            detail="Правило оповещений не найдено"
        )
    
    db.delete(rule)
    db.commit()

@router.get("/notification-logs", response_model=NotificationLogsResponse)
async def get_notification_logs(
    type: Optional[str] = Query(None, description="Тип канала для фильтрации"),
    from_: Optional[datetime] = Query(None, alias="from", description="Начальная дата/время"),
    to: Optional[datetime] = Query(None, description="Конечная дата/время"),
    limit: int = Query(50, description="Ограничение количества результатов"),
    offset: int = Query(0, description="Смещение для пагинации"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение лога отправленных уведомлений"""
    
    # Базовый запрос логов уведомлений
    query = db.query(NotificationLog)
    
    # Применение фильтров
    if type:
        query = query.filter(NotificationLog.channel_type == type)
    
    if from_:
        query = query.filter(NotificationLog.sent_at >= from_)
    
    if to:
        query = query.filter(NotificationLog.sent_at <= to)
    
    # Подсчет общего количества
    total_count = query.count()
    
    # Применение пагинации
    logs = query.offset(offset).limit(limit).all()
    
    # Преобразование в формат ответа
    notification_list = []
    for log in logs:
        notification_list.append({
            "id": log.id,
            "sentAt": log.sent_at,
            "channelType": log.channel_type,
            "channelValue": log.channel_value,
            "ruleName": log.rule_name,
            "resourceName": log.resource_name,
            "message": log.message
        })
    
    return NotificationLogsResponse(
        notifications=notification_list,
        totalCount=total_count
    )

@router.post("/selected-endpoints", response_model=dict, status_code=201)
async def save_selected_endpoints(
    request_data: SaveSelectedEndpointsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Сохранение выбранных пользователем эндпоинтов для мониторинга"""
    
    # Проверяем, что все эндпоинты принадлежат указанному ресурсу
    endpoint_ids = [ep.endpoint_id for ep in request_data.selected_endpoints]
    endpoints = db.query(Endpoint).filter(
        Endpoint.id.in_(endpoint_ids),
        Endpoint.resource_id == request_data.resource_id
    ).all()
    
    if len(endpoints) != len(endpoint_ids):
        raise HTTPException(
            status_code=400,
            detail="Один или несколько эндпоинтов не найдены или не принадлежат указанному ресурсу"
        )
    
    # Удаляем существующие записи для этого пользователя и ресурса
    existing_selections = db.query(UserSelectedEndpoint).join(Endpoint).filter(
        UserSelectedEndpoint.user_id == current_user.id,
        Endpoint.resource_id == request_data.resource_id
    ).all()
    
    for selection in existing_selections:
        db.delete(selection)
    
    # Создаем новые записи для выбранных эндпоинтов
    created_count = 0
    for selected_ep in request_data.selected_endpoints:
        if selected_ep.is_selected:
            user_selected_endpoint = UserSelectedEndpoint(
                user_id=current_user.id,
                endpoint_id=selected_ep.endpoint_id,
                is_active=True
            )
            db.add(user_selected_endpoint)
            created_count += 1
    
    db.commit()
    
    return {
        "message": f"Сохранено {created_count} выбранных эндпоинтов",
        "resource_id": request_data.resource_id,
        "selected_count": created_count
    }

@router.get("/selected-endpoints", response_model=SelectedEndpointsResponse)
async def get_selected_endpoints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение всех выбранных пользователем эндпоинтов"""
    
    selected_endpoints = db.query(UserSelectedEndpoint).join(Endpoint).filter(
        UserSelectedEndpoint.user_id == current_user.id,
        UserSelectedEndpoint.is_active == True
    ).all()
    
    endpoint_list = []
    for selection in selected_endpoints:
        endpoint_list.append(UserSelectedEndpointResponse(
            id=selection.id,
            endpoint_id=selection.endpoint_id,
            is_active=selection.is_active,
            created_at=selection.created_at,
            endpoint_path=selection.endpoint.path,
            endpoint_method=selection.endpoint.method
        ))
    
    return SelectedEndpointsResponse(selected_endpoints=endpoint_list)
