# -*- coding: utf-8 -*-
"""
Written by: Or Duek
Date: Nov. 26, 2018

This script will run through folders and convert DICOM to compressed NIFTI files. 
Basic structure should be subject name/scans(days)/anat(rest etc). 
If not the same - DON'T USE THIS SCRIPT. 
We will build another that will match. 

Eventually it will built Sub/scan/condition with one file per condition and data files (match the BIDS demands)
"""
from nipype.interfaces.dcm2nii import Dcm2niix

import os

#mainFolder = os.path.abspath('/run/user/1000/gvfs/smb-share:server=172.21.64.199,share=levy_lab/Levy_Lab/Projects/PTSD_KPE/scan_data/raw/') # should be the main folder where all subjects can be found
mainFolder = os.path.abspath('/home/or/Documents/')
condList = [] # list of conditions (names of files) 
# leaving 'rest' to go to bold folder. 

def convert (source_dir, output_dir, subName): # this is a function that takes input directory, output directory and subject name and then converts everything accordingly
    converter = Dcm2niix()
    converter.inputs.source_dir = source_dir
    converter.inputs.compression = 7 # how much compression
    converter.inputs.output_dir = output_dir
    converter.inputs.out_filename = subName + '_%d , %a, %c'
    ## adding try exepct
    converter.run()
    
            
    

subName = ['NF1319'] # should be taken from a list or a file.     
#subNameFile = open('/home/or/Documents/dicom_niix/R_A_ptsd_subList.txt') # file with subject names
#lines = subNameFile.read().split()
#subName = ['subj' + s for s in lines]

os.makedirs('/run/user/1000/gvfs/smb-share:server=172.21.64.199,share=levy_lab/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Multiband/Converted', exist_ok=True) # creating specific folder to put all data in

# change to specific folder
os.chdir('/run/user/1000/gvfs/smb-share:server=172.21.64.199,share=levy_lab/Levy_Lab/Projects/R_A_PTSD_Imaging/Data/Scans/Multiband/Converted')
print(subName)
for name in subName:
    os.makedirs(name, exist_ok = True) # create folder for user
    dir_list = next(os.walk(os.path.join(mainFolder, name)))[1] # creates a list of folders inside main one
    
    for subDir in dir_list:
       
        subDir_list = next(os.walk(os.path.join(mainFolder,name,subDir)))[1]  # look for all subfolders, if we have more than one scan
        os.makedirs(os.path.join(name,subDir), exist_ok=True) # create subfolder for each day/scan
        for rawPath in subDir_list:
            if 'Info' in rawPath: # exclude information subfolder
                continue
            else:
               # print(rawPath)
                fullPath = os.path.join(mainFolder,name,subDir,rawPath)
               # print(fullPath)
                #os.makedirs(os.path.join(subName, subDir,rawPath), exist_ok=True)
                newPath = os.path.join(name, subDir) #,rawPath)
                
                # before converting - check if there are any files:
                if not os.listdir(fullPath):
                    print('Folder is empty')
                else:
                    try:
                        convert(fullPath, newPath, name)
                    except:
                        print ("There was an error in dcm2niix" + ' Source folder:' + fullPath +" output folder:" + newPath+ " subject number:" + name)
        fileList = [] # create empty list for now
        for root, dirs, files in os.walk(newPath):
            
            for file in files:
                fileList.append(file) # creates list of .nii.gz files within this folder (session/scan folder)
                
        # will run through the list of conditions, look foe the matching files and put in folders.
        # first we will make folder accordingly
        
        for n in condList:
            os.makedirs(os.path.join(newPath,n), exist_ok = True)
            for l in fileList:
                if l.find(n)!=-1: # if the filename contains this specific condition
                    # move file to new folder
                    os.rename(os.path.join(newPath, l), os.path.join(newPath,n,l))
                else:
                    continue
# now we should read filenames and create folder according to BIDS. 
# we will define a function that 

        

    