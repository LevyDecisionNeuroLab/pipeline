# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 12:36:44 2018

@author: or

Two methods. 
lookSeriesNum will take a filename (json) and look for the SeiesNumber within.
addSeriesNum will run through a folder, look for json files and add the SeriesNumber to the nii.gz file name. 
It should help reorganizing files in time order, when filenames are on same condition (i.e. bold)
"""

import json
import os



def lookSeriesNum(fileName):
    # this function takes filename and return series number (from json file)
    with open(fileName) as f:
        data = json.load(f)
    return data["SeriesNumber"]



directory = '/home/or/Documents/dicom_niix/sub76/raw/bold'
def addSeriesNum(directory): 
    # this function takes folder in which we have many bold files and add series number (the lower number means first)
    for files in os.listdir(directory):
        os.chdir(directory)
        if 'json'in files:
            # get Series Number and keep it
            #print(os.path.splitext(files)[0])
            shouldChange = os.path.splitext(files)[0] # getting the filename without extension. 
            serial = lookSeriesNum(files)
            os.rename(shouldChange + '.nii.gz', shouldChange + str(serial) + '.nii.gz')
        else:
           continue