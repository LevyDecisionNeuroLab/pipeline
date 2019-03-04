#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 15:02:13 2019

@author: Or Duek
A short script that will convert to NIFTI.GZ (from raw DICOM data) and then create a BIDS compatible structure
"""

# convert to NIFTI
import os   
from nipype.interfaces.dcm2nii import Dcm2niix
import shutil
# folder names:
folder_name = ['anat','func','dwi','other']
subNumber = '1263'
session = 'ses-4'

source_dir = '/media/Drobo/Levy_Lab/Projects/PTSD_KPE/scan_data/raw/kpe1223/kpe1223_scan4_pb2126_harpaz-rotem'
output_dir = '/media/Data/kpe_forFmriPrep/'

subName = 'sub-' + subNumber
#%% Convert functions Converts DICOM to NIFTI.GZ
def convert (source_dir, output_dir, subName, session): # this is a function that takes input directory, output directory and subject name and then converts everything accordingly
    try:
        os.makedirs(os.path.join(output_dir, subName, session))
    except:
        print ("folder already there")
#    try:
#       os.makedirs(os.path.join(output_dir, subName, ))
#    except:
#       print("Folder Exist")    
    converter = Dcm2niix()
    converter.inputs.source_dir = source_dir
    converter.inputs.compression = 7
    converter.inputs.output_dir = os.path.join( output_dir, subName, session)
    converter.inputs.out_filename = subName + '_%d , %a, %c'
    converter.run()

#%% Check functions
def checkGz (extension):
     # check if nifti gz or something else
    if extension[1] =='.gz':
        return '.nii.gz'
    else:
        return extension[1]

def checkTask(filename):
    sep = 'bold'
    rest = filename.split(sep)[1] # takes the last part of filename
    taskName = rest.split('.',1)[0]
    return taskName.replace("_","")

#%% create folder structure 
# create folder structure
fullPath = os.path.join(output_dir, subName, session)
os.makedirs(fullPath + '/dwi')
os.makedirs(fullPath + '/anat')    
os.makedirs(fullPath + '/func')
os.makedirs(fullPath + '/misc')        
# read using keys: (i.e. diff for dwi, bold for func, MPRAGE or T1 for anat)

#%% Run convertion function
convert(source_dir, output_dir, subName, session) # run conversion

##%% run in the folder (session folder) and build file names
#a = next(os.walk(fullPath)) # list the subfolders under subject name
#
## run through the possibilities and match directory with scan number (day)
#for n in a[2]:
#    print (n)
#    b = os.path.splitext(n)
#    
#    if n.find('diff')!=-1:
#        print ('This file is DWI')
#        shutil.move((fullPath +'/' + n), fullPath + '/dwi/' + n)
#        os.rename((os.path.join(fullPath, 'dwi' ,n)), (fullPath + '/' + 'dwi' +'/' +'sub-' + subName + '_' + session +'_dwi' + checkGz(b)))
#        
#        
#    elif n.find('MPRAGE')!=-1:
#        print (n + ' Is Anat')
#        shutil.move((fullPath + '/' + n), (fullPath + '/anat/' + n))
#        os.rename(os.path.join(fullPath,'anat' , n), (fullPath + '/anat/' + 'sub-'+subName+ '_' + session + '_T1w' + checkGz(b)))
#    elif n.find('bold')!=-1:
#        print(n  + ' Is functional')
#        taskName = checkTask(n)
#        shutil.move((fullPath + '/' + n), (fullPath + '/func/' + n))
#        os.rename(os.path.join(fullPath, 'func', n), (fullPath  + '/func/' +'sub-'+subName+'_' +session + '_task-' + taskName + '_bold' + checkGz(b)))
#    else:
#        print (n + 'Is MISC')
#        shutil.move((fullPath + '/' + n), (fullPath + '/misc/' + n))
#       # os.rename(os.path.join(fullPath, 'misc', n), (fullPath +'/misc/' +'sub-'+subName+'_ses-' +sessionNum + '_MISC' + checkGz(b)))

#%%
def organizeFiles(outpu_dir, subName, session):
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
        
        if n.find('diff')!=-1:
            print ('This file is DWI')
            shutil.move((fullPath +'/' + n), fullPath + '/dwi/' + n)
            os.rename((os.path.join(fullPath, 'dwi' ,n)), (fullPath + '/' + 'dwi' +'/' + subName + '_' + session +'_dwi' + checkGz(b)))
            
            
        elif n.find('MPRAGE')!=-1:
            print (n + ' Is Anat')
            shutil.move((fullPath + '/' + n), (fullPath + '/anat/' + n))
            os.rename(os.path.join(fullPath,'anat' , n), (fullPath + '/anat/' + subName+ '_' + session + '_T1w' + checkGz(b)))
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
sessionDict = {
       
        'ses-1': '/media/Drobo/Levy_Lab/Projects/PTSD_KPE/scan_data/raw/kpe1369/kpe1369_scan1_pb3831_harpaz-rotem',
'ses-2': '/media/Drobo/Levy_Lab/Projects/PTSD_KPE/scan_data/raw/kpe1369/kpe1369_scan2_pb3882_harpaz-rotem',
'ses-3': '/media/Drobo/Levy_Lab/Projects/PTSD_KPE/scan_data/raw/kpe1369/kpe1369_scan3_pb4038_harpaz-rotem',
'ses-4': '/media/Drobo/Levy_Lab/Projects/PTSD_KPE/scan_data/raw/kpe1369/kpe1369_scan4_pb4437_harpaz-rotem'
        }
subNumber = '1369'
def fullBids(subNumber, sessionDict):
    output_dir = '/media/Data/kpe_forFmriPrep/'
    subName = 'sub-' + subNumber
    folder_name = ['anat','func','dwi','other']
    
    for i in sessionDict:
        session = i
        source_dir = sessionDict[i]
        print (session, source_dir)
        fullPath = os.path.join(output_dir, subName, session)
        print(fullPath)
        convert(source_dir,  output_dir, subName, session)
        organizeFiles(output_dir, subName, session)        
        
    
    #print (v)
#%%
fullBids(subNumber, sessionDict)
