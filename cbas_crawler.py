import json
from datetime import datetime
from pathlib import Path

import requests


def scrape():

    data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "values": [1, 2, 3] # 假設這是爬到的資料
        }

    with open(Path('data') / 'data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scrape()
