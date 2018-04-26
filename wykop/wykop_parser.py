import json
import os

from bs4 import BeautifulSoup
from bs4 import NavigableString


def _select_one(tag, select_string, index):
    if tag is None:
        return None

    tags = tag.select(select_string)
    if len(tags) > index:
        return tags[index]
    else:
        return None


def _select_list(tag, select_string):
    if tag is None:
        return []

    return tag.select(select_string)


def _attr(tag, attr_name):
    if tag is None:
        return None

    if attr_name not in tag.attrs:
        return None

    return tag.attrs[attr_name]


def _select_attr_lambda(tag, select_string, index, attr_name, func):
    attr = _attr(_select_one(tag, select_string, index), attr_name)
    if attr is None:
        return None

    return func(attr)


def _select_attr(tag, select_string, index, attr_name):
    attr = _attr(_select_one(tag, select_string, index), attr_name)
    if attr is None:
        return None

    return attr


def _extract_text(tag):
    if tag is None:
        return None

    if isinstance(tag, NavigableString):
        return tag.string.strip()

    if tag.name == 'a':
        if 'href' in tag.attrs:
            return ' ' + tag.attrs['href'] + ' '
        else:
            return " "

    if tag.name == 'br':
        return "\n"

    text = ""
    for cn in tag.contents:
        text = text + _extract_text(cn)

    return text


class WykopPage:
    """
    Class representing data on wykop page.
    """

    def __init__(self, page_text, up_votes_text=None, down_votes_text=None):
        """
        Construct page model from wykop data
        :param page_text: str individual wykop html page
        :param up_votes_text: str string representing response for up votes
        :param down_votes_text: str string representing response for up votes
        """

        page_dom = BeautifulSoup(page_text, "html.parser")

        if up_votes_text is not None:
            up_voters_json = up_votes_text.replace("for(;;);", "", 1)
            up_voters_html = json.loads(up_voters_json)['operations'][2]['html']
            self._up_voters_dom = BeautifulSoup(up_voters_html, "html.parser")
            self._up_voters = WykopVoters(self._up_voters_dom)
        else:
            self._up_voters = WykopVoters(None)

        if down_votes_text is not None:
            down_voters_json = down_votes_text.replace("for(;;);", "", 1)
            down_voters_html = json.loads(down_voters_json)['operations'][2]['html']
            self._down_voters_dom = BeautifulSoup(down_voters_html, "html.parser")
            self._down_voters = WykopVoters(self._down_voters_dom)
        else:
            self._down_voters = WykopVoters(None)

        self._page_ = page_dom
        self._mainPanelTag_ = _select_one(self._page_, "div#site div.grid div.grid-main", 0)
        self._rightPanelTag_ = _select_one(self._page_, "div#site div.grid-right", 0)

        self._contentPanelTag_ = _select_one(self._mainPanelTag_, "div.rbl-block", 0)
        self._votesPanelTag_ = _select_one(self._mainPanelTag_, "div.rbl-block", 1)
        self._discussions_ = WykopDiscussions(_select_one(self._mainPanelTag_, "ul.comments-stream", 0))

        self._infoPanel_ = _select_one(self._rightPanelTag_, "div.information", 0)

    def page_id(self):
        u = self.url()
        if u is None:
            return None

        url_prefix_len = len("http://www.wykop.pl/link/")

        if u.startswith("https"):
            url_prefix_len = len("https://www.wykop.pl/link/")

        return u[url_prefix_len:].split('/')[0]

    def url(self):
        return _select_attr(self._page_, 'meta[property="og:url"]', 0, 'content')

    def author(self):
        return _select_attr_lambda(self._page_, 'meta[property="article:author"]', 0, 'content',
                                   lambda s: s.split('/')[-2])

    def description(self):
        return _select_attr_lambda(self._page_, 'meta[property="og:description"]', 0, 'content', lambda s: s.strip())

    def keys(self):
        def split_keys(s):
            return s.replace(',', '').replace('#', '').split(' ')

        return _select_attr_lambda(self._page_, 'meta[name="keywords"]', 0, 'content', split_keys)

    def link(self):
        return _select_attr(self._page_, 'div.fix-tagline span a.affect', 0, 'href')

    def add_time(self):
        return _select_attr(self._page_, 'div.information b time', 0, 'datetime')

    def display(self):
        ds = _select_one(self._infoPanel_, 'tr.infopanel td b', 2)
        if ds is None:
            return None

        return ds.string

    def up_votes(self):
        ds = _select_one(self._infoPanel_, 'tr.infopanel td b', 0)
        if ds is None:
            return 0

        return int(ds.string)

    def down_votes(self):
        ds = _select_one(self._infoPanel_, 'tr.infopanel td b', 1)
        if ds is None:
            return 0

        return int(ds.string)

    def votes(self):
        return self.up_votes() - self.down_votes()

    def up_voters(self):
        return self._up_voters

    def down_voters(self):
        return self._down_voters

    def annotation(self):
        an = _select_one(self._contentPanelTag_, 'div.annotation p', 0)
        if an is None:
            return None

        return an.string

    def discussions(self):
        return self._discussions_

    def to_dict(self):
        return {
            'page_id': self.page_id(),
            'url': self.url(),
            'author': self.author(),
            'annotation': self.annotation(),
            'description': self.description(),
            'keys': self.keys(),
            'link': self.link(),
            'add_time': self.add_time(),
            'display': self.display(),
            'votes': self.votes(),
            'up_votes': self.up_votes(),
            'down_votes': self.down_votes(),
            'discussions': self.discussions().to_dict(),
            'up_voters': self.up_voters().to_dict(),
            'down_voters': self.down_voters().to_dict(),
        }


