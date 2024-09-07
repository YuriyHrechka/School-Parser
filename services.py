import requests
from bs4 import BeautifulSoup
import urllib.parse
import xlsxwriter

from utils import valid_data_schools, valid_data_kindergarten


class SchoolParser:
    def __init__(self, url: str, institution_type) -> None:
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/58.0.3029.110 Safari/537.3'
        }
        if institution_type == 'school':
            self.valid_data = valid_data_schools
        elif institution_type == 'kindergarten':
            self.valid_data = valid_data_kindergarten
        else:
            raise ValueError("Invalid institution type provided")

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

    def extract_info_from_table(self, table: list) -> dict:
        """Method to extract information from table"""
        extracted_info = {}

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
                    extracted_info[description_text] = value_text if value_text else "не вказано"

        return extracted_info

    def __validate(self, value: str) -> bool:
        """Checking the value for correctness"""
        if value in self.valid_data:
            return True
        else:
            return False


class TableWriter:
    def __init__(self, schools_info_list: list):
        self.schools_info_list = schools_info_list
        self.valid_data = self.__get_valid_data(schools_info_list)
        self.column_widths = [len(header) for header in self.valid_data]

    def __get_valid_data(self, school_info_list: list) -> list:
        """Gets valid data depends on institution type"""
        if 'Кількість учнів:' in school_info_list:
            return valid_data_schools
        else:
            return valid_data_kindergarten

    def write_table(self):
        """Write exel table with schools information"""
        book = xlsxwriter.Workbook('parsed_schools.xlsx')
        page = book.add_worksheet("Item")

        self.__write_school_info(page)
        self.__set_columns(page)
        self.__write_headers(page, book)

        book.close()

    def __write_school_info(self, page):
        for row, school_info in enumerate(self.schools_info_list, start=1):
            for col, param in enumerate(self.valid_data):
                value = school_info.get(param)
                page.write(row, col, value)

                # Update column width if current cell's content is wider
                self.column_widths[col] = max(self.column_widths[col], len(str(value)))

    def __set_columns(self, page):
        """Set column widths based on the calculated maximum lengths"""
        for i, width in enumerate(self.column_widths):
            page.set_column(i, i, width)

    def __write_headers(self, page, book):
        font_format = book.add_format({
            'bold': True,
        })

        for i, param in enumerate(self.valid_data):
            page.write(0, i, param, font_format)
