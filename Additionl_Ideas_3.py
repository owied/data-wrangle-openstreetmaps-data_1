
from pymongo import MongoClient

def get_db(dbase):
    client = MongoClient('localhost:27017')
    db = client[dbase]
    return db

#Access database
db = get_db("sd") 

#ADDITIONAL IDEAS-------------------------------------

#Number of restaurants with location information
restaurants = db.data.find({"$and":[{"amenity":"restaurant"},{"pos": {"$exists": True}}]})
restaurants.count() #544

db.data.find_one({"$and":[{"amenity":"restaurant"},{"address": {"$exists": True}}]})

#The border Mexico - USA through San Diego and Tijuana
#follows approximately this simple straight line
#with x is latitude and y longitude:
#y = 0.0906502699248 * (x + 117.124002) +  32.533842

def us_border(pos):
    x,y = pos #unpack the position array
    if (0.0906502699248 * (x + 117.124002) +  32.533842) < y:
        return False #on the Mexican side
    else:
        return True

#Update "is_in;country_code" information according to the function above
for r in restaurants:
    if us_border(r["pos"]):
        r["is_in:country_code"] = "US"
    else:
        r["is_in:country_code"] = "MX"
    db.data.save(r)

db.data.find_one({"$and":[{"amenity":"restaurant"},{"address": {"$exists": True}}]})

#Analysis of TIGER data-------------------------------------
tiger = db.data.find({"tiger:reviewed":"no"})
print tiger.count()


 
    
    