class WykopVoters:
    def __init__(self, voters_tag):
        self._voters_tag = voters_tag

        self._votes = []

        if self._voters_tag is not None:
            for v in _select_list(self._voters_tag, 'div.usercard'):
                self._votes.append(WykopVote(v))

    def votes(self):
        return self._votes

    def to_dict(self):
        v = []
        for vt in self.votes():
            v.append(vt.to_dict())

        return v


class WykopVote:
    def __init__(self, vote_div):
        self._vote_div = vote_div

    def user(self):
        u = _select_attr(self._vote_div, 'a["title"]', 0, 'title')
        # When user removed account there is no link. Try to extract from b tag
        if u is None:
            u = _extract_text(_select_one(self._vote_div, 'b', 0))

        return u

    def vote_time(self):
        return _select_attr(self._vote_div, 'span.info time', 0, 'datetime')

    def to_dict(self):
        return {
            'user': self.user(),
            'vote_time': self.vote_time()
        }


class WykopDiscussions:
    def __init__(self, comments_panel_tag):
        self._comments_panel_tag_ = comments_panel_tag

        self._discusions_ = []

        select_list = _select_list(self._comments_panel_tag_, "li.iC")
        for dis in select_list:
            self._discusions_.append(WykopDiscussion(dis))

        self._index = len(self._discusions_)

    def len(self):
        return len(self._discusions_)

    def all(self):
        return self._discusions_

    def to_dict(self):
        ds = []
        for d in self.all():
            ds.append(d.to_dict())

        return ds


class WykopDiscussion:
    def __init__(self, discussion_li_tag):
        self.discussion_li_tag = discussion_li_tag

        self._main_comment_ = WykopComment(_select_one(self.discussion_li_tag, "div", 0))
        self._responses_ = []

        for divs in _select_list(self.discussion_li_tag, "ul li > div.wblock.lcontrast.dC"):
            self._responses_.append(WykopComment(divs))

    def main_comment(self):
        return self._main_comment_

    def responses(self):
        return self._responses_

    def to_dict(self):
        rs = []
        for r in self.responses():
            rs.append(r.to_dict())

        return {
            'main': self.main_comment().to_dict(),
            'responses': rs
        }


class WykopComment:
    def __init__(self, comment_div_tag):

        self._comment_div_tag_ = comment_div_tag

    def comment_id(self):
        did = _attr(self._comment_div_tag_, 'data-id')
        return did

    def author(self):
        return _select_attr_lambda(self._comment_div_tag_, 'a.profile', 0, 'href', lambda s: s.split('/')[-2])

    def add_time(self):
        return _select_attr(self._comment_div_tag_, 'div.author time', 0, 'datetime')

    def up_votes(self):
        up = _select_attr(self._comment_div_tag_, 'div.author p.vC', 0, 'data-vcp')
        if up is None:
            return 0

        return abs(int(up))

    def down_votes(self):
        dw = _select_attr(self._comment_div_tag_, 'div.author p.vC', 0, 'data-vcm')
        if dw is None:
            return 0

        return abs(int(dw))

    def votes(self):
        return self.up_votes() - self.down_votes()

    def content(self):
        text = _extract_text(_select_one(self._comment_div_tag_, 'div.text', 0))
        if text is None:
            return None

        return text.strip()

    def to_dict(self):
        return {
            'comment_id': self.comment_id(),
            'author': self.author(),
            'add_time': self.add_time(),
            'votes': self.votes(),
            'up_votes': self.up_votes(),
            'down_votes': self.down_votes(),
            'content': self.content(),
        }


"""
mf = open('out/3953309/3953309_main.html')
main_page_txt = mf.read()
mf.close()

mf = open('out/3953309/3953309_up_votes.js')
up_votes_txt = mf.read()
mf.close()

mf = open('out/3953309/3953309_down_votes.js')
down_votes_txt = mf.read()
mf.close()
"""

"""
mf = open('out/3953309/3953309_comments_2.html')
main_page_txt = mf.read()
mf.close()

#pprint.pprint(WykopPage(main_page_txt, up_votes_txt, down_votes_txt).to_dict())

pprint.pprint(WykopPage(main_page_txt).to_dict())
"""


def parse_all_page_files(page_dir):
    mf = open('out/' + page_dir + '/' + page_dir + '_main.html')
    main_page_txt = mf.read()
    mf.close()

    mf = open('out/' + page_dir + '/' + page_dir + '_up_votes.js')
    up_votes_txt = mf.read()
    mf.close()

    mf = open('out/' + page_dir + '/' + page_dir + '_down_votes.js')
    down_votes_txt = mf.read()
    mf.close()

    main_dict = WykopPage(main_page_txt, up_votes_txt, down_votes_txt).to_dict()

    for page_file_name in os.listdir('out/' + page_dir):
        if "_comments_" in page_file_name:
            mf = open('out/' + page_dir + '/' + page_file_name)
            comment_page_txt = mf.read()
            mf.close()
            comment_dict = WykopPage(comment_page_txt).to_dict()
            main_dict['discussions'] = main_dict['discussions'] + comment_dict['discussions']

    return main_dict


def save_result_dict(page_dir, dict):
    mf = open('out/' + page_dir + '/' + page_dir + '_data.json', 'w')
    mf.write(json.dumps(dict))
    mf.close()


number_of_pages = len(os.listdir('out'))
counter = 0

for page_dir in os.listdir('out'):
    print "Page %d of %d -> %s" % (counter, number_of_pages, page_dir)
    main_dict = parse_all_page_files(page_dir)
    save_result_dict(page_dir, main_dict)
    counter = counter + 1

# save_result_dict('3953283', parse_all_page_files('3953283'))
