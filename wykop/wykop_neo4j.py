import os
import json
import pprint
from neo4j.v1 import GraphDatabase

ADD_PAGE_QUERY = """
MERGE (p:Page {id: $id})
ON CREATE SET p.description=$desc, p.url=$url, p.up_votes=0, p.down_votes=0, p.tags=0
MERGE (u:User {name: $name})
ON CREATE SET u.up_votes=0, u.down_votes=0, u.posts=0
MERGE (u)-[:POST]->(p)
ON CREATE SET u.posts=u.posts+1
"""

UP_VOTE_PAGE_QUERY = """
MERGE (p:Page {id: $id})
ON CREATE SET p.description=$desc, p.url=$url, p.up_votes=0, p.down_votes=0, p.tags=0
MERGE (u:User {name: $name})
ON CREATE SET u.up_votes=0, u.down_votes=0, u.posts=0
MERGE (u)-[:UP_VOTE]->(p)
ON CREATE SET u.up_votes=u.up_votes+1, p.up_votes=p.up_votes+1
"""

DOWN_VOTE_PAGE_QUERY = """
MERGE (p:Page {id: $id})
ON CREATE SET p.description=$desc, p.url=$url, p.up_votes=0, p.down_votes=0, p.tags=0
MERGE (u:User {name: $name})
ON CREATE SET u.up_votes=0, u.down_votes=0, u.posts=0
MERGE (u)-[:DOWN_VOTE]->(p)
ON CREATE SET u.down_votes=u.down_votes+1, p.down_votes=p.down_votes+1
"""

ADD_TAG_TO_PAGE = """
MERGE (p:Page {id: $id})
ON CREATE SET p.description=$desc, p.url=$url, p.up_votes=0, p.down_votes=0, p.tags=0
MERGE (t:Tag {name: $name})
ON CREATE SET t.pages=0
MERGE (p)-[:HAS_TAG]->(t)
ON CREATE SET t.pages=t.pages+1, p.tags=p.tags+1
"""


def add_page(tx, page):
    tx.run(ADD_PAGE_QUERY, id=page['id'], desc=page['description'], url=page['url'], name=page['author'])


def up_vote_page(tx, page_id, page_description, page_url, voter_name):
    tx.run(UP_VOTE_PAGE_QUERY, id=page_id, desc=page_description, url=page_url, name=voter_name)


def down_vote_page(tx, page_id, page_description, page_url, voter_name):
    tx.run(DOWN_VOTE_PAGE_QUERY, id=page_id, desc=page_description, url=page_url, name=voter_name)


def add_tag_to_page(tx, page_id, page_description, page_url, tag_name):
    tx.run(ADD_TAG_TO_PAGE, id=page_id, desc=page_description, url=page_url, name=tag_name)


driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'Password1'))
session = driver.session()


def add_page_to_db(page):

    print("Adding page: " + str(page['id']))
    session.write_transaction(add_page, page)

    for up_vote in page['up_voters']:
        print ("Adding up votes: %s -> %s %s %s" % (up_vote['user'], page['id'], page['description'], page['url']))
        session.write_transaction(up_vote_page, page['id'], page['description'], page['url'], up_vote['user'])

    for down_vote in page['down_voters']:
        print ("Adding down votes: %s -> %s %s %s" % (down_vote['user'], page['id'], page['description'], page['url']))
        session.write_transaction(down_vote_page, page['id'], page['description'], page['url'], down_vote['user'])

    for tag in page['keys']:
        print ("Adding tag: %s -> %s %s %s" % (tag, page['id'], page['description'], page['url']))
        session.write_transaction(add_tag_to_page, page['id'], page['description'], page['url'], tag)


for page_id in os.listdir('out'):
    page = json.load(open('out/' + page_id + '/' + page_id + '_data.json'))
    pprint.pprint(page)
    print "-----------------------------------"
    add_page_to_db(page)
    print "==================================="


"""
page_ids = os.listdir('out')

for i in range(3, 10):
    page_id = page_ids[i]

    page = json.load(open('out/' + page_id + '/' + page_id + '_data.json'))
    pprint.pprint(page)
    print "-----------------------------------"
    add_page_to_db(page)
    print "==================================="
"""

"""
page_id = page_ids[5]

page = json.load(open('out/' + page_id + '/' + page_id + '_data.json'))
pprint.pprint(page)
print "-----------------------------------"
add_page_to_db(page)
print "==================================="
"""

driver.close()
