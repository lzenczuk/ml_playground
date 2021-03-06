from pymongo import MongoClient
import os
import pprint
import json

client = MongoClient()
db = client.wykop
pages = db.pages
users = db.users

# insert
number_of_pages = len(os.listdir('out'))
counter = 0

for page_id in os.listdir('out'):
    page = json.load(open('out/' + page_id + '/' + page_id + '_data.json'))
    page['_id'] = page['page_id']
    del page['page_id']
    print "Page %d of %d -> %s" % (counter, number_of_pages, page_id)
    pprint.pprint(page)
    print "-----------------------------------"
    result = pages.insert_one(page)
    print result.inserted_id
    print "==================================="

###########################################################
# Converting pages into user documents ####################
###########################################################

def add_field_to_user(user_id, field_name, value):
    user = users.find_one({"_id": user_id})
    if user is None:
        user = {"_id": user_id}
        users.insert_one(user)

    users.update_one({"_id": user['_id']}, {"$set": {field_name: value}})


# Pages posted by user
for posted in pages.aggregate([
    {"$group": {"_id": "$author", "posted_pages": {"$push": "$_id"}}},
]):
    add_field_to_user(posted['_id'], 'posted_pages', posted['posted_pages'])


# Pages up_voted by user
for upv in pages.aggregate([
    {"$project": {"_id": "$_id", "up_voters": "$up_voters"}},
    {"$unwind": {"path": "$up_voters"}},
    {"$group": {"_id": "$up_voters.user", "up_voted_pages": {"$push": "$_id"}}},
]):
    add_field_to_user(upv['_id'], 'up_voted', upv['up_voted_pages'])


# Pages down_voted by user
for dov in pages.aggregate([
    {"$project": {"_id": "$_id", "down_voters": "$down_voters"}},
    {"$unwind": {"path": "$down_voters"}},
    {"$group": {"_id": "$down_voters.user", "down_voted_pages": {"$push": "$_id"}}},
]):
    add_field_to_user(dov['_id'], 'down_voted', dov['down_voted_pages'])



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
    {"$project": {"_id": "$_id", "d": "$discussions"}},
    {"$unwind": {"path": "$d"}},
    {"$project": {"_id": "$_id", "c": {"$setUnion": [["$d.main"], "$d.responses"]}}},
    {"$unwind": {"path": "$c"}},
    {"$group": {"_id": "$_id", "comments": {"$push": "$c"}}},
    {"$project": {"_id": "$_id", "comments": "$comments"}},
    {"$out": "page_comments"},
]):
    pprint.pprint(page)
"""

# pages up voted by user
# pprint.pprint(list(pages.find({'up_voters': {'$elemMatch': {'user': 'pentan1'}}})))

# poroniony_ Qp017

# pages posted by user
# pprint.pprint(list(pages.find({'author': 'pentan1'})))
# pprint.pprint(list(pages.find({'author': 'Qp017'}, {"id": 1, "up_votes": 1, "down_votes": 1, "description": 1})))
# pprint.pprint(list(pages.find({'author': 'poroniony_'}, {"id": 1, "up_votes": 1, "down_votes": 1, "description": 1})))

# page
# pprint.pprint(list(pages.find({"id": "3953765"}))[0])

# Up and down votes statistics
"""
pprint.pprint(list(pages.aggregate([
    {"$group": {
        "_id": "null",
        "max_down_votes": {"$max": "$down_votes"},
        "avg_down_votes": {"$avg": "$down_votes"},
        "std_down_votes": {"$stdDevSamp": "$down_votes"},
        "max_up_votes": {"$max": "$up_votes"},
        "avg_up_votes": {"$avg": "$up_votes"},
        "std_up_votes": {"$stdDevSamp": "$up_votes"},
    }}
]))[0])
"""

# pprint.pprint(list(pages.find({"$and": [{'down_votes': {'$gt': 27}}, {"up_votes": {"$lt": 10}}]}, {"id": 1, "up_votes": 1, "down_votes": 1, "description": 1})))

"""
# all tags list
for page in pages.distinct('keys'):
    pprint.pprint(page)
"""

"""
# votes per tag
for page in pages.aggregate([
    {"$project": {"k": "$keys", "u": "$up_voters"}},
    {"$unwind": {"path": "$k"}},
    {"$unwind": {"path": "$u"}},
    {"$group": {"_id": {"user": "$u.user", "key": "$k"}, "counter": {"$sum": 1}}},
    {"$group": {"_id": "$_id.user", "keys": {"$push": {"key": "$_id.key", "count": "$counter"}}}},
]):
    pprint.pprint(page)
"""

"""
# votes per tag
for page in pages.aggregate([
    {"$project": {"id": "$id", "d": "$description"}},
]):
    pprint.pprint(page)
"""

"""
# pages taged with key
pages_id = []
for p in list(pages.find({'keys': '4konserwy'}, {"id": 1, "description": 1})):
    pages_id.append(p['id'])
"""

# find authors of pages
# pprint.pprint(list(pages.find({"id": {"$in": pages_id}}, {"id": 1, "author": 1})))

"""
print "POST -------------------------------------------------------"

# authors of pages
for page in pages.aggregate([
    {'$match': {"id": {"$in": pages_id}}},
    {'$group': {"_id": "$author", "count": {"$sum": 1}}},
    {'$sort': {"count": -1}},
]):
    pprint.pprint(page)

print "UP-----------------------------------------------------------"

# up voters of pages
for page in pages.aggregate([
    {'$match': {"id": {"$in": pages_id}}},
    {'$unwind': {"path": "$up_voters"}},
    {'$project': {'user': "$up_voters.user"}},
    {'$group': {"_id": "$user", "count": {"$sum": 1}}},
    {'$sort': {"count": -1}},
]):
    pprint.pprint(page)

print "DOWN---------------------------------------------------------"

# down voters of pages
for page in pages.aggregate([
    {'$match': {"id": {"$in": pages_id}}},
    {'$unwind': {"path": "$down_voters"}},
    {'$project': {'user': "$down_voters.user"}},
    {'$group': {"_id": "$user", "count": {"$sum": 1}}},
    {'$sort': {"count": -1}},
]):
    pprint.pprint(page)
"""