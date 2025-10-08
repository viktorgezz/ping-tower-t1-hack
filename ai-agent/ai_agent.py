import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import statistics

class LogAnalyzer:
    """
    AI агент для анализа логов сервисов
    """
    
    def __init__(self):
        self.error_patterns = {
            "timeout": ["timeout", "timed out", "connection timeout"],
            "connection": ["connection refused", "connection reset", "connection error"],
            "ssl": ["ssl", "tls", "certificate", "handshake"],
            "dns": ["dns", "name resolution", "host not found"],
            "http": ["404", "500", "502", "503", "504", "bad gateway", "service unavailable"],
            "redirect": ["too many redirects", "redirect loop"],
            "content": ["content error", "parsing error", "invalid response"]
        }
    
    async def analyze_logs(self, logs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Анализирует логи и возвращает результат анализа
        """
        # Проверяем наличие ошибок (success может быть 0/1 или True/False)
        error_logs = []
        for log in logs_data:
            success = log.get('success', True)
            # Обрабатываем разные типы данных для success
            if isinstance(success, (int, str)):
                success = bool(int(success))
            if not success:
                error_logs.append(log)
        
        if error_logs:
            return await self._analyze_errors(error_logs, logs_data)
        else:
            return await self._analyze_successful_service(logs_data)
    
    async def _analyze_errors(self, error_logs: List[Dict[str, Any]], all_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Анализирует ошибки в логах
        """
        # Извлекаем ошибки
        errors = []
        for log in error_logs:
            if log.get('error'):
                errors.append(log['error'])
        
        # Группируем ошибки по типам
        error_categories = self._categorize_errors(errors)
        
        # Анализируем паттерны ошибок
        error_analysis = self._analyze_error_patterns(error_logs, all_logs)
        
        # Генерируем рекомендации
        recommendations = self._generate_recommendations(error_categories, error_logs)
        
        return {
            "type": "errors",
            "data": {
                "errors": errors[:10],  # Показываем максимум 10 ошибок
                "error_analysis": error_analysis,
                "recommendations": recommendations
            }
        }
    
    async def _analyze_successful_service(self, logs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Анализирует успешно работающий сервис
        """
        # Вычисляем метрики с безопасным преобразованием типов
        response_times = []
        for log in logs_data:
            rt = log.get('response_time')
            if rt is not None:
                try:
                    response_times.append(float(rt))
                except (ValueError, TypeError):
                    continue
        
        status_codes = []
        for log in logs_data:
            sc = log.get('status_code')
            if sc is not None:
                try:
                    status_codes.append(int(sc))
                except (ValueError, TypeError):
                    continue
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        # Анализируем статус коды
        status_distribution = {}
        for status in status_codes:
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # Генерируем характеристику
        characteristics = self._generate_service_characteristics(
            avg_response_time, max_response_time, min_response_time, 
            status_distribution, len(logs_data)
        )
        
        return {
            "type": "status",
            "data": {
                "general_characteristics": characteristics
            }
        }
    
    def _categorize_errors(self, errors: List[str]) -> Dict[str, List[str]]:
        """
        Категоризирует ошибки по типам
        """
        categories = {}
        
        for error in errors:
            error_lower = error.lower()
            categorized = False
            
            for category, patterns in self.error_patterns.items():
                if any(pattern in error_lower for pattern in patterns):
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(error)
                    categorized = True
                    break
            
            if not categorized:
                if "other" not in categories:
                    categories["other"] = []
                categories["other"].append(error)
        
        return categories
    
    def _analyze_error_patterns(self, error_logs: List[Dict[str, Any]], all_logs: List[Dict[str, Any]]) -> str:
        """
        Анализирует паттерны ошибок и генерирует объяснение
        """
        total_checks = len(all_logs)
        error_count = len(error_logs)
        error_rate = (error_count / total_checks) * 100 if total_checks > 0 else 0
        
        # Анализируем временные паттерны с безопасным преобразованием
        error_times = []
        for log in error_logs:
            timestamp = log.get('timestamp')
            if timestamp:
                try:
                    # Обрабатываем разные форматы timestamp
                    if isinstance(timestamp, str):
                        # Убираем 'Z' и добавляем '+00:00' если нужно
                        ts_str = timestamp.replace('Z', '+00:00')
                        if '+' not in ts_str and 'Z' not in timestamp:
                            ts_str += '+00:00'
                        error_times.append(datetime.fromisoformat(ts_str))
                    elif isinstance(timestamp, datetime):
                        error_times.append(timestamp)
                except (ValueError, TypeError):
                    continue
        error_times.sort()
        
        # Проверяем на концентрацию ошибок во времени
        if len(error_times) > 1:
            time_span = (error_times[-1] - error_times[0]).total_seconds()
            if time_span < 3600:  # Менее часа
                time_pattern = "Ошибки сконцентрированы в коротком временном промежутке"
            else:
                time_pattern = "Ошибки распределены во времени"
        else:
            time_pattern = "Единичная ошибка"
        
        # Анализируем типы ошибок
        error_categories = self._categorize_errors([log.get('error', '') for log in error_logs])
        main_category = max(error_categories.keys(), key=lambda k: len(error_categories[k])) if error_categories else "unknown"
        
        analysis = f"Обнаружено {error_count} ошибок из {total_checks} проверок ({error_rate:.1f}% отказов). {time_pattern}. "
        
        if main_category == "timeout":
            analysis += "Основная проблема связана с таймаутами соединений, что может указывать на перегрузку сервера или сетевые проблемы."
        elif main_category == "connection":
            analysis += "Преобладают ошибки соединения, возможно сервер недоступен или перегружен."
        elif main_category == "ssl":
            analysis += "Проблемы с SSL/TLS соединением, возможно истек срок действия сертификата или проблемы с конфигурацией."
        elif main_category == "http":
            analysis += "HTTP ошибки указывают на проблемы на стороне сервера или неправильную конфигурацию."
        else:
            analysis += f"Основной тип ошибок: {main_category}."
        
        return analysis
    
    def _generate_recommendations(self, error_categories: Dict[str, List[str]], error_logs: List[Dict[str, Any]]) -> str:
        """
        Генерирует рекомендации по устранению ошибок
        """
        recommendations = []
        
        if "timeout" in error_categories:
            recommendations.append("Увеличьте таймауты соединения и проверьте производительность сервера")
        
        if "connection" in error_categories:
            recommendations.append("Проверьте доступность сервера и настройки сетевого подключения")
        
        if "ssl" in error_categories:
            recommendations.append("Обновите SSL сертификаты и проверьте конфигурацию TLS")
        
        if "http" in error_categories:
            recommendations.append("Проверьте логи сервера и убедитесь в корректности конфигурации веб-сервера")
        
        if "dns" in error_categories:
            recommendations.append("Проверьте настройки DNS и убедитесь в корректности доменного имени")
        
        if "redirect" in error_categories:
            recommendations.append("Проверьте настройки редиректов и избегайте циклических перенаправлений")
        
        if not recommendations:
            recommendations.append("Проанализируйте логи сервера для получения более детальной информации об ошибках")
        
        return "Рекомендации: " + "; ".join(recommendations) + "."
    
    def _generate_service_characteristics(self, avg_response_time: float, max_response_time: float, 
                                        min_response_time: float, status_distribution: Dict[int, int], 
                                        total_checks: int) -> str:
        """
        Генерирует характеристику успешно работающего сервиса
        """
        # Оцениваем производительность
        if avg_response_time < 200:
            perf_desc = "отличная"
        elif avg_response_time < 500:
            perf_desc = "хорошая"
        elif avg_response_time < 1000:
            perf_desc = "удовлетворительная"
        else:
            perf_desc = "требует оптимизации"
        
        # Анализируем стабильность
        if max_response_time / avg_response_time < 2:
            stability_desc = "стабильная"
        else:
            stability_desc = "нестабильная"
        
        # Проверяем статус коды
        success_codes = sum(count for status, count in status_distribution.items() if 200 <= status < 300)
        success_rate = (success_codes / total_checks) * 100 if total_checks > 0 else 0
        
        if success_rate >= 99:
            reliability_desc = "высокая надежность"
        elif success_rate >= 95:
            reliability_desc = "хорошая надежность"
        else:
            reliability_desc = "средняя надежность"
        
        return f"Сервис работает стабильно с {reliability_desc} ({success_rate:.1f}% успешных запросов). Производительность {perf_desc} (среднее время отклика {avg_response_time:.0f}мс), {stability_desc} работа."
