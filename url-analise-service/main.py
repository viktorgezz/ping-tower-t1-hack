from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional
import asyncio
import json
import logging
import time
from kafka import KafkaProducer
import os

# Импортируем наши классы из предоставленного кода
from url_parser import URLService, SimpleURLScanner
from endpoint_tester import EndpointTester, monitor_endpoints
from config import settings
from telegram_service import telegram_service

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="URL Analysis Service",
    description="Сервис для анализа URL и тестирования эндпоинтов",
    version="1.0.0"
)

# Модели данных для API
class URLRequest(BaseModel):
    url: HttpUrl
    max_pages: Optional[int] = settings.DEFAULT_MAX_PAGES

class URLResponse(BaseModel):
    internal_urls: List[str]
    media_urls: List[str]
    visited_pages: int
    total_internal_urls: int
    total_media_urls: int

class EndpointTestRequest(BaseModel):
    urls: List[HttpUrl]
    max_concurrent: Optional[int] = settings.DEFAULT_MAX_CONCURRENT
    timeout: Optional[int] = settings.DEFAULT_TIMEOUT

class EndpointTestResponse(BaseModel):
    message: str
    total_urls: int
    kafka_topic: str
    batch_id: str

# Kafka Producer для отправки результатов тестирования
class KafkaService:
    def __init__(self):
        self.producer = None
        self.kafka_bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.kafka_topic = settings.KAFKA_TOPIC
        
    def init_producer(self):
        """Инициализация Kafka producer"""
        try:
            # Получаем конфигурацию Kafka
            kafka_config = settings.get_kafka_config()
            
            # Создаем producer с аутентификацией
            producer_config = {
                'bootstrap_servers': kafka_config['bootstrap_servers'],
                'value_serializer': lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
                'key_serializer': lambda k: k.encode('utf-8') if k else None,
                'security_protocol': kafka_config['security_protocol'],
                'sasl_mechanism': kafka_config['sasl_mechanism'],
                'sasl_plain_username': kafka_config['sasl_plain_username'],
                'sasl_plain_password': kafka_config['sasl_plain_password'],
                # Настройки для предотвращения дублирования соединений (совместимые с kafka-python)
                'retries': 3,
                'retry_backoff_ms': 100,
                'request_timeout_ms': 30000,
                'max_block_ms': 10000,
                'acks': 'all',  # Ждем подтверждения от всех реплик
                'compression_type': 'gzip'  # Сжатие для экономии трафика
            }
            
            self.producer = KafkaProducer(**producer_config)
            logger.info(f"Kafka producer инициализирован: {kafka_config['bootstrap_servers']}")
            logger.info(f"Kafka топик: {kafka_config['topic']}")
            logger.info(f"Kafka пользователь: {kafka_config['sasl_plain_username']}")
        except Exception as e:
            logger.error(f"Ошибка инициализации Kafka producer: {e}")
            raise HTTPException(status_code=500, detail=f"Kafka недоступен: {e}")
    
    def send_results(self, results: List[Dict], request_id: str = None):
        """Отправка результатов в Kafka как один топик со списком JSON"""
        if not self.producer:
            self.init_producer()
        
        try:
            logger.info(f"🚀 НАЧИНАЕМ ОТПРАВКУ {len(results)} РЕЗУЛЬТАТОВ В KAFKA КАК ОДИН ТОПИК")
            logger.info(f"📋 Request ID: {request_id}")
            logger.info(f"📋 Kafka Topic: {self.kafka_topic}")
            
            # Обогащаем каждый результат метаданными
            enriched_results = []
            for i, result in enumerate(results):
                logger.info(f"📝 Обрабатываем результат {i+1}/{len(results)}: {result.get('url', 'unknown')}")
                enriched_result = {
                    **result,
                    'request_id': request_id or f"req_{i}",
                    'batch_timestamp': result.get('timestamp'),
                    'service_version': '1.0.0'
                }
                enriched_results.append(enriched_result)
            
            logger.info(f"📊 Количество результатов для отправки: {len(enriched_results)}")
            logger.info(f"📊 Структура данных: {type(enriched_results)} - список из {len(enriched_results)} элементов")
            
            # ВАЖНО: Отправляем ТОЛЬКО ОДИН топик со списком результатов (простой массив JSON)
            # НЕ отправляем отдельные топики для каждого URL!
            logger.info(f"📤 ОТПРАВЛЯЕМ ТОЛЬКО ОДИН ТОПИК В KAFKA...")
            logger.info(f"📤 НЕ отправляем отдельные топики для каждого URL!")
            
            # Создаем уникальный ключ для предотвращения дублирования
            unique_key = f"{request_id}_{int(time.time() * 1000)}"
            logger.info(f"🔑 Уникальный ключ для топика: {unique_key}")
            
            # ЕДИНСТВЕННЫЙ вызов producer.send() - отправляет весь список как один топик
            future = self.producer.send(
                self.kafka_topic,
                key=unique_key,
                value=enriched_results  # Это список из N элементов, отправляется как ОДИН топик
            )
            
            # Ждем подтверждения отправки
            record_metadata = future.get(timeout=10)
            logger.info(f"📨 Сообщение отправлено в партицию {record_metadata.partition}, offset {record_metadata.offset}")
            
            self.producer.flush()
            logger.info(f"✅ УСПЕШНО ОТПРАВЛЕН ОДИН ТОПИК с {len(results)} результатами в Kafka: {self.kafka_topic}")
            logger.info(f"✅ Данные отправлены как массив JSON с {len(enriched_results)} элементами")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки в Kafka: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка отправки в Kafka: {e}")
    
    def close(self):
        """Закрытие Kafka producer"""
        if self.producer:
            self.producer.close()

