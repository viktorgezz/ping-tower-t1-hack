import requests
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
import re
from typing import Set, Dict, List
import time
from collections import deque


class WebsiteCrawler:
    def __init__(self, user_agent: str = None, delay: float = 0.1):
        self.session = requests.Session()
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.delay = delay
        self.visited_urls = set()
        self.internal_urls = set()
        self.media_urls = set()

    def is_same_domain(self, base_url: str, url: str) -> bool:
        """Проверяет, принадлежит ли URL тому же домену"""
        base_domain = urlparse(base_url).netloc
        url_domain = urlparse(url).netloc
        return base_domain == url_domain

    def normalize_url(self, url: str) -> str:
        """Нормализует URL, убирая фрагменты и параметры сортировки"""
        parsed = urlparse(url)
        # Убираем фрагмент (#)
        normalized = parsed._replace(fragment="")
        return urlunparse(normalized)

    def is_media_url(self, url: str) -> bool:
        """Проверяет, является ли URL медиа-файлом"""
        media_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',  # Изображения
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',  # Видео
            '.mp3', '.wav', '.ogg', '.m4a', '.flac',  # Аудио
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',  # Документы
            '.zip', '.rar', '.tar', '.gz',  # Архивы
            '.css', '.js'  # Стили и скрипты
        }

        # Проверяем расширение файла в URL
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()

        # Также проверяем распространенные медиа-пути
        media_patterns = [
            r'/media/', r'/uploads/', r'/images/', r'/videos/',
            r'/audio/', r'/assets/', r'/static/', r'/files/',
            r'/img/', r'/video/', r'/audio/', r'/downloads/'
        ]

        return (any(path.endswith(ext) for ext in media_extensions) or
                any(pattern in path for pattern in media_patterns) or
                'image' in path or 'video' in path or 'audio' in path)

    def extract_urls_from_page(self, url: str, html_content: str) -> Set[str]:
        """Извлекает все URL со страницы"""
        # Используем встроенный парсер 'html.parser' вместо 'lxml'
        soup = BeautifulSoup(html_content, 'html.parser')
        urls = set()

        # Извлекаем все ссылки
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and not href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                absolute_url = urljoin(url, href)
                urls.add(absolute_url)

        # Извлекаем медиа-ссылки
        for img in soup.find_all('img', src=True):
            src = img.get('src') or img.get('data-src')
            if src:
                media_url = urljoin(url, src)
                urls.add(media_url)

        # Извлекаем CSS и JS файлы
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                resource_url = urljoin(url, src)
                urls.add(resource_url)

        for link in soup.find_all('link', href=True):
            href = link.get('href')
            if href and ('stylesheet' in link.get('rel', []) or 'icon' in link.get('rel', [])):
                resource_url = urljoin(url, href)
                urls.add(resource_url)

        # Извлекаем видео и аудио
        for media in soup.find_all(['video', 'audio', 'source'], src=True):
            src = media.get('src')
            if src:
                media_url = urljoin(url, src)
                urls.add(media_url)

        return urls

    def should_visit_url(self, url: str, base_url: str) -> bool:
        """Определяет, стоит ли посещать URL"""
        # Пропускаем пустые URL
        if not url or url.strip() == '':
            return False

        # Пропускаем якорные ссылки и специальные протоколы
        if url.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
            return False

        # Пропускаем внешние домены
        if not self.is_same_domain(base_url, url):
            return False

        # Пропускаем медиа-файлы (их не нужно сканировать рекурсивно)
        if self.is_media_url(url):
            return False

        # Пропускаем уже посещенные URL
        if url in self.visited_urls:
            return False

        return True

    def crawl_website(self, start_url: str, max_pages: int = 100) -> Dict[str, List[str]]:
        """Основной метод для сканирования сайта"""
        # Нормализуем стартовый URL
        start_url = self.normalize_url(start_url)
        queue = deque([start_url])
        self.internal_urls.add(start_url)

        while queue and len(self.visited_urls) < max_pages:
            current_url = queue.popleft()

            if current_url in self.visited_urls:
                continue

            try:
                print(f"Обрабатывается: {current_url}")

                headers = {'User-Agent': self.user_agent}
                response = self.session.get(current_url, headers=headers, timeout=10)
                response.raise_for_status()

                # Проверяем, что это HTML страница
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' not in content_type:
                    self.visited_urls.add(current_url)
                    continue

                self.visited_urls.add(current_url)

                # Извлекаем все URL со страницы
                found_urls = self.extract_urls_from_page(current_url, response.text)

                for url in found_urls:
                    normalized_url = self.normalize_url(url)

                    # Добавляем медиа-файлы
                    if self.is_media_url(normalized_url):
                        self.media_urls.add(normalized_url)

                    # Добавляем внутренние ссылки в очередь для сканирования
                    elif self.should_visit_url(normalized_url, start_url):
                        if normalized_url not in queue and normalized_url not in self.visited_urls:
                            queue.append(normalized_url)
                            self.internal_urls.add(normalized_url)

                time.sleep(self.delay)

            except requests.RequestException as e:
                print(f"Ошибка при обработке {current_url}: {e}")
                self.visited_urls.add(current_url)
                continue
            except Exception as e:
                print(f"Неожиданная ошибка при обработке {current_url}: {e}")
                self.visited_urls.add(current_url)
                continue

        # Убираем стартовый URL из внутренних, если нужно
        self.internal_urls.discard(start_url)

        return {
            'internal_urls': sorted(list(self.internal_urls)),
            'media_urls': sorted(list(self.media_urls)),
            'visited_pages': len(self.visited_urls)
        }


