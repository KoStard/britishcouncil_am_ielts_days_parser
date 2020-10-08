from requests import Session
from pprint import pprint
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

ua = UserAgent()
headers = {'User-Agent': ua.random}

session = Session()
session.head('https://www.britishcouncil.am/en/exam/ielts/dates-fees-locations', headers=headers)
response = session.post(url='https://www.britishcouncil.am/en/views/ajax', 
                        data={'field_pf_exam_examname_value': 1, 'view_name': 'product_finder_ielts_test_dates', 'view_display_id': 'block_pf_ielts_test_dates', 'view_args': 'en'}, 
                        headers=headers)
commands = response.json()
insert_command = next(e for e in commands if e['command'] == 'insert')
insert_data = insert_command['data']
bs = BeautifulSoup(insert_data, features="html.parser")
table = bs.select("table")[0]
body = table.find_all('tbody')[0]
results = []
for row in body.children:
    if not hasattr(row, 'children'):
        continue
    row_data = {}
    row_children = [e for e in row.children if hasattr(e, 'select')]
    for i, td in enumerate(row_children):
        if i == 0 or i == 2:
            dt = td.select('span.date-display-single')[0].get_text()
            if i == 0:
                row_data['test_date'] = dt
            if i == 2:
                row_data['registration_deadline'] = dt
    results.append(row_data)

pprint(results)