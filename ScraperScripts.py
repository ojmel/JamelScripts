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
# connection handler failed
# Traceback (most recent call last):
#   File "C:\Users\jamel\PycharmProjects\Jamel\venv\Lib\site-packages\websockets\asyncio\server.py", line 373, in conn_handler
#     await self.handler(connection)
#   File "C:\Users\jamel\PycharmProjects\JamelScripts\server.py", line 56, in parse_socket
#     await self.godot_server.send(f'{player.player_name}:{message}')
#   File "C:\Users\jamel\PycharmProjects\Jamel\venv\Lib\site-packages\websockets\asyncio\connection.py", line 458, in send
#     async with self.send_context():
#   File "C:\Users\jamel\AppData\Local\Programs\Python\Python311\Lib\contextlib.py", line 204, in __aenter__
#     return await anext(self.gen)
#            ^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\jamel\PycharmProjects\Jamel\venv\Lib\site-packages\websockets\asyncio\connection.py", line 933, in send_context
#     raise self.protocol.close_exc from original_exc
# websockets.exceptions.ConnectionClosedError: sent 1011 (internal error); then received 1011 (internal error)
# connection handler failed
# Traceback (most recent call last):
#   File "C:\Users\jamel\AppData\Local\Programs\Python\Python311\Lib\asyncio\windows_events.py", line 489, in finish_recv
#     return ov.getresult()
#            ^^^^^^^^^^^^^^
# OSError: [WinError 64] The specified network name is no longer available
#
# During handling of the above exception, another exception occurred:
#
# Traceback (most recent call last):
#   File "C:\Users\jamel\AppData\Local\Programs\Python\Python311\Lib\asyncio\proactor_events.py", line 286, in _loop_reading
#     length = fut.result()
#              ^^^^^^^^^^^^
#   File "C:\Users\jamel\AppData\Local\Programs\Python\Python311\Lib\asyncio\windows_events.py", line 841, in _poll
#     value = callback(transferred, key, ov)
#             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\jamel\AppData\Local\Programs\Python\Python311\Lib\asyncio\windows_events.py", line 493, in finish_recv
#     raise ConnectionResetError(*exc.args)
# ConnectionResetError: [WinError 64] The specified network name is no longer available
#
# The above exception was the direct cause of the following exception:
#
# Traceback (most recent call last):
#   File "C:\Users\jamel\PycharmProjects\Jamel\venv\Lib\site-packages\websockets\asyncio\server.py", line 373, in conn_handler
#     await self.handler(connection)
#   File "C:\Users\jamel\PycharmProjects\JamelScripts\server.py", line 32, in parse_socket
#     async for message in websocket:
#   File "C:\Users\jamel\PycharmProjects\Jamel\venv\Lib\site-packages\websockets\asyncio\connection.py", line 242, in __aiter__
#     yield await self.recv()
#           ^^^^^^^^^^^^^^^^^
#   File "C:\Users\jamel\PycharmProjects\Jamel\venv\Lib\site-packages\websockets\asyncio\connection.py", line 313, in recv
#     raise self.protocol.close_exc from self.recv_exc
# websockets.exceptions.ConnectionClosedError: no close frame received or sent
# connection handler failed
# Traceback (most recent call last):
#   File "C:\Users\jamel\PycharmProjects\Jamel\venv\Lib\site-packages\websockets\asyncio\server.py", line 373, in conn_handler
#     await self.handler(connection)
#   File "C:\Users\jamel\PycharmProjects\JamelScripts\server.py", line 56, in parse_socket
#     await self.godot_server.send(f'{player.player_name}:{message}')
#   File "C:\Users\jamel\PycharmProjects\Jamel\venv\Lib\site-packages\websockets\asyncio\connection.py", line 458, in send
#     async with self.send_context():
#   File "C:\Users\jamel\AppData\Local\Programs\Python\Python311\Lib\contextlib.py", line 204, in __aenter__
#     return await anext(self.gen)
#            ^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\jamel\PycharmProjects\Jamel\venv\Lib\site-packages\websockets\asyncio\connection.py", line 933, in send_context
#     raise self.protocol.close_exc from original_exc
# websockets.exceptions.ConnectionClosedError: sent 1011 (internal error); then received 1011 (internal error)
# connection handler failed
# Traceback (most recent call last):
#   File "C:\Users\jamel\AppData\Local\Programs\Python\Python311\Lib\asyncio\windows_events.py", line 489, in finish_recv
#     return ov.getresult()
#            ^^^^^^^^^^^^^^
# OSError: [WinError 64] The specified network name is no longer available
#
# During handling of the above exception, another exception occurred:
#
# Traceback (most recent call last):
#   File "C:\Users\jamel\AppData\Local\Programs\Python\Python311\Lib\asyncio\proactor_events.py", line 286, in _loop_reading
#     length = fut.result()
#              ^^^^^^^^^^^^
#   File "C:\Users\jamel\AppData\Local\Programs\Python\Python311\Lib\asyncio\windows_events.py", line 841, in _poll
#     value = callback(transferred, key, ov)
#             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\jamel\AppData\Local\Programs\Python\Python311\Lib\asyncio\windows_events.py", line 493, in finish_recv
#     raise ConnectionResetError(*exc.args)
# ConnectionResetError: [WinError 64] The specified network name is no longer available
#
# The above exception was the direct cause of the following exception:
#
# Traceback (most recent call last):
#   File "C:\Users\jamel\PycharmProjects\Jamel\venv\Lib\site-packages\websockets\asyncio\server.py", line 373, in conn_handler
#     await self.handler(connection)
#   File "C:\Users\jamel\PycharmProjects\JamelScripts\server.py", line 32, in parse_socket
#     async for message in websocket:
#   File "C:\Users\jamel\PycharmProjects\Jamel\venv\Lib\site-packages\websockets\asyncio\connection.py", line 242, in __aiter__
#     yield await self.recv()
#           ^^^^^^^^^^^^^^^^^
#   File "C:\Users\jamel\PycharmProjects\Jamel\venv\Lib\site-packages\websockets\asyncio\connection.py", line 313, in recv
#     raise self.protocol.close_exc from self.recv_exc
# websockets.exceptions.ConnectionClosedError: no close frame received or sent
# Traceback (most recent call last):
#   File "C:\Users\jamel\AppData\Local\Programs\Python\Python311\Lib\asyncio\runners.py", line 118, in run
#     return self._loop.run_until_complete(task)
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\jamel\AppData\Local\Programs\Python\Python311\Lib\asyncio\base_events.py", line 653, in run_until_complete
#     return future.result()
#            ^^^^^^^^^^^^^^^
#   File "C:\Users\jamel\PycharmProjects\JamelScripts\server.py", line 85, in main
#     await asyncio.get_running_loop().create_future()  # run forever
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# asyncio.exceptions.CancelledError
#
# During handling of the above exception, another exception occurred:
#
# Traceback (most recent call last):
#   File "C:\Users\jamel\PycharmProjects\JamelScripts\server.py", line 93, in <module>
#     asyncio.run(main())
#   File "C:\Users\jamel\AppData\Local\Programs\Python\Python311\Lib\asyncio\runners.py", line 190, in run
#     return runner.run(main)
#            ^^^^^^^^^^^^^^^^
#   File "C:\Users\jamel\AppData\Local\Programs\Python\Python311\Lib\asyncio\runners.py", line 123, in run
#     raise KeyboardInterrupt()
# KeyboardInterrupt