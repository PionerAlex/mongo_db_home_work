import json
import os  

from pymongo import MongoClient  # ty:ignore[unresolved-import]
from datetime import datetime, timedelta
from pprint import pprint

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["my_database"]
collection = db["user_events"]
collection_archived = db["archived_users"]

# Список документов
data = [
    {
        "user_id": 123,
        "event_type": "purchase",
        "event_time": datetime(2024, 1, 20, 10, 0, 0),
        "user_info": {
            "email": "user1@example.com",
            "registration_date": datetime(2023, 12, 1, 10, 0, 0),
        },
    },
    {
        "user_id": 124,
        "event_type": "login",
        "event_time": datetime(2024, 1, 21, 9, 30, 0),
        "user_info": {
            "email": "user2@example.com",
            "registration_date": datetime(2023, 12, 2, 12, 0, 0),
        },
    },
    {
        "user_id": 125,
        "event_type": "signup",
        "event_time": datetime(2024, 1, 19, 14, 15, 0),
        "user_info": {
            "email": "user3@example.com",
            "registration_date": datetime(2023, 12, 3, 11, 45, 0),
        },
    },
    {
        "user_id": 126,
        "event_type": "purchase",
        "event_time": datetime(2024, 1, 20, 16, 0, 0),
        "user_info": {
            "email": "user4@example.com",
            "registration_date": datetime(2023, 12, 4, 9, 0, 0),
        },
    },
    {
        "user_id": 127,
        "event_type": "login",
        "event_time": datetime(2024, 1, 22, 10, 0, 0),
        "user_info": {
            "email": "user5@example.com",
            "registration_date": datetime(2023, 12, 5, 10, 0, 0),
        },
    },
    {
        "user_id": 128,
        "event_type": "signup",
        "event_time": datetime(2024, 1, 22, 11, 30, 0),
        "user_info": {
            "email": "user6@example.com",
            "registration_date": datetime(2023, 12, 6, 13, 0, 0),
        },
    },
    {
        "user_id": 129,
        "event_type": "purchase",
        "event_time": datetime(2024, 1, 23, 15, 0, 0),
        "user_info": {
            "email": "user7@example.com",
            "registration_date": datetime(2023, 12, 7, 8, 0, 0),
        },
    },
    {
        "user_id": 130,
        "event_type": "login",
        "event_time": datetime(2024, 1, 23, 16, 45, 0),
        "user_info": {
            "email": "user8@example.com",
            "registration_date": datetime(2023, 12, 8, 10, 0, 0),
        },
    },
    {
        "user_id": 131,
        "event_type": "purchase",
        "event_time": datetime(2024, 1, 24, 12, 0, 0),
        "user_info": {
            "email": "user9@example.com",
            "registration_date": datetime(2023, 12, 9, 14, 0, 0),
        },
    },
    {
        "user_id": 132,
        "event_type": "signup",
        "event_time": datetime(2024, 1, 24, 18, 30, 0),
        "user_info": {
            "email": "user10@example.com",
            "registration_date": datetime(2023, 12, 10, 10, 0, 0),
        },
    },
]

# Удаление перед вставкой
collection.drop()
collection_archived.drop()  # очищаем архив перед началом работы
# Заливка данных в коллекцию
collection.insert_many(data)
print("✅ Данные успешно загружены в MongoDB")


today = datetime.now().replace(microsecond=0)
days_30 = today - timedelta(days=30)
days_14 = today - timedelta(days=14)


registered_users_30_days = collection.distinct(
    "user_id",
    {
        "user_info.registration_date": {
            "$lt": days_30
        }
    },
)


nonactive_14_days: list = []

for id in registered_users_30_days:
    lost_event = collection.find_one(
        {"user_id": id}
    )
    if not lost_event:
        continue

    if lost_event["event_time"] < days_14:
        nonactive_14_days.append(id)


archived_user_ids: list = []

for id in nonactive_14_days:
    user = list(collection.find({"user_id": id}))
    if not user:
        continue

    collection_archived.insert_many(user)
    archived_user_ids.append(id)


report = {
    "date": today.date().isoformat(),
    "archived_users_count": len(archived_user_ids),
    "archived_user_ids": archived_user_ids,
}



name = f"{today.date().isoformat()}.json"

with open(name, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=3)


