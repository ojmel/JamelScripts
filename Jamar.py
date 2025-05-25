import sys
import ScraperScripts
import eel

@eel.expose
def request_item(query: str):
    """Creates shopping url based on a clothing item of interest and its accompanying list of descriptors"""
    url = f"https://www.google.com/search?tbm=shop&q={query}"
    ScraperScripts.download_page(url, 'test.html')


eel.init("JamarHtml")

eel.start('main.html', mode='default')
