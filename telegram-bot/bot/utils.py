from datetime import datetime


def format_alert_message(alert_data: dict) -> str:
    """Форматирование сообщения об уведомлении"""
    status = alert_data.get('status', 'UNKNOWN')

    status_emoji = "🔴" if status in ['DOWN', 'ERROR', 'FAILED'] else \
        "🟡" if status in ['DEGRADED', 'WARNING'] else \
            "🟢" if status == 'UP' else "⚪"

    return (
        f"{status_emoji} *PingTower Alert*\n\n"
        f"*Ресурс:* {alert_data.get('resource_name', 'Unknown')}\n"
        f"*Статус:* {status}\n"
        f"*Время:* {alert_data.get('timestamp', datetime.now().isoformat())}\n"
        f"*Сообщение:* {alert_data.get('message', 'No details')}\n\n"
        f"Проверить: https://pingtower.ru/resources/{alert_data.get('resource_id', '')}"
    )