from services import SchoolParser, TableWriter

a = SchoolParser('https://te.isuo.org/authorities/preschools-list/id/638', "kindergarten")
urls_list = a.base_url_list()
b = TableWriter(a.extract_school_info_from_urls(urls_list))
b.write_table()