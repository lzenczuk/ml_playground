import requests
from bs4 import BeautifulSoup


def get_number_of_latest_entry():
    r = requests.get('https://www.wykop.pl/wykopalisko/najnowsze/', allow_redirects=True)
    if r.status_code != 200:
        print "Http error: "+str(r.status_code)
        return None

    doc = BeautifulSoup(r.text, 'html.parser')
    entries = doc.select('div.grid-main > ul#itemsStream > li.link.iC > div.article')

    if len(entries) == 0:
        print "Html parsing error, no entries"
        return None

    return int(entries[0].attrs['data-id'])


def get_number_of_first_entry():
    return 1


