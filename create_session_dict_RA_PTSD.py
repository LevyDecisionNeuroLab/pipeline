#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 12:26:07 2019
A script to create dictionary of scan sessions for feeding into fmriprep
Then convert DICOM to NIFTI.GZ, and organize files according to BIDS

@author: Or Duek, (Ruonan Jia modified)
"""

#%% import library
import os
import glob

#%% function. 
# It calls other functions. Should first load them in creatBIDS.py by Or
#from creatBIDS import convert, checkGz, checkTask

def organizeFiles(output_dir, subName, session):
    
    fullPath = os.path.join(output_dir, subName, session)
    os.makedirs(fullPath + '/dwi')
    os.makedirs(fullPath + '/anat')    
    os.makedirs(fullPath + '/func')
    os.makedirs(fullPath + '/misc')    
    
    a = next(os.walk(fullPath)) # list the subfolders under subject name

    # run through the possibilities and match directory with scan number (day)
    for n in a[2]:
        print (n)
        b = os.path.splitext(n)
        # add method to find (MB**) in filename and scrape it
        if n.find('diff')!=-1:
            print ('This file is DWI')
            shutil.move((fullPath +'/' + n), fullPath + '/dwi/' + n)
            os.rename((os.path.join(fullPath, 'dwi' ,n)), (fullPath + '/' + 'dwi' +'/' + subName + '_' + session +'_dwi' + checkGz(b)))
   
        elif n.find('MPRAGE')!=-1:
            print (n + ' Is Anat')
            shutil.move((fullPath + '/' + n), (fullPath + '/anat/' + n))
            os.rename(os.path.join(fullPath,'anat' , n), (fullPath + '/anat/' + subName+ '_' + session + '_acq-mprage_T1w' + checkGz(b)))
        elif n.find('t1_flash')!=-1:
            print (n + ' Is Anat')
            shutil.move((fullPath + '/' + n), (fullPath + '/anat/' + n))
            os.rename(os.path.join(fullPath,'anat' , n), (fullPath + '/anat/' + subName+ '_' + session + '_acq-flash_T1w' + checkGz(b)))
        elif n.find('t1_fl2d')!=-1:
            print (n + ' Is Anat')
            shutil.move((fullPath + '/' + n), (fullPath + '/anat/' + n))
            os.rename(os.path.join(fullPath,'anat' , n), (fullPath + '/anat/' + subName+ '_' + session + '_acq-fl2d1_T1w' + checkGz(b))) 
        elif n.find('GRE_3D_Sag_Spoiled')!=-1:
            print (n + ' Is Anat')
            shutil.move((fullPath + '/' + n), (fullPath + '/anat/' + n))
            os.rename(os.path.join(fullPath,'anat' , n), (fullPath + '/anat/' + subName+ '_' + session + '_acq-gre_spoiled_T1w' + checkGz(b)))             
        elif n.find('bold')!=-1:
            print(n  + ' Is functional')
            taskName = checkTask(n)
            shutil.move((fullPath + '/' + n), (fullPath + '/func/' + n))
            os.rename(os.path.join(fullPath, 'func', n), (fullPath  + '/func/' +subName+'_' +session + '_task-' + taskName + '_bold' + checkGz(b)))
        else:
            print (n + 'Is MISC')
            shutil.move((fullPath + '/' + n), (fullPath + '/misc/' + n))
           # os.rename(os.path.join(fullPath, 'misc', n), (fullPath +'/misc/' +'sub-'+subName+'_ses-' +sessionNum + '_MISC' + checkGz(b)))

#%%    
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
sub_reordered = [] # subject id that reordered session number
sub_one_ses = [] # subject id who only had one session of data
sub_three_ses = [] # subject id who had three sessions of data

for sub_idx in range(len(sub_id)): 
    session_count = 0
    subject_id = sub_id[sub_idx]
    sessions_sub = {}
    for i in folder:        
        if i.find('subj%s/' %subject_id)!=-1:
            session_count = session_count + 1
            print(i)
            sessions_sub.update({session_count: i})                

    # get all study numbers
    study_nums ={}
    for ses_key in sessions_sub.keys():
        study_num = int(sessions_sub[ses_key].split('subj%s/' %subject_id)[1].split('_levy')[0][2:])
        study_nums.update({ses_key: study_num})
        
    # compare study nnumber levy_####, and determine session order
    sessions_re_sub = {} 
    if len(study_nums) == 2:
        if study_nums[1] > study_nums[2]:
            sessions_re_sub.update({'ses-1': sessions_sub[2]})
            sessions_re_sub.update({'ses-2': sessions_sub[1]})
            sub_reordered.append(subject_id)
        else:
            sessions_re_sub.update({'ses-1': sessions_sub[1]})
            sessions_re_sub.update({'ses-2': sessions_sub[2]})            
    else:
        session_re_sub = sessions_sub
        if len(study_nums) == 1:
            sub_one_ses.append(subject_id)
        elif len(study_nums) == 3:
            sub_three_ses.append(subject_id)
        
    session_dict.append(sessions_re_sub)
    
    # reorder session id
    

## check number of subject, and number of dictionary list
#len(sub_id)
#len(session_dict)
## check if sub_id and session_dict matched by subject id
#subject_test = '1350'
#session_dict[sub_id.index(subject_test)]
session_dict[sub_id.index('53')]

#%% pre MB participants
folder = glob.glob('/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Pre-MB/BV_preprocessed_data/subj*/*_S*/')

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
    sessions_sub = {}
    for i in folder:        
        if i.find('subj%s/' %subject_id)!=-1:
            print(i)
            if i.find('S1/') != -1:
                sessions_sub.update({'ses-1': i})
            elif i.find('S2/') != -1:
                sessions_sub.update({'ses-2': i})
                
    session_dict.append(sessions_sub)        
              
# Pre MB
session_dict = [{
  'ses-1': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Pre-MB/BV_preprocessed_data/subj77/77_S1/'},
 {'ses-2': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Pre-MB/BV_preprocessed_data/subj79/79_S2/',
  'ses-1': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Pre-MB/BV_preprocessed_data/subj79/79_S1/'},
 {'ses-2': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Pre-MB/BV_preprocessed_data/subj80/80_S2/',
  'ses-1': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Pre-MB/BV_preprocessed_data/subj80/80_S1/'},
 {'ses-2': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Pre-MB/BV_preprocessed_data/subj81/81_S2/',
  'ses-1': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Pre-MB/BV_preprocessed_data/subj81/81_S1/'},
 {'ses-2': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Pre-MB/BV_preprocessed_data/subj78/78_S2/',
  'ses-1': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Pre-MB/BV_preprocessed_data/subj78/78_S1/'},
 {'ses-1': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Pre-MB/BV_preprocessed_data/subj76/76_S1/',
  'ses-2': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Pre-MB/BV_preprocessed_data/subj76/76_S2/'}]

#%% for converting individual subject

sessionDict = {
        'ses-1': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Multiband/subj3/ta8967_levy'
        }

sessionDict = {
        'ses-2': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Multiband/subj3/ta8996_levy'
        }

subNumber = '3'

# there are two subjects whose scan is under_harpaz-rotem, need to manually convert it
sessionDict = {
        'ses-2': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Multiband/subj1350/pb3231_harpaz-rotem'
        }
subNumber = '1350'

sessionDict = {
        'ses-1': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Multiband/subj1328/pb2359_harpaz-rotem'
        }
subNumber = '1328'

# subject folder name not as _levy
subNumber = '53'
sessionDict = {
        'ses-1': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Multiband/subj53/ta9973_levy_DAY1',
        'ses-2': '/media/Drobo/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Multiband/subj53/ta0008_levy_DAY2'
        }


output_dir = '/media/Data/R_A_PTSD/data_bids/' 

fullBids(subNumber, sessionDict, output_dir)

#%% convert
output_dir = '/media/Data/R_A_PTSD/data_bids/' 

# exclude those already converted
#exclude = ['3','1360','111','1309','1346','1063','1206','1326','1232','1344','1325','1300','1337','1305','1237','1347','1234']
exclude = ['3']

# only convert these subjects
#include = ['122', '008', '120', '100', '125']
include = ['92', '125', '1354', '1347', '119', '110', '8', '1284', '1210', '88', '1208', '95', '1285', '1268', '1235', '1234', '1266',
           '58', '1350', '117', '82', '1300', '1344', '1005', '93', '1232', '1346', '43', '99', '56', '1278', '50', '1360', '1273',
           '108', '109', '1290', '105', '1305', '1216', '104', '1218', '1220', '100', '1269', '61', '1280', '1338', '1340', '1309', 
           '60', '1001_test', '1002_test', '1074', '38', '85', '1291', '1326', '102', '1250', '1272', '1316', '1072', '96', '115', 
           '1304', '1237']

include = sub_id

for sub_idx in range(0, len(sub_id)):
    subject_id = sub_id[sub_idx]
    
#    if subject_id not in exclude:
    if subject_id in include:
        fullBids(subject_id, session_dict[sub_idx], output_dir)
        










