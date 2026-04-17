# check_db.py
import sqlite3


def check_database():
    conn = sqlite3.connect('starwars.db')
    conn.row_factory = sqlite3.Row  # чтобы обращаться к полям по имени
    cursor = conn.cursor()

    print("🔍 ПРОВЕРКА БАЗЫ ДАННЫХ")
    print("=" * 50)

    # 1️⃣ Общее количество
    cursor.execute("SELECT COUNT(*) FROM characters")
    total = cursor.fetchone()[0]
    print(f"📊 Всего записей: {total}")
    print(f"{'✅' if total == 82 else '⚠️'} Ожидается: 82")
    print()

    # 2️⃣ Первые 5 персонажей
    print("🎬 Первые 5 персонажей:")
    cursor.execute("SELECT id, name, homeworld FROM characters LIMIT 5")
    for row in cursor.fetchall():
        print(f"  {row['id']}. {row['name']} — {row['homeworld']}")
    print()

    # 3️⃣ Проверка на дубликаты
    cursor.execute("SELECT id, COUNT(*) as cnt FROM characters GROUP BY id HAVING cnt > 1")
    duplicates = cursor.fetchall()
    if duplicates:
        print(f"⚠️  Найдены дубликаты ID: {[d['id'] for d in duplicates]}")
    else:
        print("✅ Дубликатов нет")
    print()

    # 4️⃣ Выборочная проверка отдельных персонажей
    print("🔎 Выборочная проверка персонажей:")
    sample_ids = [1, 10, 42, 82]  # Luke, Obi-Wan, случайный, последний
    for pid in sample_ids:
        cursor.execute("SELECT * FROM characters WHERE id = ?", (pid,))
        char = cursor.fetchone()
        if char:
            print(f"\n  👤 ID {char['id']}: {char['name']}")
            print(f"     🪐 Планета: {char['homeworld']}")
            print(f"     👁️  Цвет глаз: {char['eye_color']}")
            print(f"     💇 Цвет волос: {char['hair_color']}")
            print(f"     ⚧ Пол: {char['gender']}")
            print(f"     📏 Рост: {char['height'] if 'height' in char.keys() else 'N/A'}")
            print(f"     ⚖️  Масса: {char['mass']}")
            print(f"     🎂 Год рождения: {char['birth_year']}")
            print(f"     🎨 Цвет кожи: {char['skin_color']}")

            # Проверка: homeworld — это имя, а не URL?
            if char['homeworld'] and ('http' in str(char['homeworld'])):
                print(f"     ⚠️  homeworld содержит URL, а не название!")
            elif not char['homeworld']:
                print(f"     ⚠️  homeworld пустой")
            else:
                print(f"     ✅ homeworld — корректное название")
        else:
            print(f"\n  ❌ Персонаж с ID {pid} не найден")
    print()

    # 5️⃣ Статистика по пустым полям
    print("📋 Статистика заполненности полей:")
    fields = ['name', 'homeworld', 'gender', 'eye_color', 'hair_color', 'mass', 'birth_year', 'skin_color']
    for field in fields:
        cursor.execute(f"SELECT COUNT(*) FROM characters WHERE {field} IS NOT NULL AND {field} != ''")
        filled = cursor.fetchone()[0]
        percent = round(filled / total * 100) if total > 0 else 0
        status = '✅' if percent > 90 else '⚠️' if percent > 50 else '❌'
        print(f"  {status} {field:12} — заполнено: {filled}/{total} ({percent}%)")
    print()

    # 6️⃣ Уникальные планеты
    cursor.execute("SELECT COUNT(DISTINCT homeworld) FROM characters WHERE homeworld IS NOT NULL")
    unique_planets = cursor.fetchone()[0]
    print(f"🪐 Уникальных планет: {unique_planets}")

    # Покажем топ-5 планет по количеству персонажей
    print("\n🏆 Топ-5 планет по количеству персонажей:")
    cursor.execute("""
        SELECT homeworld, COUNT(*) as cnt 
        FROM characters 
        WHERE homeworld IS NOT NULL 
        GROUP BY homeworld 
        ORDER BY cnt DESC 
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  • {row['homeworld']}: {row['cnt']} персонажей")

    print("\n" + "=" * 50)
    if total == 82:
        print("БАЗА ЗАПОЛНЕНА КОРРЕКТНО")
    else:
        print("Есть расхождения — проверь загрузку")

    conn.close()


if __name__ == '__main__':
    check_database()