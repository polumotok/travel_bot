"""
Модуль содержит класс City, функцию except_write - обработка ошибок
и info_data - база донных с id-пользователя и id-запроса
"""
import json
import os

import requests
import re
from config_data.config import RAPID_API_KEY


class City:
    """
    Класс взаимодействия запросов с сайтом API
    """
    __headers = RAPID_API_KEY

    def __init__(self, city_info):
        self.city_info = city_info
        if re.search(r'[A-Za-z]', self.city_info[0]):
            self.lang = 'en_US'
            self.currency = 'USD'
        else:
            self.lang = 'ru_RU'
            self.currency = 'RUB'


    def set_headers(self, headers_dict):
        """Изменение ключей доступа к сайту API"""
        self.__headers = headers_dict

    def city_search(self) -> tuple:
        """
        Метод возвращает tuple в виде словарей, в которых
        call_name - текст для кнопки,
        call_result - словарь значений для города
        """

        url = "https://hotels4.p.rapidapi.com/locations/search"
        querystring = {"query": self.city_info, "locale": self.lang}
        header = {
	"X-RapidAPI-Key": RAPID_API_KEY,
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

        try:
            response = requests.get(url, headers=header, params=querystring)
            data_deaths = json.loads(response.text)
            data = data_deaths["suggestions"][0]["entities"]
            for item in data:
                yield {'call_name': (item['name']), 'call_result': item}
        except KeyError:
            return None


    def hotel_search(self) -> dict:
        """
        Метод возвращает словарь отелей по ID города 'Р1173889'
        (буква берётся из названия города для определения locale):
        City('Р1173889').hotel_search()->
        'Хостел Orange': {'distance': '1,9 км',
                   'exactCurrent': 12.31,
                   'starRating': 2.0,
                   'street': 'ул. Московская, 68'}
        """
        with open(os.path.abspath('serch_date.json'), "r") as fh:
            check = json.load(fh)
        url = "https://hotels4.p.rapidapi.com/properties/v2/list"
        _, _, geo_id, _ = self.city_info.split('_')
        payload = {
            "currency": self.currency,
            "eapid": 1,
            "locale": self.lang,
            "siteId": 300000001,
            "destination": {"regionId": geo_id},
            "checkInDate": {
                "day": int(check[2]),
                "month": int(check[1]),
                "year": int(check[0])
            },
            "checkOutDate": {
                "day": int(check[2]),
                "month": int(check[1]),
                "year": int(check[0])
            },
            "rooms": [
                {
                    "adults": 1,
                    "children": [{"age": 0}]
                }
            ],
            "resultsStartingIndex": 0,
            "resultsSize": 10,
            "sort": "PRICE_LOW_TO_HIGH",
            "filters": {"price": {
                "max": 300,
                "min": 50
            }}
        }
        headers = {
	"X-RapidAPI-Key": RAPID_API_KEY,
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}
        data = dict()
        try:
            response = requests.request("POST", url, json=payload, headers=headers)
            full_info_list = json.loads(response.text)['data']['propertySearch']['properties']
            for elem in full_info_list:
                key = elem['name']
                data[key] = dict()
                try:
                    data[key]['street'] = elem['address']['streetAddress']
                except KeyError:
                    data[key]['street'] = 'None'
                try:
                    data[key]['starRating'] = elem['starRating']
                except KeyError:
                    data[key]['starRating'] = 'None'
                try:
                    data[key]['exactCurrent'] = elem['price']['lead']['amount']
                except KeyError:
                    data[key]['exactCurrent'] = 'None'
                try:
                    data[key]['URL'] = elem['propertyImage']['image']['url']
                except KeyError:
                    data[key]['URL'] = 'None'
                try:
                    data[key]['distance'] = elem['destinationInfo']['distanceFromDestination']['value']
                except KeyError:
                    data[key]['distance'] = '1'
        finally:
            return data
    def hotel_sort(self, amount=10, *args):
        """
        Метод возвращает кортеж отсортированных по заданным параметрам словарей
        """
        price_list = []
        hotel_dict = self.hotel_search()
        for key in hotel_dict.keys():
            if hotel_dict[key]['exactCurrent'] != 'None' \
                    and not hotel_dict[key]['exactCurrent'] in price_list:
                price_list.append(hotel_dict[key]['exactCurrent'])
        if self.city_info[-1] == 'l':
            sort_price_list = sorted(price_list)
        else:
            sort_price_list = sorted(price_list)[::-1]
        if amount > len(price_list):
            amount = len(price_list)
        if self.city_info[-1] == 'l' or self.city_info[-1] == 'h':
            for price in sort_price_list:
                for elem in hotel_dict:
                    if hotel_dict[elem]['exactCurrent'] == price and amount != 0:
                        amount -= 1
                        yield elem, hotel_dict[elem]
        else:
            dist = float(args[0][0])
            max_price = float(args[0][1])
            min_price = float(args[0][2])
            if max_price < min_price:
                max_price, min_price = min_price, max_price
            for elem in hotel_dict:
                try:
                    if hotel_dict[elem]['distance'] < dist \
                            and hotel_dict[elem]['exactCurrent'] != 'None' \
                            and min_price < hotel_dict[elem]['exactCurrent'] < max_price \
                            and amount != 0:
                        amount -= 1
                        yield elem, hotel_dict[elem]
                except:
                    pass


def num_from_str(text: str) -> float:
    num_text = ''
    for letter in text:
        if letter.isdigit():
            num_text += letter
        elif letter == ',' or letter == '.':
            num_text += '.'
    return float(num_text)
