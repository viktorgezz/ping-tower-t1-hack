#!/usr/bin/env python3
"""
Email Alerts Service
Сервис для отправки email уведомлений
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailAlertService:
    """Сервис для отправки email уведомлений"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        
    def send_email(self, to_emails: List[str], subject: str, body: str, is_html: bool = False) -> bool:
        """
        Отправляет email уведомление
        
        Args:
            to_emails: Список email адресов получателей
            subject: Тема письма
            body: Тело письма
            is_html: Флаг HTML формата
            
        Returns:
            bool: True если письмо отправлено успешно
        """
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.error("SMTP credentials not configured")
                return False
                
            # Создание сообщения
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            # Добавление тела письма
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Подключение к SMTP серверу и отправка
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            logger.info(f"Email sent successfully to {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_alert(self, alert_type: str, message: str, recipients: List[str]) -> bool:
        """
        Отправляет уведомление о тревоге
        
        Args:
            alert_type: Тип тревоги (ERROR, WARNING, INFO)
            message: Сообщение тревоги
            recipients: Список получателей
            
        Returns:
            bool: True если уведомление отправлено успешно
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"[{alert_type}] Email Alert - {timestamp}"
        
        body = f"""
Email Alert Service Notification

Type: {alert_type}
Time: {timestamp}
Message: {message}

---
This is an automated message from Email Alert Service.
        """.strip()
        
        return self.send_email(recipients, subject, body)

def main():
    """Основная функция для тестирования сервиса"""
    service = EmailAlertService()
    
    # Проверка конфигурации
    if not service.smtp_username or not service.smtp_password:
        logger.error("Please configure SMTP credentials via environment variables")
        logger.info("Required variables: SMTP_USERNAME, SMTP_PASSWORD")
        logger.info("Optional variables: SMTP_SERVER, SMTP_PORT, FROM_EMAIL")
        return
    
    # Тестовое уведомление
    test_recipients = os.getenv('TEST_RECIPIENTS', '').split(',')
    if test_recipients and test_recipients[0]:
        logger.info("Sending test alert...")
        success = service.send_alert(
            alert_type="INFO",
            message="Email Alert Service is running successfully!",
            recipients=test_recipients
        )
        if success:
            logger.info("Test alert sent successfully")
        else:
            logger.error("Failed to send test alert")
    else:
        logger.info("No test recipients configured. Set TEST_RECIPIENTS environment variable to test.")

if __name__ == "__main__":
    main()
