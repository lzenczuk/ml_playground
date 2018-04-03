import time

from retrying import retry
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def is_browser_exception(ex):
    if isinstance(ex, StaleElementReferenceException):
        return True

    return False


# http://www.audible.com/sitemap


class Audible:
    """Stateful page audible page wrapper"""

    driver = None

    def __init__(self, driver_path=None):
        """
        Audible page wrapper constructor. To get access to page content user have to sign in.
        :param user: audible user's name
        :param password: audible user's password
        """

        if driver_path is None:
            self.driver = webdriver.Firefox()
        else:
            print("Alter gecko path")
            self.driver = webdriver.Firefox(executable_path=driver_path)

    def close(self):
        self.driver.close()

    def open_audible_com(self):
        """Open main audible com page. It doesn't have search field what may cause some problems"""
        self.driver.get("http://www.audible.com")

        self._go_to_audible_com_if_on_uk_page()

    def open_audible_com_sitemap(self):
        """Open site map page. This page contain search field so in some cases it is better as start page"""
        self.driver.get("http://www.audible.com/sitemap")

        self._go_to_audible_com_if_on_uk_page()

    def _is_audible_uk(self):
        return 'Audible UK' in self.driver.title

    def _is_audible_com(self):
        return 'Audible.com' in self.driver.title

    def _go_to_audible_com_if_on_uk_page(self):
        if self._is_audible_uk():
            self._follow_link_to_audible_com()

            if not self._is_audible_com():
                raise RuntimeError("Couldn't open audible.com. Tried to follow links from audible uk but fail.")

        else:
            if not self._is_audible_com():
                raise RuntimeError("Couldn't open audible.com. Probably on one of national audible versions "
                                   "and can't find redirection link")

    def _follow_link_to_audible_com(self):
        assert 'Audible UK' in self.driver.title
        element = self.driver.find_element_by_link_text("go to audible.com")

        assert element.tag_name == 'a'
        assert element.text == 'go to audible.com'
        assert 'audible.com' in element.get_attribute("href")

        element.click()

    def _follow_link_to_sign_in(self):
        assert 'Audible.com' in self.driver.title

        element = self.driver.find_element_by_link_text("Sign In")

        assert element.tag_name == 'a'
        assert element.text == 'Sign In'
        assert 'www.amazon.com/ap/signin' in element.get_attribute("href")

        element.click()

        # check are we on audible com
        assert 'Amazon Sign In' in self.driver.title

    def _sign_in_to_amazon_com(self, user, password):
        assert 'Amazon Sign In' in self.driver.title

        email_element = self.driver.find_element_by_name("email")
        email_element.send_keys(user)
        password_element = self.driver.find_element_by_name("password")
        password_element.send_keys(password)

        self.driver.find_element_by_id('signInSubmit').click()

        assert 'Download Audiobooks with Audible.com' in self.driver.title

    def login_to_audible_com(self, user, password):
        self.open_audible_com()
        self._follow_link_to_sign_in()
        self._sign_in_to_amazon_com(user, password)

    def find_first_matching_book(self, text):
        self._submit_search_form(text)

        time.sleep(3)

        books = self._get_search_results()

        if len(books) == 0:
            return None
        else:
            return books[0]

    def find_matching_books(self, text, max_results=None):
        self._submit_search_form(text)

        time.sleep(3)

        books = self._get_search_results()

        if max_results is not None and len(books) >= max_results:
            return books

        while self._load_next_search_result_page():
            b = self._get_search_results()

            books = books + b

            if max_results is not None and len(books) >= max_results:
                return books

        return books

    def _submit_search_form(self, text):
        try:
            # global-search-legacy
            search_element = self.driver.find_element_by_id('global-search-legacy')
        except NoSuchElementException:
            # search on site map page
            search_element = self.driver.find_element_by_id('ftx_topnav_search')

        search_element.send_keys(text, Keys.ENTER)
        ##### Problem with checking on which page we are now
        # don't work -> assert 'Audiobooks matching keywords' in driver.title
        # wait until we get results
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 "body div.desktop > div.bc-container > div.bc-row-responsive > div.bc-col-responsive.bc-col-9 li.bc-list-item.productListItem")
            )
        )
        print "Search executed"

    @retry(stop_max_attempt_number=3, wait_fixed=2000, retry_on_exception=is_browser_exception)
    def _get_search_results(self):
        # every entry is a one row with all book infromations
        entries = self.driver.find_elements_by_css_selector(
            "body div.desktop > div.bc-container > div.bc-row-responsive > div.bc-col-responsive.bc-col-9 li.bc-list-item.productListItem"
        )

        print "Extracting entries: " + str(len(entries))

        books = []

        for entry in entries:

            # left side of book row - description
            description_element = entry.find_element_by_css_selector(
                'div.bc-row-responsive  > div.bc-col-responsive.bc-spacing-top-none.bc-col-8')

            # right side of book row - price, but and wish list buttons
            price_element = entry.find_element_by_css_selector(
                'div.bc-row-responsive  > div.bc-col-responsive.bc-col-4')

            # title line with book link
            title_element = description_element.find_element_by_css_selector(
                "div.bc-col-responsive.bc-col-6 li.bc-list-item a")
            title = title_element.text
            book_link = title_element.get_attribute("href").split('?')[0]

            # authors - book may have multiple authors
            authors_element = description_element.find_elements_by_css_selector(
                "div.bc-col-responsive.bc-col-6 li.bc-list-item.authorLabel > span > a")

            authors = []

            for author_element in authors_element:
                author = author_element.text

                # amazon may have page for specific author or provide search link
                author_link = author_element.get_attribute("href")
                if (author_link.startswith('https://www.audible.com/search')):
                    author_link = author_link.split('&')[0]
                else:
                    author_link = author_link.split('?')[0]

                authors.append(Author(author, author_link))

            books.append(Book(title, book_link, authors))

        return books

    def _load_next_search_result_page(self):
        # pagination
        pagination_button_elements = self.driver.find_elements_by_css_selector(
            "body div.desktop > div.bc-container > div.bc-row-responsive > div.bc-col-responsive.bc-col-9 form.paginationElements button"
        )

        if len(pagination_button_elements) == 2:
            next_page_button = pagination_button_elements[1]

            if next_page_button.get_attribute("disabled") == 'true':
                # last page
                return False
            else:
                next_page_button.click()
                return True

        else:
            # no pagination
            return False

    def open_book_page(self, url):
        self.driver.get(url)

        self._go_to_audible_com_if_on_uk_page()

    def fetch_all_book_reviews(self):
        self._load_all_book_reviews()
        time.sleep(3)
        return self._get_book_reviews()

    def _get_book_reviews(self):
        review_elements = self.driver.find_elements_by_css_selector(
            "div.listReviewsTabUS > div.bc-row-responsive.bc-spacing-top-medium.bc-spacing-medium")

        if len(review_elements) == 0:
            review_elements = self.driver.find_elements_by_css_selector(
                "div.listReviewsTabUK > div.bc-row-responsive.bc-spacing-top-medium.bc-spacing-medium")

        book_reviews = []

        for review_element in review_elements:
            # left bottom side of review section
            reviewer_element = review_element.find_element_by_css_selector(
                "div.bc-col-responsive.bc-col-3 > div.bc-row-responsive.bc-spacing-top-small > div.bc-col-responsive.bc-col-9 a.bc-link.bc-color-link")
            reviewer_name = reviewer_element.text
            reviewer_url = reviewer_element.get_attribute("href").split('?')[0]

            # left top side of review section
            rating_elements = review_element.find_elements_by_css_selector("div.bc-col-responsive.bc-col-3 > span li")

            overall_rating = len(rating_elements[0].find_elements_by_css_selector("i.bc-color-progress"))
            performance_rating = None
            story_rating = None

            if len(rating_elements) > 1:
                performance_rating = len(rating_elements[1].find_elements_by_css_selector("i.bc-color-progress"))

                if len(rating_elements) > 2:
                    story_rating = len(rating_elements[2].find_elements_by_css_selector("i.bc-color-progress"))

            book_reviews.append(Review(reviewer_name, reviewer_url, overall_rating, performance_rating, story_rating))

        return book_reviews

    def _load_all_book_reviews(self):
        while True:
            try:
                reviews_section_element = self.driver.find_element_by_css_selector("div.listReviewsTabUS")
                show_more_button = reviews_section_element.find_element_by_css_selector("div#pagingButtonsUS button")
                show_more_button.click()
            except NoSuchElementException:
                print "No more reviews"
                break;
            except ElementClickInterceptedException:
                print "Problem with click. Waiting 3s..."
                time.sleep(3)
            except StaleElementReferenceException:
                print "Problem with button not connected to DOM tree. Waiting 3s..."
                time.sleep(3)

    def open_user_page(self, url):
        self.driver.get(url)

    def _load_all_user_reviews(self):
        while True:
            try:
                show_more_button = self.driver.find_element_by_css_selector(
                    "div#profile_content > div#adbl-reviews-by-me-cont > div.more-cont > a.adbl-profile-more.adbl-more-link")
                show_more_button.click()
            except NoSuchElementException:
                print "No more reviews"
                break;
            except ElementClickInterceptedException:
                print "Problem with click. Waiting 3s..."
                time.sleep(3)
            except StaleElementReferenceException:
                print "Problem with button not connected to DOM tree. Waiting 3s..."
                time.sleep(3)
            except ElementNotInteractableException:
                print "Problem with button. Waiting 3s..."
                time.sleep(3)

    def _get_user_reviews(self):
        review_elements = self.driver.find_elements_by_css_selector(
            "div#profile_content > div#adbl-reviews-by-me-cont li.adbl-review")

        print len(review_elements)

        for review_element in review_elements:
            book_element = review_element.find_element_by_css_selector("div.adbl-prod-title > a")
            title = book_element.text
            book_link = book_element.get_attribute("href").split('ref')[0][:-1]

            print title + " -> " + book_link


