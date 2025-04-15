import sys
import ScraperScripts
gender_options=['women%27s','men%27s']
import eel
eel.init("JamarHtml")  
@eel.expose
def request_item(descriptors:list[str],actual_item:str,gender='men%27s'):
    """Creates shopping url based on a clothing item of interest and its accompanying list of descriptors"""
    url=f'https://www.google.com/search?q={ScraperScripts.word_match(gender,gender_options,0.7)}+{"+".join(descriptors)}+{"+".join(actual_item.split(" "))}'
    ScraperScripts.download_page(url,'test.html')
eel.start('main.html', mode='default')