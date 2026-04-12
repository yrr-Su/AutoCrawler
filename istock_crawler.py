
import json
from datetime import datetime
from math import nan
from pathlib import Path

import bs4
import requests

from tool import ensure_element_found


def get_cbas_id_list() -> list[str]:
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

def istock_crawler() -> dict[str, float]:
    """crawl CBAS data from istock page"""

    id_list = get_cbas_id_list()

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
    return data

if __name__ == "__main__":

    data = istock_crawler()

    if len(data) == 0:
        exit(1)

    json_data = {
        "last_update" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data" : data
    }

    with open(Path('data') / 'istock.json', 'w') as f:
        json.dump(json_data, f, indent=4)






