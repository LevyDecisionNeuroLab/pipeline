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
    # this function takes folder in which we have many bold files, get rid of the unnecessary file suffix, and add series number (the lower number means first)
    for files in os.listdir(directory):
        os.chdir(directory)
        if 'json'in files:
            # get Series Number and keep it           
            serial = lookSeriesNum(files)
            
            # change file name
            shouldChange = os.path.splitext(files)[0] # getting the filename without extension.
            shouldChange_simp = shouldChange.split('(')[0] # get rid of  '(MB4iPAT2)_bold'
            os.rename(shouldChange + '.nii.gz', shouldChange_simp + str(serial) + '.nii.gz')
            os.rename(shouldChange + '.json', shouldChange_simp + str(serial) + '.json')           
        else:
           continue

#%% Loop through all subjects

# root directory, contains all subject folders
root_dir  = 'Y:/R_A_PTSD/data_bids_converted'
# root_dir  = 'Y:/R_A_PTSD/test'
# type of brain imaging data to change, based on the folder name
type2change = ['func']


# subject loop
for sub_dir in os.listdir(root_dir):
    # session loop
    for ses_dir in os.listdir(os.path.join(root_dir,sub_dir)):
        # type of data loop (anatomical/functional/dti, etc.)
        for type_dir in type2change:
            
            dir2change = os.path.join(root_dir, sub_dir, ses_dir, type_dir)
            
            # change file name
            addSeriesNum(dir2change)           
            print(dir2change, 'Changed')


#%% change single session for one subject
directory = 'Y:/R_A_PTSD/data_bids_converted/sub-3/ses-2/func - Copy'
addSeriesNum(directory)
        
#%% Testing code
directory = 'Y:/R_A_PTSD/data_bids_converted/sub-3/ses-2/func - Copy'
os.chdir(directory)
filename_test = 'sub-3_ses-2_task-(MB4iPAT2)_bold.json'

shouldChange = filename_test.split('-(')[0]

serial = lookSeriesNum(filename_test)



