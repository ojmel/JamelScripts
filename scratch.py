from bs4 import BeautifulSoup

import ScraperScripts
# ScraperScripts.download_page("https://www.google.com/search?tbm=shop&q=mens polo", 'test.html')
soup=ScraperScripts.load_html_file('test.html')
# Find all elements with "data-attrid"
elements = soup.find_all(attrs={"data-attrid": True})
#span aria-label="Current Price: $11.99. "
# span aria-label="Rated 4.2 out of 5"
# data-entityname="Old Navy Short-Sleeve Pique Polo for Men Heather"
#img alt="" class="VeBrne" data-deferred="1" id="dimg_0sAOaPTfNcqj5NoPx-PuoAQ_105" src="dat
for elem in elements:
    print(elem)