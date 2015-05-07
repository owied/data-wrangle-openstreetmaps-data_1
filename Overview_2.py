
#I "bulk" imported the created json file using mongoimport:
#mongoimport --file san-diego-tijuana_mexico.osm.json
#.....imported 1594251 documents

from pymongo import MongoClient
import re


#mongoimport -d sd -c data --file sample.osm.json --drop

#OVERVIEW-------------------------------------

def get_db(dbase):
    client = MongoClient('localhost:27017')
    db = client[dbase]
    return db

#Access database
db = get_db("sd") 

#Number of files
db.data.find().count() #1594251
#Number of nodes
db.data.find({"type":"node"}).count() #1480433
#Number of ways
db.data.find({"type":"way"}).count() #113818
# Top 1 contributing user
result = db.data.aggregate([{"$group":{"_id":"$created.user","count":{"$sum":1}}},{"$sort":{"count":-1}},{"$limit":1}])
print list(result) #[{u'count': 684272, u'_id': u'Adam Geitgey'}]
# Number of users appearing only once (having 1 post)
result2 = db.data.aggregate([{"$group":{"_id":"$created.user", "count":{"$sum":1}}}, {"$group":{"_id":"$count", "num_users":{"$sum":1}}}, {"$sort":{"_id":1}}, {"$limit":1}])
print list(result2) #[{u'num_users': 189, u'_id': 1}]



#MORE CLEANING-------------------------------------

postcodes = db.data.find({"address.postcode":{"$exists":True}})
#Find postcodes which are not numbers:
postcodes_non_numeric = postcodes.collection.find({"address.postcode":{"$regex":"[^0-9]"}})
postcodes_non_numeric.count() #47
#Print the result
for a in postcodes_non_numeric:
    print a["address"]["postcode"]
    
for a in postcodes_non_numeric:
    x = re.split("-",a["address"]["postcode"])
    a["address"]["postcode"] = x[0]
    if len(x) > 1:
        a["address"]["postbox"] = x[1] #create new tag
    db.data.save(a)

postcodes_non_numeric = postcodes.collection.find({"address.postcode":{"$regex":"[^0-9]"}})
for a in postcodes_non_numeric:
    x = re.split(" ",a["address"]["postcode"])
    if  x[0] == "CA":
        a["address"]["state"] = "CA"
        a["address"]["postcode"] = x[1]
    else:
        del a["address"]["postcode"] #delete others
    db.data.save(a)

postcodes.collection.find({"address.postcode":{"$regex":"[^0-9]"}}).count() #0
db.data.find_one({"address.postbox":{"$exists":True}})


#OVERVIEW OF RESTAURANTS-------------------------------------

#Number of restaurants
db.data.find({"amenity":"restaurant"}).count() #643
db.data.find({"$and":[{"amenity":"restaurant"},{"type":"node"}]}).count() #544
db.data.find({"$and":[{"amenity":"restaurant"},{"type":"way"}]}).count() #99
#Number of restaurants with (partial) addresss information
db.data.find({"$and":[{"amenity":"restaurant"},{"is_in:country_code": {"$exists": True}}]}).count() #160


    
