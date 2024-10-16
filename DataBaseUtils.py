import json

#реализация всех функций для работы с базой данных клиентов
def save_client_info(client):
    """Сохраняем информацию о клиенте в бд"""
    with open('DataBase//clients_info.txt') as f:
        data = json.load(f)

    data.append(client)

    with open('DataBase//clients_info.txt', "w") as f:
        json.dump(data, f)
        print("Данные обновлены")


def check_client_in_db(id_client):
    """Проверяем, есть ли клиент в нашей базе данных"""
    with open('DataBase//clients_info.txt') as f:
        data = json.load(f)
        for i in data:
            if i["id"] == id_client:
                return True
    return False
def get_subscribes_id_list():
    """Получаем список id зарегистрированных"""
    with open('DataBase/clients_info.txt') as f:
        data = json.load(f)
        result_id = []
        for i in data:
            if i.get("subscription"):
                result_id.append(i["id"])

    return result_id

    #return result_id

def change_subscription_by_id(id_client):
    """Обновляем значение подписки пользователя по ID"""
    with open('DataBase/clients_info.txt') as f:
        data = json.load(f)
    subscription = True
    for i in range(len(data)):
        if data[i]["id"] == id_client:
            subscription = data[i].get("subscription")
            if subscription != None:
                data[i]["subscription"] = not subscription
            else:
                data[i]["subscription"] = True

    with open('DataBase/clients_info.txt', "w") as f:
        json.dump(data, f)
        print("Подписка обновлена")

    return subscription
