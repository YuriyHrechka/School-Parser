import requests
from bs4 import BeautifulSoup
import urllib.parse


class SchoolParser:
    def __init__(self, url: str) -> None:
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    def base_url_list(self) -> list:
        """Return list with all urls school"""
        urls = []
        response = requests.get(url=self.url, headers=self.headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_="zebra-stripe list")
            links = table.find_all('a', href=True)

            for link in links:
                urls.append(f'https://te.isuo.org/{link['href']}')
            return urls
        raise ValueError('url is invalid')

    def parse_data(self, url: str) -> dict:
        response = requests.get(url=url, headers=self.headers)
        data_dict = {}
        valid_data = ['№ у системі:', 'Скорочена:', 'Поштова адреса:', 'Телефони:', 'E-mail:', 'Директор:', 'Спроможність закладу освіти (учнів):', 'Кількість учнів:']

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_="zebra-stripe")
            rows = table.find_all('tr')

            for row in rows:
                th = row.find('th')
                td = row.find('td')

                if th and td:
                    th_text = th.text.strip()
                    td_text = td.text.strip()
                    if th_text == 'E-mail:':
                        encoded_email = soup.find('a', class_='static')['onclick'].split("unescape('")[1].split("')")[0]
                        td_text = BeautifulSoup(urllib.parse.unquote(encoded_email), 'html.parser').find('a').text
                    if th_text in valid_data:
                        data_dict[th_text] = td_text

            return data_dict




