'''
url = "https://5ka.ru/api/v2/special_offers/"


headers = {
'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
}
params = {
    'records_per_page': 50,
    'categories':	870,
}

response = requests.get(url, headers=headers, params=params)
if response.status_code == 200:
    with open("special_offers.html", 'w', encoding='UTF-8') as file:
        file.write(response.text)

'''

import os
from pathlib import Path
import json
import time

import requests


class Parse5ka:
    _headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:82.0) Gecko/20100101 Firefox/82.0",
    }
    _params = {
        'records_per_page': 50,
    }

    def __init__(self, start_url):
        self.start_url = start_url

    @staticmethod
    def _get(*args, **kwargs) -> requests.Response:
        while True:
            try:
                response = requests.get(*args, **kwargs)
                if response.status_code != 200:
                    # todo Создать класс исключение
                    raise Exception
                return response
            except Exception:
                time.sleep(0.25)

    def parse(self, url):
        params = self._params
        while url:
            response: requests.Response = self._get(url, params=params, headers=self._headers)
            if params:
                params = {}
            data: dict = response.json()
            url = data.get('next')
            yield data.get('results')

    def run(self):
        for products in self.parse(self.start_url):
            for product in products:
                self._save_to_file(product, product['id'])
            time.sleep(0.1)

    @staticmethod
    def _save_to_file(product, file_name):
        path = Path(os.path.dirname(__file__)).joinpath('products').joinpath(f'{file_name}.json')
        with open(path, 'w', encoding='UTF-8') as file:
            json.dump(product, file, ensure_ascii=False)


class Cat5serka(Parse5ka):
    def __init__(self, url_api_offers, url_api_cat):
        super().__init__(url_api_offers)
        self.url_api_offers = url_api_offers
        self.url_api_cat = url_api_cat

    def _get_cat(self, url):
        response = self._get(url, headers=self._headers)
        return response.json()

    def run(self):
        for catalog in self._get_cat(self.url_api_cat):
            print(catalog)
            data = [catalog]
            data[0]['products'] = []

            self._params['categories'] = data[0]['parent_group_code']

            for products in self.parse(self.start_url):
                data[0]['products'].extend(products)
            self._save_to_file(data, data[0]['parent_group_code'])


if __name__ == '__main__':
    parser = Cat5serka('https://5ka.ru/api/v2/special_offers/', 'https://5ka.ru/api/v2/categories/')
    parser.run()
