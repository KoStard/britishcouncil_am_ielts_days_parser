from requests import Session
from pprint import pprint
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json
from constants import PROJECT_ID, DATES_KEY
from datastore_wrapper import save_to_datastore, get_from_datastore
from telegram_bot import receive_chat_ids, send_message


def get_currently_available_dates():
    print("Getting currently available dates...")
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    session = Session()
    session.head(
        'https://www.britishcouncil.am/en/exam/ielts/dates-fees-locations', headers=headers)
    response = session.post(url='https://www.britishcouncil.am/en/views/ajax',
                            data={'field_pf_exam_examname_value': 1, 'view_name': 'product_finder_ielts_test_dates',
                                  'view_display_id': 'block_pf_ielts_test_dates', 'view_args': 'en'},
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
    print("Got these test date records: ", results)
    return results


def get_from_optional_dict(value, key):
    return (value or {}).get(key)


def update_chat_ids():
    print("Updating chat ids...")
    offset = get_from_optional_dict(
        get_from_datastore("telegram_updates_offset"), "offset")
    permitted_users = set(get_from_optional_dict(
        get_from_datastore("telegram_permitted_users"), 'usernames') or [])
    chat_ids = set(get_from_optional_dict(
        get_from_datastore("telegram_chat_ids"), "ids") or [])
    new_chat_ids, new_offset = receive_chat_ids(offset, permitted_users)
    print("Adding these new chat ids: ", new_chat_ids)
    save_to_datastore("telegram_updates_offset", {"offset": new_offset})
    updated_chat_ids = chat_ids | new_chat_ids
    save_to_datastore("telegram_chat_ids", {"ids": list(updated_chat_ids)})
    print("Using these chat ids: ", updated_chat_ids)
    return updated_chat_ids


def generate_message_from_record(record):
    return f"New ielts test date available.\nTest date: {record['test_date']}\nRegistration deadline: {record['registration_deadline']}"


def send_to_all_listeners(records):
    print("Found these new records: ", records)
    chat_ids = update_chat_ids()
    for chat_id in chat_ids:
        for record in records:
            send_message(generate_message_from_record(record), chat_id)


def compare_and_inform_if_required():
    currently_available_dates = get_currently_available_dates()
    last_saved_available_dates = get_from_optional_dict(
        get_from_datastore(DATES_KEY), 'dates')
    not_found_records = []
    for current_record in currently_available_dates:
        found = False
        for saved_record in last_saved_available_dates:
            if current_record == saved_record:
                found = True
                break
        if not found:
            not_found_records.append(current_record)
    if not_found_records:
        send_to_all_listeners(not_found_records)
    save_to_datastore(
        DATES_KEY, {'dates': currently_available_dates, 'last_updated': datetime.now()})


def handle_event():
    compare_and_inform_if_required()
