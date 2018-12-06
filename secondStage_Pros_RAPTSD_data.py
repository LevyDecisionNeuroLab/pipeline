#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 15:43:14 2018

@author: or
Small script that separates resting state from bold in R&A_PTSD study and add sequence to all bold scans
"""

# run though folders and scanfor "rest" in filename
# for each  - create a new rest folder and move files there.
# run though all bold folders and add sequence using jsonMethods.py

import os
import json

def lookSeriesNum(fileName):
    # this function takes filename and return series number (from json file)
    with open(fileName) as f:
        data = json.load(f)
    return data["SeriesNumber"]

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
       

masterFolder= '/run/user/1000/gvfs/smb-share:server=172.21.64.199,share=levy_lab/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Multiband/Converted'  # define basic fodler

dir_list = next(os.walk(masterFolder))[1] #creates a list of all folders in masterFolder

for sub in dir_list:
    # go through folders, look for "rest" create a folder 
    subdir_list = next(os.walk(os.path.join(masterFolder, sub)))[1] #
    for scans in subdir_list:
         
        # move to bold folder - look for "rest" and move it to new rest folder outside bold
        fileList = [] # create empty list for now
        for root, dirs, files in os.walk(os.path.join(masterFolder,sub,scans)):
            for file in files:
                fileList.append(file) # 
            
        for l in fileList:
            if l.find('rest')!=-1: # if the filename contains this specific condition
                # move file to new folder
                print(l)
                os.makedirs(os.path.join(masterFolder, sub, scans,'rest'), exist_ok = True)
                try:
                    os.rename(os.path.join(masterFolder, sub, scans, 'bold',l), os.path.join(masterFolder, sub, scans,'rest',l))
                except:
                    print("File: " + l + " Was already transferred to rest folder")    
              # print('old file + location: ' + os.path.join(masterFolder, sub, scans, 'bold',l)+ 'New file location: ' + os.path.join(masterFolder, sub, scans,'rest',l))
            else:
                continue
        
        addSeriesNum(os.path.join(masterFolder, sub, scans, 'bold')) # add series number to bold files.
