#Python 2.7.9  28 December 2016

import requests
import json
import urllib
from urlparse import urlparse
import httplib2 as http
import numpy as np
import pandas as pd

######retrieving data######
#Authentication perimeters
headers = {
    'AccountKey':'*',
    'UniqueUserID' :'*',
    'accept':'application/json'
    }


#Define a function to repeat API calls from different URLs source: http://www.lihaoyi.com/post/PlanningBusTripswithPythonSingaporesSmartNationAPIs.html#exploring-the-lta-data-mall

def fetch_all(url):
    results = []
    while True:
        new_results = requests.get(
            url,
            headers=headers,
            params={'$skip': len(results)}
        ).json()['value']
        if new_results == []:
            break
        else:
            results += new_results
    return results

#Importing json data. No longer required if you already have json files in working directory. ***Do run if json not found
if __name__=="__main__":
    services = fetch_all("http://datamall2.mytransport.sg/ltaodataservice/BusServices")
    print len(services) #checking number of data points
    stops = fetch_all("http://datamall2.mytransport.sg/ltaodataservice/BusStops")
    print len(stops)
    routes = fetch_all("http://datamall2.mytransport.sg/ltaodataservice/BusRoutes")
    print len(routes)

#Dumping data so that I don't have to reload them. Dated 28/12/2016
with open("routes.json", "w") as f:
    f.write(json.dumps(routes))
with open("stops.json", "w") as f:
    f.write(json.dumps(stops))
with open("services.json", "w") as f:
    f.write(json.dumps(services))
#call data with json.loads(open("___.json").read())

#######Loading and Manipulating data#########
services = json.loads(open("services.json").read())
stops = json.loads(open("stops.json").read())
routes = json.loads(open("routes.json").read())

#mapping code/description for easier access later on...
stop_desc_map = {stop["Description"]: stop for stop in stops}
stop_code_map = {stop["BusStopCode"]: stop for stop in stops} #More elegant method of turning json library into a dict

#Create CSV for easier usage
stops_Df = pd.DataFrame(stops)
stops_Df.to_csv("StopsData.csv")

services_Df = pd.DataFrame(services)
services_Df.to_csv("ServicesData.csv")

routes_Df = pd.DataFrame(routes)
routes_Df.to_csv("RoutesData.csv")

#Looking at data that we only need
trunkServices = services_Df.loc[services_Df["Category"] == "TRUNK"]
stops_Df = stops_Df.drop(stops_Df.index[5036:]) #Get rid of non-stops in stops_Df

#Testing looking at buses that stop at a particular Bus Stop by Bus Stop Code
testing = routes_Df.loc[routes_Df["BusStopCode"] == "01231"] #Sample bus stop code
testing = testing.drop_duplicates(subset="ServiceNo", keep="last")
print len(testing.index) #Check number of buses from this stop. Seems alright, although it adds the express buses serving the same route as well...

#Time to do the same for all bus stops, iterating through them...

def rCount(code): #rmb to enter code as str, else it will return octal numbers e.g. rCount("01012")
    #code = str(code)
    code = code.zfill(5)
    routeCount = routes_Df.loc[routes_Df["BusStopCode"] == code]
    routeCount = routeCount.drop_duplicates(subset="ServiceNo", keep="last")
    return len(routeCount.index)


#Trying to iterate over bus stop codes...
routeList = routes_Df["BusStopCode"].tolist()
newrouteList = []
for value in routeList:
    value = str(value)
    value = value.zfill(5)
    newrouteList.append(rCount(value))

newrouteList = pd.Series(newrouteList)
routes_Df["routeNo"] = newrouteList.values
routesDf_Clean = routes_Df.drop_duplicates(subset="BusStopCode", keep="last")
#Save again so I don't have to iterate over 24k worth of data points!!
routesDf_Clean.to_csv("RouteDataNew.csv")

#Read CSV to file when I need to open
routesStop = pd.read_csv("RouteDataNew.csv", header=0)
#Let's clean it up a bit
routesStop.drop(routesStop.columns[[0, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12]], axis=1, inplace=True)
#Save it to a cleaner CSV
routesStop.to_csv("RouteDataClean.csv")

"""
for a in stops_Df["BusStopCode"]:
    routeCount = routes_Df.loc[routes_Df["BusStopCode"] == a]
    routeCount = routeCount.drop_duplicates(subset="ServiceNo", keep="last")
    routeCount["routeNo"] = len(routeCount.index)
    routeCount.drop_duplicates(subset="BusStopCode", keep="last")
    if routeCount["BusStopCode"] == stops_Df["BusStopCode"]:
        stops_Df["routeNo"] = len(routeCount.index)
"""
