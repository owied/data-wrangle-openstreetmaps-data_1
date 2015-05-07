# -*- coding: utf-8 -*-
"""
@author: OlafWied
"""
import re
import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict
import codecs
import json


filename = "sample.osm" 
#filename = "san-diego-tijuana_mexico.osm" 

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]
            
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            
def check_street_names():
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(filename, events = ("start",)):
        if elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    pprint.pprint(dict(street_types))
    


check_street_names()
#I accepted abbreviations but I reduced them to one abbreviation per street type.
#The inspection of the street types led me to update the street types as follows:
mapping = {
            r"St.\b": "St",
            r"\bBl\b" : "Blvd",
            r"Blvd.\b" : "Blvd",
            r"Ave.\b":"Ave",
            r"Av\b" : "Ave",
            r"Rd.\b":"Rd",
            r"Py\b" : "Pkwy",
            r"Prky\b" : "Pkwy",
            r"Wy\b": "Way",
            r"street\b" : "Street"
            }
            
def update_name(name, mapping):
    for key in mapping:
        name = re.sub(key,mapping[key],name)
    return name
    
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

#Convert data into dict format and save as a JSON file
def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        
        node['created'] = {}
        la = None
        lo = None
        for at in element.attrib:
            if at == 'lat':
                la = float(element.attrib[at])
            elif at == 'lon':
                lo = float(element.attrib[at])
            elif at in CREATED:
                    node['created'][at] = element.attrib[at]
            else:
                node[at] = element.attrib[at]
        if la != None:
            node['pos'] = [la,lo]
        
        node['address'] = {}
        for tag in element.iter("tag"):
            k_split = tag.attrib['k'].split(":")
            if k_split[0] == 'addr':
                if len(k_split) > 2:
                    continue
                else: 
                    if k_split[1] == "street": #key == "addr:street"
                        node['address'][k_split[1]] = update_name(tag.attrib['v'],mapping) #if necessary update name according to 'mapping'
                    else: #different key (not a street name)
                        node['address'][k_split[1]] = tag.attrib['v']
            else:
                node[tag.attrib['k']] = tag.attrib['v']
        if node['address'] == {}:
            del node['address']
        if node['created'] == {}:
            del node['created']
        
        node['node_refs'] = []
        for nd in element.iter("nd"):
            node['node_refs'].append(nd.attrib['ref'])
        if node['node_refs'] == []:
            del node['node_refs']
            
        node['type'] = element.tag #this eventually overrides possible "type" tags
        return node
    else:
        return None


def process_map(file_in):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                fo.write(json.dumps(el) + "\n")
    return data
    

process_map(filename)