class Book:

    def __init__(self, title, link, authors):
        self.title = title
        self.link = link
        self.authors = authors

    def __str__(self):
        return u'Book {{title: {0}, link: {1}, authors: {2}}}' \
            .format(self.title, self.link, ', '.join(map(str, self.authors))) \
            .encode('ascii', 'xmlcharrefreplace')


class Author:

    def __init__(self, name, link):
        self.name = name
        self.link = link

    def __str__(self):
        return u'Author {{name: {0}, link: {1}}}' \
            .format(self.name, self.link) \
            .encode('ascii', 'xmlcharrefreplace')


class Review:

    def __init__(self, reviewer_name, reviewer_url, book_title, book_url, overall_rating, performance_rating=None, story_rating=None):
        self.author = Author(reviewer_name, reviewer_url)
        self.book_url = book_url
        self.book_title = book_title
        self.overall_rating = overall_rating
        self.performance_rating = performance_rating
        self.story_rating = story_rating

    def __str__(self):
        return u'Review {{ author: {0}, overall: {1}, performance: {2}, story: {3}}}' \
            .format(self.author, self.overall_rating, self.performance_rating, self.story_rating) \
            .encode('ascii', 'xmlcharrefreplace')


au = Audible(driver_path='/home/dev/local/geckodriver/geckodriver')
first_matching_linux_book = au.find_first_matching_book("linux")
au.open_book_page(first_matching_linux_book.link)
reviews = au.fetch_all_book_reviews()

for review in reviews:
    print review
    au.open_user_page(review.author.link)


