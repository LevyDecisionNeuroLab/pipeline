#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 16:02:52 2019

@author: Or Duek
Extracting KPE physio data from biopac using bioread package
https://github.com/uwmadison-chm/bioread
"""

import bioread
import os

# loading file
#a= bioread.read('/media/Drobo/Levy_Lab/Projects/PTSD_KPE/physio_data/raw/kpe1403/Scan_4/KPE1403.4_task_2018-09-12T12_41_45.acq')

# choose scripts channel
#b = a.named_channels["Script"].raw_data
#%%
# create loop that will look for changes between zero and back to zero as on and off set time points. 
def lookZero(b, offSet): # take Channel data and if we need to adjust timings
    time_onset = []
    time_offset = []
# this function takes a raw data from bioread channel and return two arrays of on and off sets.
    look_for_zero = b[0] != 0
    for i, v in enumerate(b[1:]):
        if look_for_zero and v == 0:
            look_for_zero = False
            time_offset.append(i/1000 - offSet)
        elif not look_for_zero and v != 0:
            look_for_zero = True
            time_onset.append(i/1000 - offSet)
    return (time_onset, time_offset)
        
#%% Other option - exporting to matlab        
from bioread.writers import matlabwriter
matlabwriter.MatlabWriter.write_file(a, "myfile.mat")


#%% Function to extract actual data from subjects
def kpeTaskDat(filename):
    # takes filename and returns data frame of onsets and duration. Needs to attach condition and subject number
    import pandas as pd
    import bioread
    a = bioread.read(filename)
   ## Take the first ready screen
    readyScreen = a.named_channels["Ready Screen"].raw_data
    readyOn = lookZero(readyScreen,0)[0]     
    # set difference between first appereance and TRs. 
    # Setting to first Ready screen at 6 seconds
    diff = readyOn[0] - 6
    # Choose Script channel by its name
    b = a.named_channels["Script"].raw_data
    scriptTime = lookZero(b, diff)
    duration = []
 
    for i in range(len(scriptTime[0])): # run through the set
        duration.append(round(scriptTime[1][i] - scriptTime[0][i])) # create duration
    events= pd.DataFrame({'onset':scriptTime[0], 'duration':duration})
    
    return events


#%% This part takes the scan sheet and create a data frame with condition and sessions. 
totalScanData = pd.read_excel('/media/Drobo/Levy_Lab/Projects/PTSD_KPE/kpe_scan_table.xls', sheet_name = 'kpe_scan_table')        
# short loop to fill in subject numebrs and sessions
totalScanData["subject_id"] = totalScanData["subject_id"].fillna('noSub') # filling all NaNs with noSub. 
# create a session column
   
for index,rows  in totalScanData.iterrows():
    print(index)
    print (rows.subject_id)
    if rows.subject_id != 'noSub':
        subject = rows.subject_id
 
    else:
        totalScanData["subject_id"][index] = subject
 
trialOrder = pd.DataFrame({'subject_id': totalScanData["subject_id"], "scriptOrder":totalScanData["Script Order"], "session":totalScanData["scan_num"]})
 # read subject id and pick the right line from the data frame



subjectId = "kpe" + str(subNum)
subjectData = trialOrder[trialOrder.subject_id==subjectId]
# rnu through all session of subject and create conditions with onset and duration. 
for s , r in subjectData.iterrows(): # s is index and r is the actual row
    print(s)
    breakTrial = subjectData["scriptOrder"][s].split() # now its the first line but should be with subject id accordinaly. 
    for n in breakTrial:
        print (n)
        if 'Sad' in n:
            condition.append('sad')
        elif 'Relax' in n:
            condition.append('relax')
        elif 'Trauma' in n:
            condition.append('trauma')
        else:
            pass
    
    events= pd.DataFrame({'onset':scriptTime[0], 'duration':duration, 'condition':condition})
    # now we should create a data frame
    
    
               
    return (events)
            
#%% Get all acq files
import glob
# get all scripts acq files
fileList = glob.glob('/media/Drobo/Levy_Lab/Projects/PTSD_KPE/physio_data/raw/kpe*/**/*scripts*.acq')
# remove faulty script file PLEASE MAKE SURE THE LOCATION WAS NOT CHANGED
del fileList[16]

def getSubjectNum(filePath):
    # simple function to get subject number from data
    a = filePath.split('/kpe')
    b = a[1].split('/')
    subjectNum = b[0]
    return subjectNum

def getScanNum(filePath):
    # simple function to get scan number from file name
    a= filePath.split('can_')
    b = a[1].split('/')
    scanNum = b[0]
    return int(scanNum)

#%%
# now create a loop through all files
import numpy as np
events = []   
totalEvents = [] #np.array([])
# get subject number + name
for file in fileList:
    print(file)
    subNum = getSubjectNum(file)
    subjectId = "kpe" + str(subNum)
    scanNum = getScanNum(file)
    subjectData = trialOrder[trialOrder.subject_id==subjectId][trialOrder.session == scanNum] #, trialOrder.session==scanNum]
   # sessionData = subjectData[subjectData.session == scanNum]
    # rnu through all session of subject and create conditions with onset and duration. 
    condition = []
    for s , r in subjectData.iterrows(): # s is index and r is the actual row
        print(s)
        breakTrial = subjectData["scriptOrder"][s].split(';') # now its the first line but should be with subject id accordinaly.  Removed the comments
        breakTrial2 = breakTrial[0].split()         
        
        for n in breakTrial2:
            print (n)
            if 'Sad' in n:
                condition.append('sad')
            elif 'Relax' in n:
                condition.append('relax')
            elif 'Relaxing' in n:
                condition.append('relax')
            elif 'Trauma' in n:
                condition.append('trauma')
            else:
                pass
    events = kpeTaskDat(file)
    events["condition"] = condition
    events["session"] = scanNum
    events["subject"] = subNum
    totalEvents.insert(int(subNum), events)
   # totalEvents = np.append(totalEvents, events)
type(totalEvents)
totalEvents[8]


















