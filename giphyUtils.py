import requests
import json
from Constants import GIPHY_TOKEN

#получение одной случайной гифки
def get_random_gif():
    """Функция, которая получает одну случайную гифку"""
    url = "http://api.giphy.com/v1/gifs/random"

    param = {
        "api_key": GIPHY_TOKEN,
        "rating": "g"
    }

    result = requests.get(url, params=param)
    result_dict = result.json()

    link_origin = result_dict["data"]["images"]["original"]["url"]

    return link_origin

#получение гифки по поиску
def get_gif_by_name(name):
    """Функция, которая получает одну гифку по поиску"""

    url = "http://api.giphy.com/v1/gifs/search"

    param = {
        "api_key": GIPHY_TOKEN,
        "rating": "g",
        "q": name,
        "limit": 1,
        "lang": "ru"
    }

    result = requests.get(url, params=param)
    result_dict = result.json()
    print(json.dumps(result_dict, sort_keys=True, indent=4))
    link_origin = result_dict["data"][0]["images"]["original"]["url"]

    return link_origin