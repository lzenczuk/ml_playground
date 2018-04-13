import os
import json
import pprint

import networkx as nx


def add_page_to_graph(G, page):
    print("Adding page: " + str(page['id']))
    G.add_node(page['id'], type="page", attr_dict={"desc": page['description'], "url": page['url']})
    if not G.has_node(page['author']):
        G.add_node(page['author'], type="user")

    G.add_edge(page['author'], page['id'], relation="post")

    for up_vote in page['up_voters']:
        print ("Adding up votes: %s -> %s %s %s" % (up_vote['user'], page['id'], page['description'], page['url']))
        if not G.has_node(up_vote['user']):
            G.add_node(up_vote['user'], type="user")

        G.add_edge(up_vote['user'], page['id'], relation="up_vote")

    for down_vote in page['down_voters']:
        print ("Adding down votes: %s -> %s %s %s" % (down_vote['user'], page['id'], page['description'], page['url']))
        if not G.has_node(down_vote['user']):
            G.add_node(down_vote['user'], type="user")

        G.add_edge(down_vote['user'], page['id'], relation="down_vote")

    for tag in page['keys']:
        print ("Adding tag: %s -> %s %s %s" % (tag, page['id'], page['description'], page['url']))
        if not G.has_node(tag):
            G.add_node(tag, type="tag")
        G.add_edge(tag, page['id'], relation="has_tag")


number_of_pages = len(os.listdir('out'))
counter = 0

G = nx.Graph()

for page_id in os.listdir('out'):
    page = json.load(open('out/' + page_id + '/' + page_id + '_data.json'))
    print "Page %d of %d -> %s" % (counter, number_of_pages, page_id)
    pprint.pprint(page)
    print "-----------------------------------"
    add_page_to_graph(G, page)
    print "==================================="

nx.write_graphml(G, "wykop.graphml")

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

