import requests

URL = "http://127.0.0.1:8000/recommend"

tests = [
    {
        "name": "Сценарий - Новый пользователь",
        "payload": {"user_id": -999, "online_history": []}
    },
    {
        "name": "Сценарий - Пользователь С рекомендациями, но без онлайн-истории",
        "payload": {"user_id": 0, "online_history": []}
    },
    {
        "name": "Сценарий - Пользователь С персональными рекомендациями и С онлайн-историей",
        "payload": {"user_id": 0, "online_history": [123, 456, 789]}
    }
]

def run_tests():
    for i, test in enumerate(tests, 1):
        try:
            response = requests.post(URL, json=test['payload'], timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"Рекомендации - ({len(data['recommendations'])}): {data['recommendations']}")
            else:
                print(f"Ошибка сервиса - {response.status_code}, Ответ - {response.text}")
        except requests.exceptions.ConnectionError:
            print("Не удалось подключиться к сервису")
            break

if __name__ == "__main__":
    run_tests()