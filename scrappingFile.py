#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 09:43:43 2019

@author: Or Duek
small script that will remove (MB4iPAT2) from filename
"""

import os
from bids.grabbids import BIDSLayout

data_dir = '/media/Data/PTSD_Reversal_2018/scan_data/raw/megha/BIDS'
#data_dir = '/media/Data/kpe_forFmriPrep'

layout = BIDSLayout(data_dir)
source_epi = layout.get(type="bold")

for i in source_epi:
    a = i.filename
   # print (i.filename)
    if a.find('(MB4iPAT2)')!=-1:
        print ("We have found an issue with ", a)
        b = a.split('(MB4iPAT2)') # this is the part that will be omitted from the file name. If you have an extra - you should add that too. 
        c = b[0] + b[1] # cmobine toghether
        #change filename
        os.rename(a, c)
