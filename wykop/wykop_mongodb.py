from pymongo import MongoClient
import os
import pprint
import json

client = MongoClient()
db = client.wykop
pages = db.pages

"""
# insert
number_of_pages = len(os.listdir('out'))
counter = 0

for page_id in os.listdir('out'):
    page = json.load(open('out/' + page_id + '/' + page_id + '_data.json'))
    print "Page %d of %d -> %s" % (counter, number_of_pages, page_id)
    pprint.pprint(page)
    print "-----------------------------------"
    result = pages.insert_one(page)
    print result.inserted_id
    print "==================================="
"""

"""
# get all pages
for page in pages.find():
    pprint.pprint(page['author'])
"""

"""
# count posted pages
for page in pages.aggregate([
    {"$group": {"_id": "$author", "posts": {"$sum": 1}}}
]):
    pprint.pprint(page)
"""

"""
# stats posted pages
for page in pages.aggregate([
    {"$group": {"_id": "$author", "posts": {"$sum": 1}}},
    {"$group": {"_id": "null", "std_dev_posts": {"$stdDevSamp": "$posts"}}},
]):
    pprint.pprint(page)

for page in pages.aggregate([
    {"$group": {"_id": "$author", "posts": {"$sum": 1}}},
    {"$group": {"_id": "null", "max": {"$max": "$posts"}}},
]):
    pprint.pprint(page)

for page in pages.aggregate([
    {"$group": {"_id": "$author", "posts": {"$sum": 1}}},
    {"$group": {"_id": "null", "avg": {"$avg": "$posts"}}},
]):
    pprint.pprint(page)
"""

"""
# stats up votes
for page in pages.aggregate([
    {"$group": {"_id": "null", "std_dev_up_votes": {"$stdDevSamp": "$up_votes"}}},
]):
    pprint.pprint(page)

for page in pages.aggregate([
    {"$group": {"_id": "null", "max": {"$max": "$up_votes"}}},
]):
    pprint.pprint(page)

for page in pages.aggregate([
    {"$group": {"_id": "null", "avg": {"$avg": "$up_votes"}}},
]):
    pprint.pprint(page)
"""

"""
# number of up votes per user 
for page in pages.aggregate([
    {"$unwind": {"path": "$up_voters"}},
    {"$group": {"_id": "$up_voters.user", "up_votes": {"$sum": 1}}}
]):
    pprint.pprint(page)
"""

"""
# user's up voted pages
for page in pages.aggregate([
    {"$unwind": {"path": "$up_voters"}},
    {"$group": {"_id": "$up_voters.user", "pages": {"$addToSet": "$id"}}}
]):
    pprint.pprint(page)
"""

"""
# tags of up voted pages
for page in pages.aggregate([
    {"$unwind": {"path": "$up_voters"}},
    {"$unwind": {"path": "$keys"}},
    {"$group": {"_id": "$up_voters.user", "keys": {"$push": "$keys"}}}
]):
    pprint.pprint(page)
"""

"""
# count tags of up voted pages
for page in pages.aggregate([
    {"$unwind": {"path": "$up_voters"}},
    {"$unwind": {"path": "$keys"}},
    {"$group": {"_id": {"user": "$up_voters.user", "tag": "$keys"}, "tag_count": {"$sum": 1}}},
    {"$group": {"_id": "$_id.user", "tags": {"$push": {"tag": "$_id.tag", "count": "$tag_count"}}}}
]):
    pprint.pprint(page)
"""

"""
# tags frequency
for page in pages.aggregate([
    {"$unwind": {"path": "$keys"}},
    {"$group": {"_id": "$keys", "occurs": {"$sum": 1}}},
    {"$sort": {"occurs": -1}}
]):
    pprint.pprint(page)
"""

"""
# page's comments
for page in pages.aggregate([
    {"$project": {"id": "$id", "d": "$discussions"}},
    {"$unwind": {"path": "$d"}},
    {"$project": {"page_id": "$id", "c": {"$setUnion": [["$d.main"], "$d.responses"]}}},
    {"$unwind": {"path": "$c"}},
    {"$group": {"_id": "$page_id", "comments": {"$push": "$c"}}},
    {"$project": {"_id": "$_id.page_id", "comments": "$comments"}},
]):
    pprint.pprint(page)
"""