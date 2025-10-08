from celery import current_task
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.celery_app import celery_app
from app.services.monitoring_service import MonitoringService
from app.models.user import UserSelectedEndpoint
from app.models.resource import Endpoint, Resource
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.tasks.monitoring.monitor_all_endpoints")
def monitor_all_endpoints(self):
    """
    Периодическая задача для мониторинга всех выбранных эндпоинтов
    Выполняется каждую минуту
    """
    logger.info("Запуск задачи мониторинга всех эндпоинтов")
    
    try:
        # Получаем все активные эндпоинты
        endpoints_data = get_all_active_endpoints()
        
        if not endpoints_data:
            logger.info("Нет активных эндпоинтов для мониторинга")
            return {"message": "No active endpoints to monitor"}
        
        # Создаем сервис мониторинга
        monitoring_service = MonitoringService()
        
        # Строим полные URL
        urls = monitoring_service.build_full_urls(endpoints_data)
        
        if not urls:
            logger.warning("Не удалось построить URL для мониторинга")
            return {"message": "No valid URLs to monitor"}
        
        logger.info(f"Отправка {len(urls)} URL на мониторинг")
        
        # Отправляем на внешний API
        result = monitoring_service.send_endpoints_for_monitoring(urls)
        
        if result.get("success"):
            logger.info(f"Успешно отправлено на мониторинг: {result.get('total_urls', 0)} URL")
            return {
                "status": "success",
                "message": f"Sent {result.get('total_urls', 0)} URLs for monitoring",
                "total_urls": result.get('total_urls', 0)
            }
        else:
            logger.error(f"Ошибка при отправке на мониторинг: {result.get('error')}")
            return {
                "status": "error",
                "message": f"Failed to send URLs for monitoring: {result.get('error')}",
                "error": result.get('error'),
                "details": result.get('details')
            }
            
    except Exception as e:
        logger.error(f"Критическая ошибка в задаче мониторинга: {e}")
        return {
            "status": "error",
            "message": f"Critical error in monitoring task: {str(e)}"
        }

def get_all_active_endpoints() -> List[Dict[str, Any]]:
    """
    Получение всех активных эндпоинтов из базы данных
    
    Returns:
        Список словарей с данными эндпоинтов
    """
    db: Session = SessionLocal()
    endpoints_data = []
    
    try:
        # Получаем все активные выбранные эндпоинты с информацией о ресурсах
        query = db.query(
            UserSelectedEndpoint,
            Endpoint,
            Resource
        ).join(
            Endpoint, UserSelectedEndpoint.endpoint_id == Endpoint.id
        ).join(
            Resource, Endpoint.resource_id == Resource.id
        ).filter(
            UserSelectedEndpoint.is_active == True
        ).all()
        
        for user_selected, endpoint, resource in query:
            endpoint_data = {
                "user_selected_id": user_selected.id,
                "endpoint_id": endpoint.id,
                "resource_id": resource.id,
                "resource_url": str(resource.url),
                "path": endpoint.path,
                "method": endpoint.method,
                "user_id": user_selected.user_id
            }
            endpoints_data.append(endpoint_data)
            logger.info(f"Добавлен эндпоинт: {endpoint_data}")
        
        logger.info(f"Найдено {len(endpoints_data)} активных эндпоинтов для мониторинга")
        
    except Exception as e:
        logger.error(f"Ошибка при получении эндпоинтов из БД: {e}")
    finally:
        db.close()
    
    return endpoints_data

@celery_app.task(bind=True, name="app.tasks.monitoring.process_monitoring_results")
def process_monitoring_results(self, results: Dict[str, Any]):
    """
    Обработка результатов мониторинга (если потребуется в будущем)
    
    Args:
        results: Результаты мониторинга от внешнего API
    """
    logger.info("Обработка результатов мониторинга")
    
    try:
        # Здесь можно добавить логику обработки результатов
        # Например, сохранение в таблицу logs или обновление статусов
        
        logger.info(f"Результаты мониторинга обработаны: {results}")
        return {"status": "success", "message": "Results processed"}
        
    except Exception as e:
        logger.error(f"Ошибка при обработке результатов мониторинга: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True, name="app.tasks.monitoring.test_monitoring_connection")
def test_monitoring_connection(self):
    """
    Тестовая задача для проверки подключения к внешнему API мониторинга
    """
    logger.info("Тестирование подключения к API мониторинга")
    
    try:
        monitoring_service = MonitoringService()
        
        # Тестовый запрос с одним URL
        test_urls = ["https://httpbin.org/status/200"]
        result = monitoring_service.send_endpoints_for_monitoring(test_urls)
        
        if result.get("success"):
            logger.info("Подключение к API мониторинга успешно")
            return {"status": "success", "message": "Connection test passed"}
        else:
            logger.error(f"Ошибка подключения к API мониторинга: {result.get('error')}")
            return {"status": "error", "message": result.get('error')}
            
    except Exception as e:
        logger.error(f"Ошибка при тестировании подключения: {e}")
        return {"status": "error", "message": str(e)}
