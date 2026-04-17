
import json
from datetime import datetime
from math import nan
from pathlib import Path
from typing import Literal

import bs4
import requests

from tool import ensure_element_found


def get_id_list_from_istock() -> list[str]:
    """get CBAS id list from istock page"""

    def _clean_id_text(text: str) -> str:
        _cleaned_text = text.strip().split('-')[0].strip()
        if _cleaned_text.isdigit():
            return _cleaned_text
        return ''

    session = requests.Session()
    response = session.get('http://money-104.com/paper_bookentry.php?')
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    id_list = []

    select_id = ensure_element_found(
        soup.find('select', {'name': 'stock_id'}),
        describe="select element for stock_id in istock page",
        msg="get_cbas_id_list in thefewCrawler")

    option_list = ensure_element_found(
        select_id.find_all('option'),
        describe="all option element for stock_id in istock page",
        msg="get_cbas_id_list in thefewCrawler")

    for option in option_list:
        cleaned_id = _clean_id_text(option.text)
        if cleaned_id:
            id_list.append(cleaned_id)

    return id_list

def get_id_list_from_thefew() -> list[str]:
    """get CBAS id list from thefew page"""

    session = requests.Session()
    response = session.get('https://thefew.tw/cb')
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    id_list = []

    table = ensure_element_found(
        soup.find('table', id="cb-table"),
        describe="table element in thefew page",
        msg="get_cbas_id_list in thefewCrawler")

    div_id_list = ensure_element_found(
        table.find_all('div', class_='inline-block w-1/3') ,
        describe="all id element in thefew page",
        msg="get_cbas_id_list in thefewCrawler")

    for div_id in div_id_list:
        id_text = div_id.text.strip()
        if id_text.isdigit():
            id_list.append(id_text)

    return id_list


id_list_function = {
    'thefew': get_id_list_from_istock,
    'istock': get_id_list_from_thefew
    }

def istock_crawler(
        id_list_src: Literal['thefew', 'istock'] = 'thefew'
        ) -> tuple[dict[str, float], str]:
    """crawl CBAS data from istock page"""

    id_list = id_list_function[id_list_src]()

    session = requests.Session()
    data = dict()

    for id in id_list:
        try:
            response = session.get(f'http://money-104.com/paper_bookentry.php?cb_id={id}')
            soup = bs4.BeautifulSoup(response.text, 'html.parser')

            table = ensure_element_found(
                soup.find('table'),
                describe=f"table for {id}",
                msg="istock_crawler in thefewCrawler")

            tr_data = ensure_element_found(
                table.find_all('tr'),
                describe=f"all tr data for {id}",
                msg="istock_crawler in thefewCrawler")

            now_balance = ensure_element_found(
                tr_data[1].find_all('td')[4],
                describe=f"now balance for {id}",
                msg="istock_crawler in thefewCrawler").text.replace(',', '')

            initial_balance = ensure_element_found(
                tr_data[-1].find_all('td')[4],
                describe=f"initial balance for {id}",
                msg="istock_crawler in thefewCrawler").text.replace(',', '')

            transformed_ratio = (
                (float(initial_balance) - float(now_balance)) / float(initial_balance)
                ) * 100

            data[id] = transformed_ratio

            print(id, transformed_ratio)

        except Exception as e:
            print(e)
            data[id] = nan

    session.close()
    return data, id_list_src

if __name__ == "__main__":

    data, id_list_src_nam = istock_crawler()
    if len(data) == 0:
        exit(1)

    json_data = {
        "last_update" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "id_list_src" : id_list_src_nam,
        "data" : data
        }

    with open(Path('data') / 'istock.json', 'w') as f:
        json.dump(json_data, f, indent=4)






