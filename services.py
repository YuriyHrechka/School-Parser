import requests
from bs4 import BeautifulSoup
import urllib.parse

from utils import valid_data


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

    def __validate(self, value: str) -> bool:
        """Checking the value for correctness"""
        if value in valid_data:
            return True

    def parse_school_info(self, url: str) -> list:
        """Parses data about one school"""
        response = requests.get(url=url, headers=self.headers)
        school_info_list = []

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_="zebra-stripe")
            rows = table.find_all('tr')

            for row in rows:
                description = row.find('th')
                value = row.find('td')

                if description and value:
                    description_text = description.text.strip()
                    value_text = value.text.strip()
                    if description_text == 'E-mail:':
                        encoded_email = soup.find('a', class_='static')['onclick'].split("unescape('")[1].split("')")[0]
                        value_text = BeautifulSoup(urllib.parse.unquote(encoded_email), 'html.parser').find('a').text
                    if self.__validate(description_text):
                        school_info_list.append(value_text)

            return school_info_list

    def extract_school_info_from_urls(self, urls: list) -> list:
        schools_info_list = []

        for url in urls:
            school_info = self.parse_school_info(url)
            schools_info_list.append(school_info)

        return schools_info_list
