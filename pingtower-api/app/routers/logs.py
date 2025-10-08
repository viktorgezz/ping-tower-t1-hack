from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User
from app.models.resource import Resource, Endpoint, Log
from app.schemas.logs import LogsResponse, LogEntry, LogAnalysis, LogsQueryParams

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

@router.get("/", response_model=LogsResponse)
async def get_logs(
    resourceId: Optional[UUID] = Query(None, description="ID ресурса для фильтрации"),
    endpointId: Optional[UUID] = Query(None, description="ID эндпоинта для фильтрации"),
    status: Optional[str] = Query(None, description="Статус для фильтрации"),
    from_: Optional[datetime] = Query(None, alias="from", description="Начальная дата/время"),
    to: Optional[datetime] = Query(None, description="Конечная дата/время"),
    limit: int = Query(100, description="Ограничение количества результатов"),
    offset: int = Query(0, description="Смещение для пагинации"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение логов по всем ресурсам пользователя с возможностью фильтрации"""
    
    # Получение всех ресурсов пользователя
    user_resources = db.query(Resource).filter(Resource.owner_id == current_user.id).all()
    resource_ids = [r.id for r in user_resources]
    
    if not resource_ids:
        return LogsResponse(logs=[], totalCount=0)
    
    # Базовый запрос логов
    query = db.query(Log).filter(Log.resource_id.in_(resource_ids))
    
    # Применение фильтров
    if resourceId:
        query = query.filter(Log.resource_id == resourceId)
    
    if endpointId:
        query = query.filter(Log.endpoint_id == endpointId)
    
    if status:
        query = query.filter(Log.status == status)
    
    if from_:
        query = query.filter(Log.timestamp >= from_)
    
    if to:
        query = query.filter(Log.timestamp <= to)
    
    # Подсчет общего количества
    total_count = query.count()
    
    # Применение пагинации
    logs = query.offset(offset).limit(limit).all()
    
    # Преобразование в формат ответа
    log_entries = []
    for log in logs:
        # Получение информации о ресурсе и эндпоинте
        resource = db.query(Resource).filter(Resource.id == log.resource_id).first()
        endpoint = db.query(Endpoint).filter(Endpoint.id == log.endpoint_id).first()
        
        log_entries.append(LogEntry(
            id=log.id,
            timestamp=log.timestamp,
            resourceId=log.resource_id,
            resourceName=resource.name if resource else "Unknown",
            endpointId=log.endpoint_id,
            path=endpoint.path if endpoint else "Unknown",
            method=endpoint.method if endpoint else "Unknown",
            statusCode=log.status_code,
            responseTime=log.response_time,
            status=log.status,
            errorMessage=log.error_message
        ))
    
    return LogsResponse(logs=log_entries, totalCount=total_count)

@router.get("/{log_id}/analysis", response_model=LogAnalysis)
async def get_log_analysis(
    log_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение AI-анализа для конкретного лога или группы логов"""
    
    # Проверка существования лога и прав доступа
    log = db.query(Log).join(Resource).filter(
        Log.id == log_id,
        Resource.owner_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(
            status_code=404,
            detail="Лог не найден"
        )
    
    # В реальном приложении здесь должен быть вызов AI-сервиса
    # Для демонстрации возвращаем примерный анализ
    analysis_text = f"""
    Анализ лога {log_id}:
    
    Обнаружена проблема с эндпоинтом {log.endpoint_id} в период с {log.timestamp.strftime('%H:%M')} до {log.timestamp.strftime('%H:%M')}.
    
    Основные причины:
    - Высокое время отклика ({log.response_time}мс)
    - HTTP статус: {log.status_code}
    - Ошибка: {log.error_message or 'Не указана'}
    
    Рекомендации:
    1. Проверить состояние сервера
    2. Увеличить таймауты
    3. Мониторить нагрузку на базу данных
    """
    
    # Поиск связанных логов (в том же временном окне)
    time_window = timedelta(minutes=15)
    related_logs = db.query(Log).filter(
        Log.resource_id == log.resource_id,
        Log.timestamp >= log.timestamp - time_window,
        Log.timestamp <= log.timestamp + time_window,
        Log.id != log_id
    ).limit(5).all()
    
    related_log_ids = [str(l.id) for l in related_logs]
    
    return LogAnalysis(
        analysis=analysis_text.strip(),
        relatedLogs=related_log_ids
    )
