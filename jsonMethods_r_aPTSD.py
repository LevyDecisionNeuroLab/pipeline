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


#%%
def lookSeriesNum(fileName):
    # this function takes filename and return series number (from json file)
    with open(fileName) as f:
        data = json.load(f)
    return data["SeriesNumber"]


#%%
def addSeriesNum(directory): 
    # this function takes folder in which we have many bold files, get rid of the unecessary file suffix, and add series number (the lower number means first)
    for files in os.listdir(directory):
        os.chdir(directory)
        if 'json'in files:
            # get Series Number and keep it           
            serial = lookSeriesNum(files)
            
            # change file name
            shouldChange = os.path.splitext(files)[0] # getting the filename without extension.
            shouldChange_simp = shouldChange.split('-(')[0] # get rid od  '-(MB4iPAT2)_bold'
            os.rename(shouldChange + '.nii.gz', shouldChange_simp + str(serial) + '.nii.gz')
            os.rename(shouldChange + '.json', shouldChange_simp + str(serial) + '.json')           
        else:
           continue

#%%




directory = 'Y:/R_A_PTSD/data_bids_converted/sub-3/ses-2/func - Copy'
addSeriesNum(directory)
        
#%% Testing code
directory = 'Y:/R_A_PTSD/data_bids_converted/sub-3/ses-2/func - Copy'
os.chdir(directory)
filename_test = 'sub-3_ses-2_task-(MB4iPAT2)_bold.json'

shouldChange = filename_test.split('-(')[0]

serial = lookSeriesNum(filename_test)



