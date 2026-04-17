# Star Wars Data Loader

Асинхронный скрипт для загрузки данных о персонажах Star Wars из публичного API (`swapi.dev`) в базу данных SQLite.

## Задача

- Выгрузить всех персонажей из API
- Сохранить следующие поля: `id`, `birth_year`, `eye_color`, `gender`, `hair_color`, `homeworld`, `mass`, `name`, `skin_color`
- Поле `homeworld` преобразовать из URL в название планеты
- Загрузка должна быть асинхронной
- Результат сохранить в любую базу данных

## Используемые технологии

- Python 3.13
- `aiohttp` — асинхронные HTTP-запросы
- `SQLAlchemy` — ORM для работы с SQLite

## Установка и запуск

1. Клонировать репозиторий и перейти в папку проекта:

git clone <url>
cd starwars_async

2. Установить зависимости:

pip install -r requirements.txt

3. Запустить скрипт:

python load_data_fast.py

После выполнения появится файл starwars.db с таблицей characters, содержащей всех персонажей.

# Структура проекта

load_data_fast.py — основной скрипт (миграция + загрузка данных)

models.py — описание модели Character

requirements.txt — зависимости

starwars.db — база данных SQLite (создаётся автоматически)

# Пример данных

SELECT id, name, homeworld FROM characters LIMIT 5;

Результат:

id	            name	            homeworld
1	            Luke Skywalker	    Tatooine
2	            C-3PO	            Tatooine
3	            R2-D2	            Naboo
4	            Darth Vader	        Tatooine
5	            Leia Organa	        Alderaan

# Примечания

API Star Wars (swapi.dev) имеет ограничения на частоту запросов, поэтому загрузка происходит пачками с задержкой.

В базе данных может оказаться 81 или 82 персонажа в зависимости от доступности некоторых ID в API.

