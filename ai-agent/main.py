from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
from datetime import datetime, timedelta
import clickhouse_connect
from ai_agent import LogAnalyzer
from config import settings
from adaptive_query import AdaptiveClickHouseClient

app = FastAPI(title="Service Log Analyzer", version="1.0.0")

# Модели данных
class AnalysisRequest(BaseModel):
    url: str
    check_count: int = settings.DEFAULT_CHECK_COUNT

class ErrorAnalysis(BaseModel):
    errors: Optional[List[str]] = None
    error_analysis: Optional[str] = None
    recommendations: Optional[str] = None

class ServiceStatus(BaseModel):
    general_characteristics: Optional[str] = None

class AnalysisResponse(BaseModel):
    url: str
    analysis_type: str  # "errors" или "status"
    data: Dict[str, Any]

# Инициализация клиента ClickHouse
def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host=settings.CLICKHOUSE_HOST,
        port=settings.CLICKHOUSE_PORT,
        database=settings.CLICKHOUSE_DATABASE,
        username=settings.CLICKHOUSE_USER,
        password=settings.CLICKHOUSE_PASSWORD
    )

# Инициализация AI агента и адаптивного клиента
log_analyzer = LogAnalyzer()
adaptive_client = AdaptiveClickHouseClient()

@app.get("/")
async def root():
    return {"message": "Service Log Analyzer API"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_service_logs(request: AnalysisRequest):
    """
    Анализирует логи сервиса на основе последних N проверок
    """
    try:
        # Валидация количества проверок
        if request.check_count > settings.MAX_CHECK_COUNT:
            raise HTTPException(
                status_code=400, 
                detail=f"Maximum check count is {settings.MAX_CHECK_COUNT}"
            )
        
        # Получаем данные из ClickHouse с адаптивным запросом
        try:
            logs_data, used_columns = adaptive_client.get_checks_data(
                url=request.url, 
                limit=request.check_count
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        if not logs_data:
            raise HTTPException(status_code=404, detail=f"No data found for URL: {request.url}")
        
        # Анализируем данные с помощью AI агента
        analysis_result = await log_analyzer.analyze_logs(logs_data)
        
        return AnalysisResponse(
            url=request.url,
            analysis_type=analysis_result["type"],
            data=analysis_result["data"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    try:
        client = get_clickhouse_client()
        client.command("SELECT 1")
        return {"status": "healthy", "clickhouse": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "clickhouse": "disconnected", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
