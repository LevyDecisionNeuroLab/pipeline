#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 12:26:07 2019
A script to create dictionary of scan sessions for feeding into fmriprep
Then convert DICOM to NIFTI.GZ, and organize files according to BIDS

@author: Or Duek, Ruonan Jia
"""

#%% import library
import os
import glob

#%% function. 
# It calls other functions. Should first load them in creatBIDS.py by Or
def fullBids(subNumber, sessionDict, output_dir):
    subName = 'sub-' + subNumber
  #  folder_name = ['anat','func','dwi','other']
    
    for i in sessionDict:
        session = i
        source_dir = sessionDict[i]
        print (session, source_dir)
        fullPath = os.path.join(output_dir, subName, session)
        print(fullPath)
        convert(source_dir,  output_dir, subName, session)
        organizeFiles(output_dir, subName, session)        
        
#%% grab all subject folders
folder = glob.glob('/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Multiband/subj*/*_levy')

#%% create a list of dictionary

# list of subject ID
sub_id = [] # each element is a subject id, the order is matched with session_dict
for sub_idx in range(len(folder)):
    sub_folder = folder[sub_idx].split('subj')
    subject = sub_folder[1].split('/')
    sub_id.append(subject[0])
# get unique elemets    
sub_id = list(set(sub_id))

# session dictionary
session_dict = [] # each element is a dictionary, for a single subject
for sub_idx in range(len(sub_id)): 
    session_count = 0
    subject_id = sub_id[sub_idx]
    session_dict_sub = {}
    for i in folder:        
        if i.find('subj%s/' %subject_id)!=-1:
            session_count = session_count + 1
            print(i)
            session_dict_sub.update({'ses-%s' % session_count: i})
    session_dict.append(session_dict_sub)

# check number of subject, and number of dictionary list
len(sub_id)
len(session_dict)
# check if sub_id and session_dict matched by subject id
subject_test = '1350'
session_dict[sub_id.index(subject_test)]
    
#%% for converting individual subject

# there are two subjects whose scan is under_harpaz-rotem, need to manually convert it
sessionDict = {
        'ses-2': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Multiband/subj1350/pb3231_harpaz-rotem'
        }
subNumber = '1350'

output_dir = '/media/Data/R_A_PTSD/data_bids_converted/' 

fullBids(subNumber, sessionDict, output_dir)

#%% convert
output_dir = '/media/Data/R_A_PTSD/data_bids_converted/' 

# exclude those already converted
exclude = ['3','1360','111','1309','1346','1063','1206','1326','1232','1344','1325','1300','1337','1305','1237','1347','1234']

# only convert these subjects
include = ['122', '008', '120', '100', '125']

for sub_idx in range(0, len(sub_id)):
    subject_id = sub_id[sub_idx]
    
    # if subject_id not in exclude:
    if subject_id in include:
        fullBids(subject_id, session_dict[sub_idx], output_dir)
        