# Сервисный класс для удобного использования
class URLService:
    @staticmethod
    def extract_urls(url: str, max_pages: int = 50) -> Dict[str, List[str]]:
        """Основной метод сервиса для извлечения URL"""
        crawler = WebsiteCrawler(delay=0.3)  # Увеличиваем задержку для безопасности
        return crawler.crawl_website(url, max_pages)

    @staticmethod
    def save_results(results: Dict[str, List[str]], filename: str = "urls_results.txt"):
        """Сохраняет результаты в файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=== ВНУТРЕННИЕ URL ===\n")
            for url in results['internal_urls']:
                f.write(f"{url}\n")

            f.write("\n=== МЕДИА-ФАЙЛЫ ===\n")
            for url in results['media_urls']:
                f.write(f"{url}\n")

            f.write(f"\nВсего обработано страниц: {results['visited_pages']}\n")
            f.write(f"Найдено внутренних URL: {len(results['internal_urls'])}\n")
            f.write(f"Найдено медиа-файлов: {len(results['media_urls'])}\n")


# Альтернативный упрощенный вариант для быстрого сканирования
class SimpleURLScanner:
    @staticmethod
    def scan_url(url: str, max_depth: int = 2) -> Dict[str, List[str]]:
        """Упрощенный сканер для быстрого получения результатов"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            internal_urls = set()
            media_urls = set()

            # Собираем все ссылки
            for link in soup.find_all(['a', 'img', 'script', 'link'], href=True):
                href = link.get('href')
                if href:
                    absolute_url = urljoin(url, href)
                    if SimpleURLScanner.is_media_url(absolute_url):
                        media_urls.add(absolute_url)
                    else:
                        internal_urls.add(absolute_url)

            for media in soup.find_all(['img', 'script', 'source'], src=True):
                src = media.get('src')
                if src:
                    absolute_url = urljoin(url, src)
                    if SimpleURLScanner.is_media_url(absolute_url):
                        media_urls.add(absolute_url)

            return {
                'internal_urls': sorted(list(internal_urls)),
                'media_urls': sorted(list(media_urls)),
                'visited_pages': 1
            }

        except Exception as e:
            print(f"Ошибка: {e}")
            return {'internal_urls': [], 'media_urls': [], 'visited_pages': 0}

    @staticmethod
    def is_media_url(url: str) -> bool:
        media_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.mp4', '.mp3', '.pdf'}
        return any(url.lower().endswith(ext) for ext in media_extensions)
