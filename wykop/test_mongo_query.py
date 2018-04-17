from pymongo import MongoClient

c = MongoClient()
if "test_mongo_query" in c.database_names():
    print "Test db 'test_mongo_query' already exists."
    c.drop_database("test_mongo_query")
    print "Dropped"

pages = c.test_mongo_query.pages

pages.insert_many([
    {
        "_id": 0,
    },
    {
        "_id": 1,
        "d": [{
            "m": {"id": "p1m"}
        }]
    },
    {
        "_id": 2,
        "d": [{
            "m": {"id": "p2m"},
            "r": []
        }]
    },
    {
        "_id": 3,
        "d": [{
            "m": {"id": "p3m0"},
            "r": [{"id": "p3m0r0"}]
        },
            {
                "m": {"id": "p3m1"},
                "r": [{"id": "p3m1r0"}]
            },
        ]
    },
    {
        "_id": 4,
        "d": [{
            "m": {"id": "p4m0"},
            "r": [{"id": "p4m0r0"}, {"id": "p4m0r1"}]
        }]
    },
    {
        "_id": 5,
        "d": [{
            "m": {"id": "p5m0"},
            "r": [{"id": "p5m0r0"}, {"id": "p5m0r1"}, {"id": "p5m0r2"}]
        },
            {
                "m": {"id": "p5m1"},
                "r": [{"id": "p5m1r0"}]
            },
            {
                "m": {"id": "p5m2"},
                "r": [{"id": "p5m2r0"}, {"id": "p5m2r1"}]
            },
            {
                "m": {"id": "p5m3"},
            }
        ]

    },
])

assert 6 == len(list(pages.find()))

# collect all comments
pc = pages.aggregate([
    {"$unwind": {"path": "$d"}},
    {"$project": {"_id": "$_id", "c": {"$setUnion": [["$d.m"], {"$ifNull": ["$d.r", []]}]}}},
    {"$unwind": {"path": "$c"}},
    {"$group": {"_id": "$_id", "comments": {"$push": "$c"}}},
    {"$project": {"_id": "$_id", "comments": "$comments"}},
])

for p in pc:
    print p
    if p['_id'] == 1:
        assert p == {u'_id': 1, u'comments': [{u'id': u'p1m'}]}
    if p['_id'] == 2:
        assert p == {u'_id': 2, u'comments': [{u'id': u'p2m'}]}
    if p['_id'] == 3:
        assert p == {u'_id': 3, u'comments': [{u'id': u'p3m0'}, {u'id': u'p3m0r0'}, {u'id': u'p3m1'}, {u'id': u'p3m1r0'}]}
    if p['_id'] == 4:
        assert p == {u'_id': 4, u'comments': [{u'id': u'p4m0'}, {u'id': u'p4m0r0'}, {u'id': u'p4m0r1'}]}
    if p['_id'] == 5:
        assert p == {u'_id': 5, u'comments': [{u'id': u'p5m0'}, {u'id': u'p5m0r0'}, {u'id': u'p5m0r1'}, {u'id': u'p5m0r2'}, {u'id': u'p5m1'}, {u'id': u'p5m1r0'}, {u'id': u'p5m2'}, {u'id': u'p5m2r0'}, {u'id': u'p5m2r1'}, {u'id': u'p5m3'}]}


c.drop_database("test_mongo_query")
