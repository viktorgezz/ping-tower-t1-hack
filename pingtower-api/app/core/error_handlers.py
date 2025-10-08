from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Коды ошибок согласно API спецификации
class ErrorCodes:
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    INVALID_INPUT = "INVALID_INPUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"

def create_error_response(code: str, message: str, details: dict = None) -> dict:
    """Создание стандартизированного ответа об ошибке"""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {}
        }
    }

def setup_error_handlers(app: FastAPI):
    """Настройка обработчиков ошибок"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Обработка HTTP исключений"""
        logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        
        # Маппинг HTTP статусов на коды ошибок API
        status_code_mapping = {
            400: ErrorCodes.INVALID_INPUT,
            401: ErrorCodes.AUTHENTICATION_FAILED,
            403: ErrorCodes.PERMISSION_DENIED,
            404: ErrorCodes.RESOURCE_NOT_FOUND,
            500: ErrorCodes.INTERNAL_ERROR
        }
        
        error_code = status_code_mapping.get(exc.status_code, ErrorCodes.INTERNAL_ERROR)
        
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                code=error_code,
                message=str(exc.detail),
                details={"status_code": exc.status_code}
            )
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_exception_handler(request: Request, exc: StarletteHTTPException):
        """Обработка Starlette HTTP исключений"""
        logger.error(f"Starlette Exception: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                code=ErrorCodes.INTERNAL_ERROR,
                message=str(exc.detail),
                details={"status_code": exc.status_code}
            )
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Обработка ошибок валидации"""
        logger.error(f"Validation Error: {exc.errors()}")
        
        # Форматирование ошибок валидации
        error_details = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            error_details.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=400,
            content=create_error_response(
                code=ErrorCodes.INVALID_INPUT,
                message="Validation error",
                details={"validation_errors": error_details}
            )
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Обработка общих исключений"""
        logger.error(f"Unhandled Exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                code=ErrorCodes.INTERNAL_ERROR,
                message="Internal server error",
                details={"exception_type": type(exc).__name__}
            )
        )

def setup_middleware(app: FastAPI):
    """Настройка middleware"""
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Middleware для логирования HTTP запросов"""
        import time
        start_time = time.time()
        
        # Логирование входящего запроса
        logger.info(f"Request: {request.method} {request.url}")
        
        # Обработка запроса
        response = await call_next(request)
        
        # Вычисление времени обработки
        process_time = time.time() - start_time
        
        # Логирование ответа
        logger.info(
            f"Response: {response.status_code} - "
            f"Process time: {process_time:.4f}s"
        )
        
        # Добавление заголовка с временем обработки
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
