import asyncio
import aiohttp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Character, Base

DATABASE_URL = "sqlite:///starwars.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


async def fetch_planet_name(session, planet_url):
    """Получает название планеты по URL"""
    async with session.get(planet_url) as resp:
        if resp.status == 200:
            data = await resp.json()
            return data.get('name')
    return None


async def fetch_character(session, person_id):
    url = f"https://swapi.dev/api/people/{person_id}/"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            planet_url = data.get('homeworld')
            planet_name = None
            if planet_url:
                planet_name = await fetch_planet_name(session, planet_url)
            return {
                'id': int(data['url'].split('/')[-2]),
                'birth_year': data.get('birth_year'),
                'eye_color': data.get('eye_color'),
                'gender': data.get('gender'),
                'hair_color': data.get('hair_color'),
                'homeworld': planet_name,
                'mass': data.get('mass'),
                'name': data.get('name'),
                'skin_color': data.get('skin_color'),
            }
    return None


async def save_to_db(characters_data):
    db = SessionLocal()
    for data in characters_data:
        if data and 'name' in data:
            character = Character(**data)
            db.add(character)
    db.commit()
    db.close()
    print(f"Сохранено {len(characters_data)} персонажей")


async def main():
    init_db()
    async with aiohttp.ClientSession() as session:
        total_ids = range(1, 83)
        batch_size = 10

        for i in range(0, len(total_ids), batch_size):
            batch = total_ids[i:i + batch_size]
            tasks = [fetch_character(session, pid) for pid in batch]
            results = await asyncio.gather(*tasks)

            valid_results = [r for r in results if r and 'name' in r]
            if valid_results:
                await save_to_db(valid_results)
                await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())