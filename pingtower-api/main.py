from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, resources, logs, user
from app.core.config import settings
from app.core.error_handlers import setup_error_handlers, setup_middleware

app = FastAPI(
    title="PingTower API",
    description="Облачный инструмент для мониторинга доступности сайтов и сервисов",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"  # Явно указываем путь
)

# CORS middleware - разрешаем все для Swagger
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка обработчиков ошибок и middleware
setup_error_handlers(app)
setup_middleware(app)

# Подключение роутеров
app.include_router(auth.router, prefix="/auth", tags=["Аутентификация"])
app.include_router(resources.router, prefix="/resources", tags=["Ресурсы"])
app.include_router(logs.router, prefix="/logs", tags=["Логи"])
app.include_router(user.router, prefix="/user", tags=["Пользователь"])

@app.get("/")
async def root():
    return {"message": "PingTower API v1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Явный эндпоинт для OpenAPI (на всякий случай)
@app.get("/openapi.json")
async def get_openapi():
    return app.openapi()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)