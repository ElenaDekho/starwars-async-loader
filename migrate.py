# migrate.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from models import Base

# Путь к БД
DATABASE_URL = "sqlite+aiosqlite:///starwars.db"

async def migrate():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        # create_all безопасно: создаст таблицу, только если её нет
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Миграция завершена: таблица 'characters' готова")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())