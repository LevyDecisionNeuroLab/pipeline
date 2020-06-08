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
    converter.inputs.output_dir = os.path.join(output_dir, subName, session)
    converter.inputs.out_filename = subName + '_' + '%2s' + "_" +'%p'
    converter.run()

#%% Check functions
def checkGz (extension):
     # check if nifti gz or something else
    if extension[1] =='.gz':
        return '.nii.gz'
    else:
        return extension[1]

def checkTask(funcdir, subName, ses):
    
    files = next(os.walk(funcdir))[2]
    files.sort()
    task  = {'rest' : {},
             'task' : {}}
    
    for f in files:
        if f.find('rest')!=-1:
            task['rest'][f.split('_')[1]] = 'rest'+str(len(task['rest']))
        else:
            run = f.split('bold')[1].split('.')[0].replace('(MB4iPAT2)','').replace('task','').replace('_','').replace('-','')
            if  run == '':
                task['task'][f.split('_')[1]] = 'task'+str(len(task['task']))
            else:
                task['task'][f.split('_')[1]] = run
                            
    
    for f in files:
        ext = checkGz(os.path.splitext(f))
        src = (os.path.join(funcdir, f))
        kind = 'task'
        if f.find('rest')!=-1:
             kind = 'rest'
        dest = funcdir + subName + '_' + ses + '_task-' + task[kind][f.split('_')[1]] + "_bold" + ext
        
        os.rename(src, dest)

def checkdwi(dwidir, subName, ses):
    files = next(os.walk(dwidir))[2]
    files.sort()
    runs = []
    for f in files:
        runs.append(int(f.split('_')[1]))
    minrun = min(runs)
    for f in files:
        ext = checkGz(os.path.splitext(f))
        run = 1+int(f.split('_')[1])-minrun
        src = (os.path.join(dwidir, f))
        dest = dwidir + subName + '_' + ses + '_run-' + str(run) + '_dwi' + ext
        os.rename(src, dest)
    
#%%
def organizeFiles(output_dir, subName, session):
    
    fullPath = os.path.join(output_dir, subName, session)
    os.makedirs(fullPath + '/dwi')
    os.makedirs(fullPath + '/anat')    
    os.makedirs(fullPath + '/func')
    os.makedirs(fullPath + '/misc')    
    
    a = next(os.walk(fullPath)) # list the subfolders under subject name
    dwi = False
    # run through the possibilities and match directory with scan number (day)
    for n in a[2]:
        print (n)
        b = os.path.splitext(n)
        # add method to find (MB**) in filename and scrape it
        if n.find('diff')!=-1:
            print ('This file is DWI')
            dwi = True
            shutil.move((fullPath +'/' + n), fullPath + '/dwi/' + n)
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
            shutil.move((fullPath + '/' + n), (fullPath + '/func/' + n))
        else:
            print (n + 'Is MISC')
            shutil.move((fullPath + '/' + n), (fullPath + '/misc/' + n))
           
    checkTask((fullPath + '/func/'), subName, session)
    if dwi:
        checkdwi((fullPath + '/dwi/'), subName, session)
    
# need to run thorugh misc folder and extract t1's when there is no MPRAGE - Need to solve issue with t1 - as adding the names is not validated with BIDS
#%%
sessionDict = {
      'ses-1': '/media/Drobo/Levy_Lab/Projects/PTSD_reconsolidation/TrioB/Scan_data/newer/RCF1099/RCF1099_D1_tb2387_harpaz-rotem'
#      'ses-2': '/media/Data/Lab_Projects/KPE_PTSD_Project/neuroimaging/raw_dicom/kpe1480/kpe1480_scan2_pb8818_harpaz-rotem',
#     'ses-3': '/media/Data/Lab_Projects/KPE_PTSD_Project/neuroimaging/raw_dicom/kpe1480/kpe1480_scan4_pb9370_harpaz-rotem'
        }
subNumber = '1099'
def fullBids(subNumber, sessionDict):
    output_dir = '/media/Data/Lab_Projects/RCF/neuroimaging/test'
    subName = 'sub-' + subNumber
    
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
