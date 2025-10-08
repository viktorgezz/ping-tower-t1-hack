import aiohttp
import asyncio
from urllib.parse import urlparse
import time
from typing import Dict, List, Optional
import ssl
import json
from datetime import datetime, timezone
import asyncpg
from bs4 import BeautifulSoup
import re
import logging
from telegram_service import telegram_service

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EndpointTester:
    def __init__(self, max_concurrent: int = 50, timeout: int = 30):
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.session = None
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def init_session(self):
        """Инициализация асинхронной сессии"""
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent,
            ssl=self.ssl_context,
            force_close=True
        )
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )

    async def close_session(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()

    async def test_endpoint(self, url: str) -> Dict:
        """Тестирование одного эндпоинта с сбором максимальной информации"""
        result = {
            'url': url,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'success': False,
            'error': None,
            'response_time': None,
            'status_code': None,
            'content_type': None,
            'content_length': None,
            'headers': {},
            'is_https': False,
            'technology_stack': [],
            'security_headers': {},
            'content_analysis': {},
            'additional_checks': {},
            'redirect_chain': []
        }

        start_time = time.time()

        try:
            async with self.session.get(
                    url,
                    allow_redirects=True,
                    ssl=self.ssl_context
            ) as response:
                # Базовая информация
                result['response_time'] = time.time() - start_time
                result['status_code'] = response.status
                result['content_type'] = response.headers.get('Content-Type')
                result['content_length'] = response.headers.get('Content-Length')
                result['success'] = 200 <= response.status < 400
                result['is_https'] = response.url.scheme == 'https'
                
                # Отправляем уведомление в Telegram при статусе 500
                if response.status == 500:
                    error_message = f"Внутренняя ошибка сервера (500) для URL: {url}"
                    logger.warning(f"Обнаружена ошибка 500: {url}")
                    try:
                        telegram_service.send_error_notification(
                            url=url,
                            status_code=500,
                            error_message="Внутренняя ошибка сервера"
                        )
                    except Exception as e:
                        logger.error(f"Ошибка отправки Telegram уведомления: {e}")

                # Заголовки
                result['headers'] = dict(response.headers)

                # Анализ цепочки редиректов
                if hasattr(response, 'history'):
                    result['redirect_chain'] = [str(res.url) for res in response.history]

                # Анализ безопасности
                self._analyze_security_headers(result, response.headers)

                # Анализ технологического стека
                self._analyze_technology_stack(result, response.headers)

                # Чтение и анализ контента
                try:
                    content = await response.read()
                    if content and result['content_type']:
                        self._analyze_content(result, content, result['content_type'])
                except Exception as e:
                    logger.warning(f"Content analysis failed for {url}: {str(e)}")
                    result['content_analysis']['error'] = str(e)

                # Информация о SSL (только для HTTPS)
                if result['is_https']:
                    try:
                        ssl_info = {}
                        if hasattr(response.connection, 'ssl_object'):
                            ssl_obj = response.connection.ssl_object
                            ssl_info = {
                                'cipher': ssl_obj.cipher(),
                                'protocol': ssl_obj.version(),
                            }
                        result['ssl_info'] = ssl_info
                    except Exception as e:
                        logger.warning(f"SSL info extraction failed for {url}: {str(e)}")
                        result['ssl_info'] = {'error': str(e)}

        except aiohttp.ClientError as e:
            result['error'] = str(e)
            # Отправляем уведомление о критических ошибках соединения
            try:
                telegram_service.send_error_notification(
                    url=url,
                    status_code=0,  # 0 означает ошибку соединения
                    error_message=f"Ошибка соединения: {str(e)}"
                )
            except Exception as telegram_error:
                logger.error(f"Ошибка отправки Telegram уведомления: {telegram_error}")
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
            # Отправляем уведомление о неожиданных ошибках
            try:
                telegram_service.send_error_notification(
                    url=url,
                    status_code=0,  # 0 означает неожиданную ошибку
                    error_message=f"Неожиданная ошибка: {str(e)}"
                )
            except Exception as telegram_error:
                logger.error(f"Ошибка отправки Telegram уведомления: {telegram_error}")

        # Дополнительные проверки для успешных запросов
        if result['success']:
            try:
                await self._perform_additional_checks(result, url)
            except Exception as e:
                logger.warning(f"Additional checks failed for {url}: {str(e)}")
                result['additional_checks']['error'] = str(e)

        return result

    def _analyze_security_headers(self, result: Dict, headers):
        """Анализ security headers"""
        security_headers = {
            'strict-transport-security': headers.get('Strict-Transport-Security'),
            'x-content-type-options': headers.get('X-Content-Type-Options'),
            'x-frame-options': headers.get('X-Frame-Options'),
            'x-xss-protection': headers.get('X-XSS-Protection'),
            'content-security-policy': headers.get('Content-Security-Policy'),
            'referrer-policy': headers.get('Referrer-Policy'),
            'permissions-policy': headers.get('Permissions-Policy'),
            'access-control-allow-origin': headers.get('Access-Control-Allow-Origin'),
            'access-control-allow-methods': headers.get('Access-Control-Allow-Methods'),
        }
        result['security_headers'] = security_headers

    def _analyze_technology_stack(self, result: Dict, headers):
        """Анализ технологического стека по заголовкам"""
        technologies = []

        # Определение технологий по заголовкам
        server = headers.get('Server', '').lower()
        if 'nginx' in server:
            technologies.append('nginx')
        elif 'apache' in server:
            technologies.append('apache')
        elif 'iis' in server:
            technologies.append('iis')

        powered_by = headers.get('X-Powered-By', '').lower()
        if 'php' in powered_by:
            technologies.append('php')
        elif 'asp.net' in powered_by:
            technologies.append('asp.net')
        elif 'node' in powered_by:
            technologies.append('node.js')

        # По заголовкам приложения
        if headers.get('X-Generator'):
            technologies.append(headers.get('X-Generator').split()[0].lower())

        result['technology_stack'] = technologies

    def _analyze_content(self, result: Dict, content: bytes, content_type: str):
        """Анализ содержимого ответа"""
        content_analysis = {}

        try:
            # Для HTML контента
            if 'text/html' in content_type:
                soup = BeautifulSoup(content, 'html.parser')

                # Мета-информация
                content_analysis['title'] = soup.title.string if soup.title else None

                # Мета-теги
                meta_tags = {}
                for meta in soup.find_all('meta'):
                    name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
                    if name:
                        meta_tags[name.lower()] = meta.get('content')
                content_analysis['meta_tags'] = meta_tags

                # Количество элементов
                content_analysis['element_count'] = {
                    'links': len(soup.find_all('a')),
                    'images': len(soup.find_all('img')),
                    'scripts': len(soup.find_all('script')),
                    'stylesheets': len(soup.find_all('link', rel='stylesheet')),
                    'forms': len(soup.find_all('form')),
                }

                # Поиск технологий в контенте
                content_str = content.decode('utf-8', errors='ignore').lower()
                tech_indicators = {
                    'wordpress': ['wp-content', 'wp-includes', 'wordpress'],
                    'drupal': ['drupal', 'sites/all'],
                    'joomla': ['joomla', 'media/jui'],
                    'react': ['react', 'react-dom'],
                    'vue': ['vue.js', 'vue@'],
                    'angular': ['angular', 'ng-'],
                    'jquery': ['jquery', '$().'],
                    'bootstrap': ['bootstrap', 'btn-primary'],
                }

                detected_tech = []
                for tech, indicators in tech_indicators.items():
                    if any(indicator in content_str for indicator in indicators):
                        detected_tech.append(tech)

                result['technology_stack'].extend(detected_tech)
                result['technology_stack'] = list(set(result['technology_stack']))

            # Для JSON контента
            elif 'application/json' in content_type:
                try:
                    json_data = json.loads(content.decode('utf-8'))
                    content_analysis['json_valid'] = True
                    if isinstance(json_data, dict):
                        content_analysis['json_keys'] = list(json_data.keys())
                        content_analysis['json_size'] = len(json.dumps(json_data))
                    else:
                        content_analysis['json_type'] = type(json_data).__name__
                        content_analysis['json_size'] = len(content)
                except:
                    content_analysis['json_valid'] = False

            # Для текстового контента
            elif 'text/' in content_type:
                content_str = content.decode('utf-8', errors='ignore')
                content_analysis['line_count'] = len(content_str.split('\n'))
                content_analysis['word_count'] = len(content_str.split())
                content_analysis['character_count'] = len(content_str)

            # Для XML контента
            elif 'application/xml' in content_type or 'text/xml' in content_type:
                content_str = content.decode('utf-8', errors='ignore')
                content_analysis['xml_size'] = len(content_str)
                content_analysis['has_xml_declaration'] = content_str.startswith('<?xml')

        except Exception as e:
            content_analysis['analysis_error'] = str(e)

        result['content_analysis'] = content_analysis

    async def _perform_additional_checks(self, result: Dict, url: str):
        """Дополнительные проверки"""
        parsed_url = urlparse(url)
        additional_checks = {}

        # Проверка robots.txt
        if parsed_url.scheme and parsed_url.netloc:
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            try:
                async with self.session.get(robots_url, timeout=10) as response:
                    additional_checks['robots_txt'] = {
                        'exists': response.status == 200,
                        'status_code': response.status,
                        'content_type': response.headers.get('Content-Type')
                    }
            except:
                additional_checks['robots_txt'] = {'exists': False}

        # Проверка sitemap.xml
        sitemap_url = f"{parsed_url.scheme}://{parsed_url.netloc}/sitemap.xml"
        try:
            async with self.session.get(sitemap_url, timeout=10) as response:
                additional_checks['sitemap_xml'] = {
                    'exists': response.status == 200,
                    'status_code': response.status,
                    'content_type': response.headers.get('Content-Type')
                }
        except:
            additional_checks['sitemap_xml'] = {'exists': False}

        # Проверка favicon.ico
        favicon_url = f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.ico"
        try:
            async with self.session.get(favicon_url, timeout=10) as response:
                additional_checks['favicon'] = {
                    'exists': response.status == 200,
                    'content_type': response.headers.get('Content-Type'),
                    'size': response.headers.get('Content-Length')
                }
        except:
            additional_checks['favicon'] = {'exists': False}

        result['additional_checks'] = additional_checks

    async def test_multiple_endpoints(self, urls: List[str]) -> List[Dict]:
        """Тестирование множества эндпоинтов"""
        if not self.session:
            await self.init_session()

        tasks = []
        for url in urls:
            task = asyncio.create_task(self.test_endpoint(url))
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Обработка исключений
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'url': urls[i],
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'success': False,
                    'error': str(result),
                    'response_time': None,
                    'status_code': None
                })
            else:
                processed_results.append(result)

        return processed_results


