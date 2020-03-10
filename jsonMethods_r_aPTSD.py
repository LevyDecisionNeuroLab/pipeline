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
            # get rid of  '(MB4iPAT2)'
            if 'rest' in shouldChange:
                continue
            else:
                shouldChange_simp = shouldChange.split('task-')[0]
                os.rename(shouldChange + '.nii.gz', shouldChange_simp + 'task-' + str(serial) + '_bold.nii.gz')
                os.rename(shouldChange + '.json', shouldChange_simp + 'task-' + str(serial) + '_bold.json')           
        else:
           continue


#%% Loop through all subjects

# root directory, contains all subject folders
root_dir  = '/media/Data/R_A_PTSD/data_bids'
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
directory = '/media/Data/R_A_PTSD/data_bids/sub-3/ses-2 - Copy/func/'
addSeriesNum(directory)

#%% check where the resting state scan 
sub_id = 38
ses_id = 2
folder = '/media/Data/R_A_PTSD/data_bids/sub-' + str(sub_id) + '/ses-' + str(ses_id) + '/func/'
os.listdir(folder)

#%%test

files = os.listdir(directory)[1]
files
shouldChange = os.path.splitext(files)[0]
shouldChange
shouldChange_simp = shouldChange.split('task-')[0]
shouldChange_simp


#%% rename based on absolute order of task. NEEDS TO BE CHANGED 
data_root = '/home/rj299/project/mdm_analysis/data_rename'
#%%
# functions for changing file names

# rename all files by adding run number determined by session and task number during scanning
def addRunNum(directory): 
    """ Add scan run numbers to file name
    
    Parameters
    --------------
    directory: directory for a subject, contains data for all runs
    
    """
    
    os.chdir(directory)
    
    # get sorted task number from the directory
    task_num_all = getTaskNum(directory)
    
    # add run number and rename
    for filename in os.listdir(directory):
        # get task number
        task_num = int(filename.split('_task-task')[1].split('_')[0])
        
        # get the run number based on all the task number in the directory
        run_count = task_num_all.index(task_num) + 1

        
        filename_new = filename.split('_task-task%s' %task_num)[0] + '_task-%s' %run_count + filename.split('_task-task%s' %task_num)[1]

        os.rename(filename, filename_new)  
        print(filename_new)

# get all task numbers for ses one
def getTaskNum(directory):
    """ Get all the task number for a session
     
    Parameters
    -----------------
    directory: data directory for a subject
    
    Return
    -----------------
    task_num: sorted task number for each session
    """
    file_ses = glob.glob('sub-*_ses-1_task*_bold.nii.gz')
    
    task_num = []
    
    for file in file_ses:
        task_id = file.split('_task-task')[1].split('_space')[0]
        task_num.append(int(task_id))
    
    task_num.sort()
    
    return task_num

#%% NEEDS to be run only once
    
# rename files and add run number in the file name
# needs running only ONCE
sub_fold = ['/home/rj299/project/mdm_analysis/data_rename/sub-2654',
            '/home/rj299/project/mdm_analysis/data_rename/sub-2658']

for fold in sub_fold:
    if fold != '/home/rj299/project/mdm_analysis/data_rename/sub-2582':
        fold_func = os.path.join(fold, 'ses-1', 'func')
        addRunNum(fold_func)    

#%% subject 2582 only
# rename files and add run number in the file name
# subject 2582 only, because the files are named in a different way
# rename all files by adding run number determined by session and task number during scanning

# run ONLY ONCE

def addRunNum_2582(directory): 
     """ Add scan run numbers to file name
    
     Parameters
     --------------
     directory: directory for a subject, contains data for all runs
    
     """
     os.chdir(directory)
    
     # get sorted task number from the directory
     task_num_all = getTaskNum_2582(directory)
    
     # add run number and rename
     for filename in os.listdir(directory):
         # get task number
         task_num = int(filename.split('_task-')[1].split('_')[0])
        
         # get the run number based on all the task number in the directory
         run_count = task_num_all.index(task_num) + 1

        
         filename_new = filename.split('_task-%s' %task_num)[0] + '_task-task-%s' %run_count + filename.split('_task-%s' %task_num)[1]

         os.rename(filename, filename_new)  
         print(filename_new)

 # get all task numbers for ses one
def getTaskNum_2582(directory):
     """ Get all the task number for a session
    
     Parameters
     -----------------
     directory: data directory for a subject
    
     Return
     -----------------
     task_num: sorted task number for each session
     """
     
     os.chdir(directory)
     
     file_ses = glob.glob('sub-*_ses-1_task*_bold.nii.gz')
    
     task_num = []
    
     for file in file_ses:
         task_id = file.split('_task-')[1].split('_space')[0]
         task_num.append(int(task_id))
    
     task_num.sort()
    
     return task_num

#%%
# subject 2582 has a weird way of naming files, need to run these two steps sequentially
# step 1, add run number, by adding an extra stirng of 'task' to prevent renaming wrong files
addRunNum_2582(os.path.join(data_root, 'sub-2582','ses-1','func')) 
# step 2, get rid of 'task' 
addRunNum(os.path.join(data_root, 'sub-2582','ses-1','func'))
#%%
task_num_temp = getTaskNum_2582(os.path.join(data_root, 'sub-2582','ses-1','func')) 
