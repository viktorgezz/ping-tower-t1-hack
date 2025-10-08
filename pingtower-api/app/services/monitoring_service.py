import requests
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class MonitoringService:
    """Сервис для работы с внешним API мониторинга"""
    
    def __init__(self):
        self.api_url = "http://203.81.208.57:8020/api/v1/test-endpoints"
        self.timeout = 30
        self.max_concurrent = 20
    
    def send_endpoints_for_monitoring(
        self, 
        urls: List[str], 
        max_concurrent: int = None, 
        timeout: int = None
    ) -> Dict[str, Any]:
        """
        Отправка эндпоинтов на внешний сервис мониторинга
        
        Args:
            urls: Список URL для мониторинга
            max_concurrent: Максимальное количество одновременных запросов
            timeout: Таймаут для запросов
            
        Returns:
            Dict с результатом запроса
        """
        if not urls:
            logger.warning("Список URL для мониторинга пуст")
            return {"error": "No URLs provided"}
        print(f"urls: {urls}")
        payload = {
            "urls": urls,
            "max_concurrent": max_concurrent or self.max_concurrent,
            "timeout": timeout or self.timeout
        }
        
        try:
            logger.info(f"Отправка {len(urls)} URL на мониторинг: {self.api_url}")
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout + 10  # Дополнительное время для HTTP запроса
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Успешно отправлено на мониторинг: {result}")
                return {
                    "success": True,
                    "data": result,
                    "total_urls": len(urls)
                }
            else:
                error_data = response.json() if response.content else {}
                logger.error(f"Ошибка API мониторинга: {response.status_code} - {error_data}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "details": error_data
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"Таймаут при обращении к API мониторинга: {self.api_url}")
            return {
                "success": False,
                "error": "Timeout",
                "details": "Request timeout"
            }
        except requests.exceptions.ConnectionError:
            logger.error(f"Ошибка подключения к API мониторинга: {self.api_url}")
            return {
                "success": False,
                "error": "Connection error",
                "details": "Cannot connect to monitoring API"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к API мониторинга: {e}")
            return {
                "success": False,
                "error": "Request error",
                "details": str(e)
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка при обращении к API мониторинга: {e}")
            return {
                "success": False,
                "error": "Unexpected error",
                "details": str(e)
            }
    
    def build_full_urls(self, endpoints: List[Dict[str, Any]]) -> List[str]:
        """
        Построение полных URL из эндпоинтов и ресурсов
        
        Args:
            endpoints: Список эндпоинтов с информацией о ресурсе
            
        Returns:
            Список полных URL
        """
        urls = []
        logger.info(f"Построение URL из {len(endpoints)} эндпоинтов")
        
        for i, endpoint in enumerate(endpoints):
            logger.info(f"Обработка эндпоинта {i+1}: {endpoint}")
            resource_url = endpoint.get("resource_url", "").rstrip("/")
            endpoint_path = endpoint.get("path", "").lstrip("/")
            
            if resource_url and endpoint_path:
                full_url = f"{resource_url}/{endpoint_path}"
            elif resource_url:
                full_url = resource_url
            else:
                logger.warning(f"Пропуск эндпоинта из-за отсутствия URL: {endpoint}")
                continue
                
            urls.append(full_url)
            logger.info(f"Добавлен URL: {full_url}")
        
        logger.info(f"Итого построено {len(urls)} URL")
        return urls
