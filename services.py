import requests
from bs4 import BeautifulSoup
import urllib.parse
import xlsxwriter

from utils import valid_data_schools, valid_data_kindergarten


class SchoolParser:
    def __init__(self, url: str) -> None:
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/58.0.3029.110 Safari/537.3'
        }
        self.valid_data = valid_data_schools

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

    def extract_school_info_from_urls(self, urls: list) -> list:
        schools_info_list = []

        for url in urls:
            school_info = self.parse_school_info(url)
            schools_info_list.append(school_info)

        return schools_info_list

    def parse_school_info(self, url: str) -> list:
        """Parses data about one school"""
        response = requests.get(url=url, headers=self.headers)
        school_info_list = []

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_="zebra-stripe")
            rows = table.find_all('tr')
            school_info_list = self.extract_info_from_table(rows)

        return school_info_list

    def extract_info_from_table(self, table: list) -> list:
        """Method to extract information from table"""
        extracted_info = []

        for row in table:
            description = row.find('th')
            value = row.find('td')

            if description and value:
                description_text = description.text.strip()
                value_text = value.text.strip()

                if description_text == 'E-mail:':
                    # Because of onclick attribute need to parse email separately
                    email_tag = row.find('a', class_='static')
                    if email_tag and 'onclick' in email_tag.attrs:
                        # If the email exists change value_text to actual email
                        encoded_email = email_tag['onclick'].split("unescape('")[1].split("')")[0]
                        value_text = BeautifulSoup(urllib.parse.unquote(encoded_email), 'html.parser').find(
                            'a').text
                if self.__validate(description_text):
                    extracted_info.append(value_text if value_text else "No value provided")

        return extracted_info

    def __validate(self, value: str) -> bool:
        """Checking the value for correctness"""
        if value in self.valid_data:
            return True


class TableWriter:
    def __init__(self, schools_info_list: list):
        self.schools_info_list = schools_info_list

    def write_table(self):
        book = xlsxwriter.Workbook('parsed_schools.xlsx')
        page = book.add_worksheet("Item")

        self.__set_columns(page)

        font_format = book.add_format({
            'bold': True,
        })

        for i, param in enumerate(valid_data_schools):
            page.write(0, i, param, font_format)

        row = 1
        col = 0

        for school_info in self.schools_info_list:
            for i, value in enumerate(school_info):
                page.write(row, col + i, value)
            row += 1

        book.close()

    def __set_columns(self,page):
        columns = {
            "A:A": 20,
            "B:B": 10,
            "C:C": 10,
            "D:D": 25,
            "E:E": 20,
            "F:F": 20,
            "G:G": 30,
            "H:H": 20,
        }

        for col, width in columns.items():
            page.set_column(col, width)
