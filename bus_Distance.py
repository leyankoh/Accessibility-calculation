# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 16:37:25 2017

@author: Le Yan
"""
#Access files from C:\Users\Le Yan\Dropbox\Dissertation\Data\Data for Calculating Distance
#Function to calculate coordinate distance
import math 
def spdist(lat1, lon1, lat2, lon2):
    D = 3959
    phi1 = math.radians(lat1)
    lambda1 = math.radians(lon1)
    phi2 = math.radians(lat2)
    lambda2 = math.radians(lon2)
    dlambda = lambda2 - lambda1
    dphi = phi2 - phi1
    sinlat = math.sin(dphi/2.0)
    sinlong = math.sin(dlambda/2.0)
    alpha = (sinlat * sinlat) + math.cos(phi1) * \
        math.cos(phi2) * (sinlong * sinlong)
    c = 2 * math.asin(min(1, math.sqrt(alpha)))
    d = D * c
    return d 

#Function to convert distance from miles to meters
def convert(mi):
    meters = mi * 1609.344
    return meters 

import pysal as ps
import numpy as np
import pandas as pd
import geopandas as gpd
from pysal.contrib.viz import mapping as maps #Maybe I don't need this

#load in important files
centroids = pd.read_csv("centroid_geom.csv")
bus_dbf = ps.open("Bus_Centroid_Intersect.dbf", 'r')
bus_info = pd.DataFrame(bus_dbf[:,:])
bus_info.columns = bus_dbf.header
#Rename columns to make it less confusing
bus_info.columns = ['OBJECTID', 'CADASTRAL_', 'LON_centroid', 'LAT_centroid', 'Name', 'LON', 'LAT']
#Check length
print len(bus_info)

#Let's get down to business - calculating all distances.
#this is the same code used to calculate MRT distances. Now we have both. 
bus_dist = []
for value in range(0, 4620):
    lat1, lon1 = bus_info['LAT_centroid'][value], bus_info['LON_centroid'][value]
    lat2, lon2 = bus_info['LAT'][value], bus_info['LON'][value]
    bus_dist.append(convert(spdist(lat1, lon1, lat2, lon2)))
bus_dist = pd.Series(bus_dist)
bus_info['bus_dist'] = bus_dist.values
bus_info.to_csv("bus_centroid_join.csv") 


##########Redo Distance Calculation for bus stop info from API instead of OSM#######
bus2_dbf = ps.open("Bus_Centroid_Intersect_API.dbf", 'r')
bus2_info = pd.DataFrame(bus2_dbf[:,:])
bus2_info.columns = bus2_dbf.header
print len(bus2_info) #always check the length

bus_dist = []
for value in range(0, 4528):
    lat1, lon1 = bus2_info['LAT'][value], bus2_info['LON'][value]
    lat2, lon2 = bus2_info['Latitude'][value], bus2_info['Longitude'][value]
    bus_dist.append(convert(spdist(lat1, lon1, lat2, lon2)))
bus_dist = pd.Series(bus_dist)
bus2_info['bus_dist'] = bus_dist.values
bus2_info.to_csv("bus_API_centroid_join.csv")