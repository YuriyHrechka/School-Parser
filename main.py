from services import SchoolParser

a = SchoolParser('https://te.isuo.org/koatuu/schools-list/id/6110100000')
print(a.parse_school_info(a.base_url_list()[0]))
