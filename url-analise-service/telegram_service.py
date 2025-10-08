"""
Сервис для отправки уведомлений в Telegram
"""

import requests
import logging
from typing import Optional
from config import settings

# Настройка логирования
logger = logging.getLogger(__name__)


class TelegramService:
    """Сервис для отправки уведомлений в Telegram"""
    
    def __init__(self):
        self.config = settings.get_telegram_config()
        self.bot_token = self.config['bot_token']
        self.chat_id = self.config['chat_id']
        self.enabled = self.config['enabled']
        
    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        Отправляет сообщение в Telegram через бота
        
        Args:
            message (str): Текст сообщения
            parse_mode (str): Режим парсинга (HTML, Markdown)
        
        Returns:
            bool: True если отправка успешна, False в случае ошибки
        """
        if not self.enabled:
            logger.info("Telegram уведомления отключены")
            return False
            
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram не настроен: отсутствует токен или chat_id")
            return False
            
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        
        try:
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Telegram сообщение успешно отправлено")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при отправке Telegram сообщения: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке Telegram сообщения: {e}")
            return False
    
    def send_error_notification(self, url: str, status_code: int, error_message: str = None) -> bool:
        """
        Отправляет уведомление об ошибке эндпоинта
        
        Args:
            url (str): URL эндпоинта
            status_code (int): HTTP статус код
            error_message (str): Дополнительное сообщение об ошибке
        
        Returns:
            bool: True если отправка успешна, False в случае ошибки
        """
        message = f"🚨 <b>Ошибка эндпоинта</b>\n\n"
        message += f"🔗 <b>URL:</b> <code>{url}</code>\n"
        message += f"📊 <b>Статус:</b> <code>{status_code}</code>\n"
        
        if error_message:
            message += f"❌ <b>Ошибка:</b> <code>{error_message}</code>\n"
        
        message += f"\n⏰ <b>Время:</b> {self._get_current_time()}"
        
        return self.send_message(message)
    
    def send_service_error_notification(self, service_name: str, error_message: str) -> bool:
        """
        Отправляет уведомление об ошибке сервиса
        
        Args:
            service_name (str): Название сервиса
            error_message (str): Сообщение об ошибке
        
        Returns:
            bool: True если отправка успешна, False в случае ошибки
        """
        message = f"🚨 <b>Ошибка сервиса</b>\n\n"
        message += f"🔧 <b>Сервис:</b> <code>{service_name}</code>\n"
        message += f"❌ <b>Ошибка:</b> <code>{error_message}</code>\n"
        message += f"\n⏰ <b>Время:</b> {self._get_current_time()}"
        
        return self.send_message(message)
    
    def send_monitoring_summary(self, total_urls: int, successful: int, failed: int, 
                              avg_response_time: float = None) -> bool:
        """
        Отправляет сводку по мониторингу эндпоинтов
        
        Args:
            total_urls (int): Общее количество URL
            successful (int): Количество успешных запросов
            failed (int): Количество неудачных запросов
            avg_response_time (float): Среднее время ответа
        
        Returns:
            bool: True если отправка успешна, False в случае ошибки
        """
        message = f"📊 <b>Сводка мониторинга</b>\n\n"
        message += f"🔗 <b>Всего URL:</b> <code>{total_urls}</code>\n"
        message += f"✅ <b>Успешных:</b> <code>{successful}</code>\n"
        message += f"❌ <b>Ошибок:</b> <code>{failed}</code>\n"
        
        if avg_response_time is not None:
            message += f"⏱️ <b>Среднее время:</b> <code>{avg_response_time:.3f}s</code>\n"
        
        success_rate = (successful / total_urls * 100) if total_urls > 0 else 0
        message += f"📈 <b>Процент успеха:</b> <code>{success_rate:.1f}%</code>\n"
        
        message += f"\n⏰ <b>Время:</b> {self._get_current_time()}"
        
        return self.send_message(message)
    
    def _get_current_time(self) -> str:
        """Возвращает текущее время в формате строки"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Глобальный экземпляр сервиса
telegram_service = TelegramService()
