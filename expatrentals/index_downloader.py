import requests
from bs4 import BeautifulSoup

main_url = 'https://www.expatrentals.eu/country/netherlands/amsterdam?country_id=1&locationNameText=Amsterdam&area_id=1&streetName=Center&limitToStreet=False&latitude=&longitude=&distance=20000&min_price_rent=&max_price_rent=&furnished=&bedrooms=&max_bedrooms=&min_date=&order=2'

links_file_name = "rent_links.csv"


def download_index():

    save_header(links_file_name)

    fp = fetch_first_page()
    if fp['error'] is not None:
        print("Error code: " + str(fp['error']))
        return

    content_ = fp['content']
    number_of_pages = extract_number_of_pages(content_)
    links = extract_data(content_)
    save_links_to_file(links_file_name, links)

    for np in range(0, number_of_pages):
        print("------------------------ page "+str(np)+" from "+str(number_of_pages))

        fp = fetch_next_page(np+2)
        if fp['error'] is not None:
            print("Error code: " + str(fp['error']))
            return

        content_ = fp['content']
        links = extract_data(content_)
        print("Entries: "+str(len(links)))
        save_links_to_file(links_file_name, links)


def fetch_first_page():
    r = requests.get(main_url, allow_redirects=False)
    if r.status_code == 200:
        return {
            'content': r.content,
            'error': None
        }
    else:
        return {
            'content': None,
            'error': r.status_code
        }


def fetch_next_page(page_num):
    url = "https://www.expatrentals.eu/country/netherlands/amsterdam?streetName=Center&pagenum="+str(page_num)
    headers = {'Referer': main_url}
    r = requests.get(url, allow_redirects=False, headers=headers)
    if r.status_code == 200:
        return {
            'content': r.content,
            'error': None
        }
    else:
        return {
            'content': None,
            'error': r.status_code
        }


def extract_number_of_pages(content):
    doc = BeautifulSoup(content, 'html.parser')
    number_of_pages_string = doc.select_one("span#page-count-top").text
    res = number_of_pages_string.split(' ')

    if len(res) != 7:
        print("Error. Unknown page string format. Expecting: 'Showing results 1 to 13 of 386', was '"+number_of_pages_string+"'")
        return None
    else:
        total_offers = int(res[6])
        return (total_offers-13)/10


def extract_data(content):
    doc = BeautifulSoup(content, 'html.parser')

    links = []

    for rental in doc.select("div#resultList > div.rental"):
        link_element = rental.select_one("div.details > a.title")
        if link_element is None:
            continue

        # Link
        link = link_element.attrs['href']

        # Address
        address = link_element.text
        if address.endswith("NEW"):
            address = address.replace("NEW", "")
        address = address.strip()

        # Price
        price = None
        price_element = rental.select_one("div.pricing > div.priceNumber")
        if price_element is not None:
            price = price_element.text

        # Furnishing
        furnished = None
        furnishing_element = rental.select_one("div.pricing > div.furnishings")
        if furnishing_element is not None:
            f = furnishing_element.text.strip().lower()

            if 'furnished'==f:
                furnished = True

            if 'unfurnished'==f:
                furnished = False

        # Bedrooms
        bedrooms = None
        bedrooms_element = rental.select_one("div.pricing > div.further")
        if bedrooms_element is not None:
            bedrooms = bedrooms_element.text.strip().split(' ')[0]

        links.append({
            'link': link,
            'address': address,
            'price': price,
            'furnished': furnished,
            'bedrooms': bedrooms
        })


    return links


def save_links_to_file(file_name, data_list):
    page_file = open('out/' + file_name, "a")

    for d in data_list:
        l = ''
        l = l+d['link']
        l = l+';'+d['address']

        if d['price'] is None:
            l = l + ';'
        else:
            l = l+';'+d['price'][1:]

        if d['furnished'] is None:
            l = l + ';'
        else:
            if d['furnished']:
                l = l + ';'+'1'
            else:
                l = l + ';' + '0'

        if d['bedrooms'] is None:
            l = l + ';'
        else:
            l = l+';'+d['bedrooms']

        page_file.write((l+"\n").encode('utf8'))

    page_file.close()


def save_header(file_name):
    page_file = open('out/' + file_name, "w")

    l = 'link;address;price;furnished;bedrooms'
    page_file.write((l+"\n").encode('utf8'))

    page_file.close()


download_index()
