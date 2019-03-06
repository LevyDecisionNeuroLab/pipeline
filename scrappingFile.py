#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 09:43:43 2019

@author: Or Duek
small script that will remove (MB4iPAT2) from filename
"""

import os
from bids.grabbids import BIDSLayout

data_dir = '/media/Data/testKPE'
#data_dir = '/media/Data/kpe_forFmriPrep'

layout = BIDSLayout(data_dir)
source_epi = layout.get(type="bold")

for i in source_epi:
    a = i.filename
   # print (i.filename)
    if a.find('((MB4iPAT2))'):
        print (a)
        b = a.split('-(MB4iPAT2)')
        c = b[0] + b[1] # cmobine toghether
        #change filename
        os.rename(a, c)
