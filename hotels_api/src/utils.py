import json
import re
from datetime import datetime
from typing import Iterable
import urllib.parse

import rnet

with open("src/proxies.txt", "r") as f: proxies = f.read().splitlines()

if not proxies:
    proxies = [""]

rnet_impersonations: list[rnet.Impersonate.Chrome136] = [getattr(rnet.Impersonate, k) for k in rnet.Impersonate.__dict__.keys() if not k.startswith("__") and not k.startswith("Ok")]

async def get_response_json(coroutine):
    response = await coroutine
    response_text = await response.text()

    try:
        return json.loads(response_text)
    except:
        raise Exception(f"couldn't decode json: {response_text}")

def to_query_param(param):
    if isinstance(param, str):
        return param
    elif isinstance(param, bool):
        return str(param).lower()
    else:
        return str(param)

def dict_to_query_params(dict: dict):
    tuples_list = []

    for k, v in dict.items():
        if isinstance(v, str):
            pass
        elif isinstance(v, Iterable):
            for sub_v in v:
                tuples_list.append((k, to_query_param(sub_v)))
            continue
        tuples_list.append((k, to_query_param(v)))
    return tuples_list

def parse_date(date: str):
    search = re.search(r'(\d+)[^\d]+(\d+)[^\d]+(\d+)', date)
    return datetime(year=int(search.group(1)), month=int(search.group(2)), day=int(search.group(3)))

def filter_string(string: str, start: str = None, end: str = None, include_start: bool = False,
                  include_end: bool = False):
    if start is not None:
        start_match = re.search(start, string)
        if start_match:
            if include_start:
                string = string[start_match.start():]
            else:
                string = string[start_match.end():]
    if end is not None:
        end_match = re.search(end, string)
        if end_match:
            if include_end:
                string = string[:end_match.end()]
            else:
                string = string[:end_match.start()]
    return string