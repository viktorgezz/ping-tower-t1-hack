#!/usr/bin/env python3
"""
Скрипт для проверки данных в таблицах мониторинга
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import UserSelectedEndpoint
from app.models.resource import Endpoint, Resource
from sqlalchemy import text

def check_database_data():
    """Проверка данных в базе данных"""
    db = SessionLocal()
    
    try:
        print("🔍 Проверка данных в базе данных")
        print("=" * 50)
        
        # 1. Проверяем таблицу resources
        resources = db.query(Resource).all()
        print(f"📊 Ресурсы (resources): {len(resources)}")
        for resource in resources:
            print(f"  - ID: {resource.id}, Name: {resource.name}, URL: {resource.url}")
        
        print()
        
        # 2. Проверяем таблицу endpoints
        endpoints = db.query(Endpoint).all()
        print(f"📊 Эндпоинты (endpoints): {len(endpoints)}")
        for endpoint in endpoints:
            print(f"  - ID: {endpoint.id}, Resource: {endpoint.resource_id}, Path: {endpoint.path}, Method: {endpoint.method}")
        
        print()
        
        # 3. Проверяем таблицу user_selected_endpoints
        selected_endpoints = db.query(UserSelectedEndpoint).all()
        print(f"📊 Выбранные эндпоинты (user_selected_endpoints): {len(selected_endpoints)}")
        for selected in selected_endpoints:
            print(f"  - ID: {selected.id}, User: {selected.user_id}, Endpoint: {selected.endpoint_id}, Active: {selected.is_active}")
        
        print()
        
        # 4. Проверяем JOIN запрос (как в задаче мониторинга)
        query = db.query(
            UserSelectedEndpoint,
            Endpoint,
            Resource
        ).join(
            Endpoint, UserSelectedEndpoint.endpoint_id == Endpoint.id
        ).join(
            Resource, Endpoint.resource_id == Resource.id
        ).filter(
            UserSelectedEndpoint.is_active == True
        ).all()
        
        print(f"📊 Активные эндпоинты для мониторинга: {len(query)}")
        for user_selected, endpoint, resource in query:
            print(f"  - User: {user_selected.user_id}")
            print(f"    Resource: {resource.name} ({resource.url})")
            print(f"    Endpoint: {endpoint.method} {endpoint.path}")
            print(f"    Full URL: {resource.url.rstrip('/')}/{endpoint.path.lstrip('/')}")
            print()
        
        # 5. Проверяем SQL запросом
        print("📊 SQL запрос для проверки:")
        result = db.execute(text("""
            SELECT 
                use.id as user_selected_id,
                e.id as endpoint_id,
                r.id as resource_id,
                r.url as resource_url,
                e.path as endpoint_path,
                e.method as endpoint_method,
                use.user_id,
                use.is_active
            FROM user_selected_endpoints use
            JOIN endpoints e ON use.endpoint_id = e.id
            JOIN resources r ON e.resource_id = r.id
            WHERE use.is_active = true
        """))
        
        rows = result.fetchall()
        print(f"SQL результат: {len(rows)} записей")
        for row in rows:
            print(f"  - {dict(row._mapping)}")
        
    except Exception as e:
        print(f"❌ Ошибка при проверке БД: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_database_data()
