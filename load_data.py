# load_data_async.py
import asyncio
import aiohttp
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Character(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    birth_year = Column(String)
    eye_color = Column(String)
    gender = Column(String)
    hair_color = Column(String)
    homeworld = Column(String)
    mass = Column(String)
    name = Column(String)
    skin_color = Column(String)


DATABASE_URL = "sqlite+aiosqlite:///starwars.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def fetch_with_retry(session, url, max_retries=3, timeout=15):
    """Запрос с повторными попытками при ошибке"""
    for attempt in range(max_retries):
        try:
            async with session.get(url, timeout=timeout) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    print(f"⚠️  Статус {resp.status} для {url}")
        except asyncio.TimeoutError:
            print(f"⏱️  Таймаут ({attempt + 1}/{max_retries}): {url}")
        except aiohttp.ClientError as e:
            print(f"🌐 Ошибка сети ({attempt + 1}/{max_retries}): {e}")
        except Exception as e:
            print(f"❌ Ошибка ({attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            await asyncio.sleep(1 * (attempt + 1))  # экспоненциальная пауза

    return None


async def fetch_planet_name(session, planet_url):
    """Получить название планеты по URL"""
    if not planet_url:
        return None
    data = await fetch_with_retry(session, planet_url)
    if data:
        return data.get('result', {}).get('properties', {}).get('name')
    return None


async def fetch_character(session, person_id):
    """Получить данные персонажа по ID"""
    url = f"https://www.swapi.tech/api/people/{person_id}/"
    data = await fetch_with_retry(session, url)

    if data:
        props = data.get('result', {}).get('properties', {})
        planet_url = props.get('homeworld')
        planet_name = await fetch_planet_name(session, planet_url) if planet_url else None

        return {
            'id': int(data.get('result', {}).get('uid', person_id)),
            'birth_year': props.get('birth_year'),
            'eye_color': props.get('eye_color'),
            'gender': props.get('gender'),
            'hair_color': props.get('hair_color'),
            'homeworld': planet_name,
            'mass': props.get('mass'),
            'name': props.get('name'),
            'skin_color': props.get('skin_color'),
        }
    return None


async def save_to_db(characters_data):
    """Асинхронное сохранение"""
    async with AsyncSessionLocal() as db:
        for data in characters_data:
            if data and data.get('name'):
                existing = await db.get(Character, data['id'])
                if not existing:
                    db.add(Character(**data))
        await db.commit()
        print(f"💾 Сохранено: {len(characters_data)}")


async def main():
    # Создаём таблицу
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with aiohttp.ClientSession() as session:
        # Получаем список всех персонажей через пагинацию
        all_people = []
        page_url = "https://www.swapi.tech/api/people/"
        page_num = 1

        while page_url:
            print(f"📄 Загрузка страницы {page_num}...")
            data = await fetch_with_retry(session, page_url)

            if not data:
                print(f"❌ Не удалось загрузить страницу {page_num}, пробуем дальше...")
                page_num += 1
                # Пробуем сформировать следующую страницу вручную
                page_url = f"https://www.swapi.tech/api/people?page={page_num}&limit=10"
                if page_num > 10:  # защита от бесконечного цикла
                    break
                continue

            results = data.get('results', [])
            all_people.extend(results)
            print(f"✅ Страница {page_num}: найдено {len(results)}, всего: {len(all_people)}")

            page_url = data.get('next')
            page_num += 1
            await asyncio.sleep(0.5)  # пауза между страницами

        print(f"🎯 Всего персонажей для загрузки: {len(all_people)}")

        # Загружаем детали каждого персонажа пачками
        batch_size = 3
        for i in range(0, len(all_people), batch_size):
            batch = all_people[i:i + batch_size]
            tasks = []
            for person in batch:
                pid = person.get('url', '').strip('/').split('/')[-1]
                if pid.isdigit():
                    tasks.append(fetch_character(session, int(pid)))

            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                valid = [r for r in results if isinstance(r, dict) and r.get('name')]
                if valid:
                    await save_to_db(valid)

            await asyncio.sleep(0.5)  # пауза между пачками

    print("✅ Загрузка завершена!")


if __name__ == '__main__':
    asyncio.run(main())