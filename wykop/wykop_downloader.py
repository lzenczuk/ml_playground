import requests
from bs4 import BeautifulSoup
import os


def fetch_wykop_page(page_id):
    """
    Fetch main wykop page by id

    Parameters:
    id: page id

    Returns:
    Dictionary: {
        id: requested page's id
        exists: boolean - is page exists
        url: full url of page with requested id
        error: error massage if error ocure
        body: text with body of page
    }
    """

    r = requests.get('https://www.wykop.pl/link/%d/' % page_id, allow_redirects=False)
    if r.status_code == 404:
        return {
            'id': page_id,
            'exists': False,
            'error': None
        }
    elif r.status_code == 301:
        r2 = requests.get(r.headers['Location'], allow_redirects=False)
        if r2.status_code == 200:
            return {
                'id': page_id,
                'exists': True,
                'url': r.headers['Location'],
                'error': None,
                'body': r2.text
            }
        else:
            return {
                'id': page_id,
                'exists': True,
                'url': r.headers['Location'],
                'error': 'error fetching redirected page: %d' % r2.status_code
            }
    else:
        return {
            'id': page_id,
            'exists': False,
            'error': 'error fetching main page: %d' % r.status_code
        }


def number_of_comment_pages(page_txt):
    doc = BeautifulSoup(page_txt, 'html.parser')
    pages_links = doc.select("div.pager > p > a.button")
    if len(pages_links) != 0:
        last_page_number = int(pages_links[-2].text)
    else:
        last_page_number = 0

    return last_page_number


def fetch_up_votes(page_id):
    return fetch_votes(page_id, is_up=True)


def fetch_down_votes(page_id):
    return fetch_votes(page_id, is_up=False)


def fetch_votes(page_id, is_up):
    if is_up:
        r = requests.get('https://www.wykop.pl/ajax2/links/Upvoters/%d/' % page_id)
        votes_type = 'up'
    else:
        r = requests.get('https://www.wykop.pl/ajax2/links/downvoters/%d/' % page_id)
        votes_type = 'down'

    if r.status_code == 200:
        return {
            'id': page_id,
            'exists': True,
            'error': None,
            'body': r.text
        }
    else:
        return {
            'id': page_id,
            'exists': False,
            'error': 'error fetching %s votes page: %d' % (votes_type, r.status_code)
        }


def fetch_comment_page(main_page_url, comments_page_number):
    comments_page_url = main_page_url + '/strona/' + str(comments_page_number) + '/'
    r = requests.get(comments_page_url)

    if r.status_code == 200:
        return {
            'exists': True,
            'error': None,
            'body': r.text
        }
    else:
        return {
            'exists': False,
            'error': 'error fetching comments page number: %s, status code: %d' % (comments_page_url, r.status_code)
        }


def save_txt_to_file(page_id, file_name, content):
    page_file = open('out/' + str(page_id) + '/' + file_name, "w")
    page_file.write(content.encode('utf8'))
    page_file.close()


def create_page_folder(page_id):
    os.mkdir('out/'+str(page_id))


def fetch_all_raw_page_data(page_id):

    print 'Fetching page: '+str(page_id)
    main_page = fetch_wykop_page(page_id)

    if main_page['exists']:

        create_page_folder(page_id)

        # real url of the page
        save_txt_to_file(page_id, str(page_id) + "_info.txt", str(page_id)+' '+main_page['url'])

        # page content
        save_txt_to_file(page_id, str(page_id) + "_main.html", main_page['body'])

        # up votes
        print 'Fetching up votes on page: ' + str(page_id)
        up_votes_page = fetch_up_votes(page_id)
        if up_votes_page['exists']:
            save_txt_to_file(page_id, str(page_id) + "_up_votes.js", up_votes_page['body'])
        else:
            save_txt_to_file(page_id, str(page_id) + "_up_votes_error.txt", up_votes_page['error'])

        # down votes
        print 'Fetching down votes on page: ' + str(page_id)
        down_votes_page = fetch_down_votes(page_id)
        if down_votes_page['exists']:
            save_txt_to_file(page_id, str(page_id) + "_down_votes.js", down_votes_page['body'])
        else:
            save_txt_to_file(page_id, str(page_id) + "_down_votes_error.txt", down_votes_page['error'])

        # all comments
        comment_pages = number_of_comment_pages(main_page['body'])
        for cpn in range(2, comment_pages+1):
            print 'Fetching comments page number :'+str(cpn)+' on page: ' + str(page_id)
            cp = fetch_comment_page(main_page['url'], cpn)
            if cp['exists']:
                save_txt_to_file(page_id, str(page_id) + "_comments_"+str(cpn)+".html", cp['body'])
            else:
                save_txt_to_file(page_id, str(page_id) + "_comments_" + str(cpn) + "_error.txt", cp['error'])
    else:
        print 'Page: ' + str(page_id)+' not exists'

# 1 comment, no pages: 3953285
# 16 pages of comments: 3953283
# 2 pages of comments: 3953291

# fetch_all_raw_page_data(3953283)

for i in range(3953283, 3953365):
    fetch_all_raw_page_data(i)

#print os.listdir('out')
