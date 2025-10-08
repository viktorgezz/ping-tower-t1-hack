@echo off
echo 🔄 Перезапуск сервиса анализа логов
echo ================================================

echo.
echo 🛑 Остановка существующих контейнеров...
docker-compose down

echo.
echo 🧹 Очистка старых образов...
docker-compose build --no-cache

echo.
echo 🚀 Запуск с новым портом...
docker-compose up --build -d

echo.
echo ✅ Сервис перезапущен!
echo.
echo 🌐 API доступен по адресу: http://localhost:8001
echo 📖 Документация API: http://localhost:8001/docs
echo.
echo 📋 Полезные команды:
echo   docker-compose logs -f          - просмотр логов
echo   docker-compose down             - остановка сервиса
echo.
pause
