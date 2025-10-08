from app.core.database import engine, Base
from app.models import user, resource, notification

def init_db():
    """Инициализация базы данных - создание всех таблиц"""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("База данных инициализирована!")