# Упрощенный класс для хранения результатов (без PostgreSQL)
class SimpleResultsStorage:
    @staticmethod
    def save_results_to_file(results: List[Dict], filename: str = "monitoring_results.json"):
        """Сохранение результатов в JSON файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Результаты сохранены в файл: {filename}")


async def monitor_endpoints(urls: List[str]):
    """Основная функция мониторинга эндпоинтов"""
    tester = EndpointTester(max_concurrent=20, timeout=15)

    try:
        # Тестирование эндпоинтов
        logger.info(f"Начинаем тестирование {len(urls)} эндпоинтов...")
        results = await tester.test_multiple_endpoints(urls)

        # Статистика
        successful = sum(1 for r in results if r['success'])
        failed = len(urls) - successful
        avg_response_time = sum(r.get('response_time', 0) for r in results if r['success']) / max(successful, 1)

        logger.info(f"Успешных запросов: {successful}/{len(urls)}")
        logger.info(f"Среднее время ответа: {avg_response_time:.3f}s")

        # Отправляем сводку в Telegram
        try:
            telegram_service.send_monitoring_summary(
                total_urls=len(urls),
                successful=successful,
                failed=failed,
                avg_response_time=avg_response_time if successful > 0 else None
            )
        except Exception as e:
            logger.error(f"Ошибка отправки сводки в Telegram: {e}")

        # Сохранение результатов
        SimpleResultsStorage.save_results_to_file(results)

        return results

    finally:
        await tester.close_session()


# Функция для красивого вывода результатов
def print_detailed_results(results: List[Dict]):
    """Красивый вывод результатов"""
    for i, result in enumerate(results, 1):
        print(f"\n{'=' * 60}")
        print(f"РЕЗУЛЬТАТ #{i}: {result['url']}")
        print(f"{'=' * 60}")

        print(f"✅ Статус: {'УСПЕХ' if result['success'] else 'ОШИБКА'}")
        print(f"📊 Код ответа: {result.get('status_code', 'N/A')}")
        print(f"⏱️  Время ответа: {result.get('response_time', 0):.3f}s")
        print(f"🔒 HTTPS: {'Да' if result.get('is_https') else 'Нет'}")

        if result.get('error'):
            print(f"❌ Ошибка: {result['error']}")

        # Технологии
        if result.get('technology_stack'):
            print(f"🛠️  Технологии: {', '.join(result['technology_stack'])}")

        # Заголовки безопасности
        security_headers = result.get('security_headers', {})
        if any(security_headers.values()):
            print("🔐 Security Headers:")
            for key, value in security_headers.items():
                if value:
                    print(f"   • {key}: {value}")

        # Дополнительные проверки
        checks = result.get('additional_checks', {})
        if checks:
            print("📋 Дополнительные проверки:")
            for check_name, check_data in checks.items():
                exists = check_data.get('exists', False)
                status = "✅ Есть" if exists else "❌ Нет"
                print(f"   • {check_name}: {status}")
