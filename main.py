from services import SchoolParser

a = SchoolParser('https://te.isuo.org/koatuu/schools-list/id/6110100000')
urls_list = a.base_url_list()
print(a.extract_school_info_from_urls(urls_list))
