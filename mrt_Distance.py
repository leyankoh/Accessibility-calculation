# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#Code to calculate great circle distance
#Calculates the distance (in miles) of a lat/long pair
#written in GIS Algorithms by Ningchuan Xiao
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

#testing code
if __name__ == "__main__":
    lat1, lon1 = 40, -83
    lat2, lon2 = 39.91, 116.56
    print spdist(lat1, lon1, lat2, lon2)

def convert(mi):
    meters = mi * 1609.344
    return meters 

#Read data
import pysal as ps
import numpy as np
import pandas as pd
import geopandas as gpd
from pysal.contrib.viz import mapping as maps

stop_dbf = ps.open("poly_Join.dbf", 'r')
train_dbf = ps.open("MRT_Attribute_Join.dbf", 'r')
centroids_dbf = ps.open("centroids.dbf", 'r')

stop_info = pd.DataFrame(stop_dbf[:,:]) #convert to dataframe
stop_info.columns = stop_dbf.header #add colnames

centroids_info = pd.DataFrame(centroids_dbf[:,:])
centroids_info.columns = centroids_dbf.header

train_info = pd.DataFrame(train_dbf[:,:])
train_info.columns = train_dbf.header

#Cleaning up unnecessary columns
#"CADASTRAL_" column will act as the "point ID" to relate distance to 
stop_info.drop(['timestamp', 'osm_id', 'type','INC_CRC', 'FMEL_UPD_D', 'X_ADDR', 'Y_ADDR', 'SHAPE_Leng', 'SHAPE_Area'], axis=1, inplace=True)
centroids_info.drop(['INC_CRC', 'FMEL_UPD_D', 'X_ADDR', 'Y_ADDR', 'SHAPE_Leng', 'SHAPE_Area', 'XCOORD', 'YCOORD'], axis=1, inplace=True)
train_info.drop(['Descriptio', 'INC_CRC', 'FMEL_UPD_D', 'X_ADDR', 'Y_ADDR', 'SHAPE_Leng', 'SHAPE_Area'], axis=1, inplace=True)

stop_info.to_csv("stop_geom.csv")
train_info.to_csv("train_geom.csv")
centroids_info.to_csv("centroid_geom.csv")

#sanity checking - does distance calc and conversion work?
lat1, lon1 = 1.31805, 103.89232 #Paya lebar station - falling in cadastral 1835
lat2, lon2 = 1.31743, 103.89577 #Centroid 1835
print convert(spdist(lat1, lon1, lat2, lon2)) #Output 389m! It works!

#Run from here 
stops = pd.read_csv("stop_geom.csv")
centroids = pd.read_csv("centroid_geom.csv")
train = pd.read_csv("train_geom.csv")

train.sort_values(by='OBJECTID', ascending=True, inplace=True)
centroids.sort_values(by='OBJECTID', ascending=True, inplace=True)
stops.sort_values(by='OBJECTID', ascending=True, inplace=True)

#Finding a loop to calculate the distances of train stops to matching centroids
train_merge = train.merge(centroids, on='OBJECTID')
#Cleaning up useless rows
train_merge.drop(['Unnamed: 0_x', 'Unnamed: 0_y', 'CADASTRAL__y'], axis=1, inplace=True)
#LON_x and LAT_x are coordinates of train stop
#LON_y and LAT_y are coordinates of centroid
#This does not work! It does not take into account other centroids (POIs) that a train stop might cover as well...
train_dist = []
for value in range(0,224):
    lat1, lon1 = train_merge['LAT_x'][value], train_merge['LON_x'][value]
    lat2, lon2 = train_merge['LAT_y'][value], train_merge['LON_y'][value]
    train_dist.append(convert(spdist(lat1, lon1, lat2, lon2)))
train_dist = pd.Series(train_dist)
train_merge['train_dist'] = train_dist.values
           
#Thus, load in a new SHP file that joins centroids that fall within the 
#buffer area of the MRT; then, calculate the distance of these centroids
#to their assigned MRT station
#There will be repeated centroid points for overlapping MRT Buffers 
MRT_dbf = ps.open("MRT_Centroid_Intersect_v2.dbf", 'r')
MRT_info = pd.DataFrame(MRT_dbf[:,:]) #convert to dataframe
MRT_info.columns = MRT_dbf.header
MRT_info.columns = ['OBJECTID', 'CADASTRAL_', 'LON_centroid', 'LAT_centroid', 'Name', 'Description', 'Wkday', 'Wkend', 'LON', 'LAT']

MRT_dist = []
for value in range(0, 829):
    lat1, lon1 = MRT_info['LAT_centroid'][value], MRT_info['LON_centroid'][value]
    lat2, lon2 = MRT_info['LAT'][value], MRT_info['LON'][value]
    MRT_dist.append(convert(spdist(lat1, lon1, lat2, lon2)))
MRT_dist = pd.Series(MRT_dist)
MRT_info['MRT_dist'] = MRT_dist.values
MRT_info.to_csv("MRT_centroid_join.csv")        
#In this CSV File, I will have:
#List of MRT stations that cover each POI
#And the distance of these MRT stations to the POI 