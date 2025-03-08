import difflib
import json
import os.path
import pickle
import time
import ast
from functools import reduce
from pathlib import Path
from selenium import webdriver
import requests
from bs4 import BeautifulSoup

def subtract_all(series):
    return reduce(lambda x, y: x - y, series)
def get_url_soup(url):
    if (response := requests.get(url)).status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')


def download_page(url, html_file):
    driver = webdriver.Edge()
    driver.get(url)
    time.sleep(2)
    html = driver.page_source
    with open(html_file, "w", encoding="utf-8") as file:
        file.write(html)
    return html


def download_multipages(html_url_dict: dict[str, str]):
    driver = webdriver.Edge()
    for html_file, url in html_url_dict.items():
        if not os.path.exists(html_file):
            driver.get(url)
            time.sleep(2)
            html = driver.page_source
            time.sleep(2)
            with open(html_file, "w", encoding="utf-8") as file:
                file.write(html)


def load_html_file(html_file, url=''):
    if url and not os.path.exists(html_file):
        html = download_page(url, html_file)
    else:
        with open(html_file, "r", encoding="utf-8") as file:
            html = file.read()
    return BeautifulSoup(html, 'html.parser')


def create_json(obj: dict, json_file):
    with open(json_file, "w") as json_file:
        json.dump(obj, json_file)


def load_json(json_file):
    with open(json_file, 'rb') as jfile:
        return json.load(jfile)


def step_thru_parents(soup: BeautifulSoup, text_to_find):
    child = soup.find(string=text_to_find)
    print(child)
    for x in range(100):
        parent = child.next_sibling
        print(parent)
        input("Press Enter to continue...")


def word_match(word, choices, cutoff=0.5):
    return next(iter(difflib.get_close_matches(word, choices, n=1, cutoff=cutoff)), None)


def clear_html(directory):
    for file in (file for file in Path(directory).iterdir() if file.name.endswith('.html')):
        Path.unlink(file)

def pickle_it(obj, file):
    with open(file, 'wb') as file:
        pickle.dump(obj, file)


def unpickle_it(file):
    with open(file, 'rb') as obj:
        return pickle.load(obj)

def navigable_str_to_obj(obj):
    return json.loads(str(obj))