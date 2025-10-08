#!/bin/bash
echo "🚀 Запуск сервиса анализа логов через Docker"
echo "================================================"

echo ""
echo "📦 Сборка и запуск контейнера..."
docker-compose up --build -d

echo ""
echo "✅ Сервис запущен!"
echo ""
echo "🌐 API доступен по адресу: http://localhost:8001"
echo "📖 Документация API: http://localhost:8001/docs"
echo ""
echo "📋 Полезные команды:"
echo "  docker-compose logs -f          - просмотр логов"
echo "  docker-compose down             - остановка сервиса"
echo "  docker-compose restart          - перезапуск сервиса"
echo ""
