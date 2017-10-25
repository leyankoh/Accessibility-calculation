# -*- coding: utf-8 -*-
"""
Created on Wed Mar 01 18:16:12 2017

@author: Le Yan
"""

import numpy as np 
import pandas as pd

def weight(df1, objID):
    df = df1.loc[df1["OBJECTID"] == objID]
    df["weight"] = np.nan
    df.sort_values(by="edf", ascending=False, inplace=True)
    df.reset_index(inplace=True) #gotta reset index or else
    df.drop(["index"], axis=1, inplace=True)
    df.set_value(0, 'weight', '1')
    df.ix[1:, 'weight'] = 0.5 
    return df


mrt = pd.read_csv("MRT_PTAL_raw.csv", header=0)
mrt.drop(["Unnamed: 0", "Wkday", "Wkend", "MRT_dist", "freq", "walk_time", "swt", "awt", "tat", "aimode"], axis=1, inplace=True)

mrt_predt = mrt #recreate dataframe 

to_del = mrt_predt[mrt_predt['Description'].isin(['Thomson-EC Line', 'Downtown Line'])].index.tolist()
nsl_del = mrt_predt[mrt_predt['Name'].isin(['Canberra (U/C)', 'Keppel', 'Cantonment', 'Prince Edward', 'Gul Circle', 'Tuas Cresent', 'Tuas West', 'Tuas Link'])].index.tolist()
mrt_predt = mrt_predt.drop(to_del)
mrt_predt = mrt_predt.drop(nsl_del)

mrt_predt.to_csv("MRT_PTAL_PreDT.csv")

mrt_predt.drop(["weight", "ai"], axis=1, inplace=True) #We will have to recalculate these values

objList = mrt_predt["OBJECTID"].tolist()
objList = set(objList)

#recalculate weight
mrt_predt_ptal = pd.DataFrame([])

for value in objList:
    dataFrame = weight(mrt_predt, value)
    mrt_predt_ptal = mrt_predt_ptal.append(dataFrame, ignore_index=True)
    
    
#get modal AI
mrt_predt_ptal['ai'] = mrt_predt_ptal['edf'] * mrt_predt_ptal['weight']
mrt_predt_ptal['aimode'] = mrt_predt_ptal['ai'].groupby(mrt_predt_ptal['OBJECTID']).transform('sum')

#get dataframe of just AImode
aimode = mrt_predt_ptal['ai'].groupby(mrt_predt_ptal['OBJECTID']).sum()
aimode = pd.DataFrame(aimode)
aimode.reset_index(inplace=True)
aimode.columns = ["OBJECTID", "ai_mrt_predt"]

aimode.to_csv("mrt_predt_aimode.csv")


aitotal = pd.read_csv("final_index_reviewed.csv", header=0)
aitotal.drop(["Unnamed: 0", "ai_mrt_predt", "categories_predt", "ai_poi_predt_new", "ai_poi_predt", "categories_predt_new"], axis=1, inplace=True)

#merge frames
aitotal = pd.merge(aitotal, aimode, on='OBJECTID', how='outer')
aitotal = aitotal.fillna(0)


#get ai for POI(object ID)
aitotal["ai_poi_predt"] = aitotal["ai_new"] + aitotal["ai_mrt_predt"]

#Bin data
bins = [-1, 0, 2.5, 5, 10, 15, 20, 25, 40, 200]
bands = ["No Access", "1a", "1b", "2", "3", "4", "5", "6a", "6b"]

#bin data
categories = pd.cut(aitotal['ai_poi_predt'], bins, labels=bands)
aitotal['categories_predt'] = pd.cut(aitotal['ai_poi_predt'], bins, labels=bands)

aitotal.to_csv("final_index_predt.csv")
aitotal.to_csv("final_index_reviewed.csv")