# Глобальный экземпляр Kafka сервиса
kafka_service = KafkaService()

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "URL Analysis Service",
        "version": "1.0.0",
        "endpoints": {
            "parse_url": "/api/v1/parse-url",
            "test_endpoints": "/api/v1/test-endpoints"
        }
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "service": "url-analysis-service"}

@app.post("/api/v1/parse-url", response_model=URLResponse)
async def parse_website_urls(request: URLRequest):
    """
    Парсинг URL сайта и извлечение всех эндпоинтов
    
    Принимает URL сайта и возвращает список всех найденных URL
    """
    try:
        logger.info(f"Начинаем парсинг URL: {request.url}")
        
        # Используем URLService для парсинга
        results = URLService.extract_urls(str(request.url), request.max_pages)
        
        logger.info(f"Парсинг завершен. Найдено {len(results['internal_urls'])} внутренних URL и {len(results['media_urls'])} медиа-файлов")
        
        return URLResponse(
            internal_urls=results['internal_urls'],
            media_urls=results['media_urls'],
            visited_pages=results['visited_pages'],
            total_internal_urls=len(results['internal_urls']),
            total_media_urls=len(results['media_urls'])
        )
        
    except Exception as e:
        logger.error(f"Ошибка при парсинге URL {request.url}: {str(e)}")
        # Отправляем уведомление об ошибке сервиса
        try:
            telegram_service.send_service_error_notification(
                service_name="URL Parser",
                error_message=f"Ошибка парсинга URL {request.url}: {str(e)}"
            )
        except Exception as telegram_error:
            logger.error(f"Ошибка отправки Telegram уведомления: {telegram_error}")
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга: {str(e)}")

@app.post("/api/v1/test-endpoints", response_model=EndpointTestResponse)
async def test_endpoints(request: EndpointTestRequest):
    """
    Тестирование списка эндпоинтов и отправка результатов в Kafka
    
    Принимает список URL для тестирования и отправляет результаты в Kafka
    """
    try:
        logger.info(f"Начинаем тестирование {len(request.urls)} эндпоинтов")
        
        # Конвертируем HttpUrl в строки
        url_strings = [str(url) for url in request.urls]
        
        # Создаем тестер с настройками из запроса
        tester = EndpointTester(
            max_concurrent=request.max_concurrent,
            timeout=request.timeout
        )
        
        # Тестируем эндпоинты
        logger.info(f"🔍 Начинаем тестирование {len(url_strings)} эндпоинтов...")
        try:
            results = await tester.test_multiple_endpoints(url_strings)
            logger.info(f"✅ Тестирование завершено. Получено {len(results)} результатов")
            
            # Отправляем результаты в Kafka
            request_id = f"test_{len(url_strings)}_{int(time.time())}"
            logger.info(f"📤 Отправляем результаты в Kafka с request_id: {request_id}")
            kafka_service.send_results(results, request_id)
        finally:
            # Обязательно закрываем сессию
            await tester.close_session()
        
        # Статистика
        successful = sum(1 for r in results if r.get('success', False))
        avg_response_time = sum(r.get('response_time', 0) for r in results if r.get('success', False)) / max(successful, 1)
        
        logger.info(f"Тестирование завершено. Успешных: {successful}/{len(url_strings)}, среднее время: {avg_response_time:.3f}s")
        
        return EndpointTestResponse(
            message=f"Протестировано {len(url_strings)} эндпоинтов. Успешных: {successful}",
            total_urls=len(url_strings),
            kafka_topic=kafka_service.kafka_topic,
            batch_id=request_id
        )
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании эндпоинтов: {str(e)}")
        # Отправляем уведомление об ошибке сервиса
        try:
            telegram_service.send_service_error_notification(
                service_name="Endpoint Tester",
                error_message=f"Ошибка тестирования эндпоинтов: {str(e)}"
            )
        except Exception as telegram_error:
            logger.error(f"Ошибка отправки Telegram уведомления: {telegram_error}")
        raise HTTPException(status_code=500, detail=f"Ошибка тестирования: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка ресурсов при завершении работы"""
    kafka_service.close()
    logger.info("Сервис завершает работу")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
