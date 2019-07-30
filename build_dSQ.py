#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 09:20:14 2019

@author: Or Duek
Build a dSQ script

This script is an example for building a dSQ (dead simple sequence) for use in slurm - to run fmriPrep for many subjects at once.
Please notice that you need to supply a subject number list (subList) and keep in mind that fmriPrep versin might change
Also- keep in mind to change paths for the BIDS compatible image files and the output directory
After creating this txt file (basically each line is a different fmriPrep run) you should follow the next steps in the cluster:
    1. module load dSQ
    2. dSQ --jobfile MyFile.txt -c 10 -t 16:00:00 --mem=10g > run.sh (can change number of cpus, memory and time)
    3. Read the run.sh file to receive the actual filename
    4. sbatch actualFileName (from run.sh) 
"""

# iterate trhough subject list and create a single line calling singularity for each subject
import pandas as pd
subList = sub_id

file1 = open("MyFile.txt","a") # open an empty txt file
for sub in subList:
    a = 'singularity run --cleanenv /project/ysm/levy_ifat/fmriPrep/fmriprep-1.4.1.simg /home/oad4/scratch60/RCF_BidsConversion /home/oad4/scratch60/RCF_output participant --skip_bids_validation --fs-license-file /home/oad4/freesurferLicense/license.txt -w /home/oad4/scratch60/work_RCF --nthreads 8 --participant_label %s \n' %(sub)
    print (a)        
    file1.write(a)
    
file1.close()