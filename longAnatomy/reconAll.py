#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 16:42:40 2019
@author: Or Duek
This script runs recon-all on all (number of) sessions and then continue to label subregions of hippocampus and amygdala
"""

# folders necessary for analysis
import nipype.pipeline.engine as pe
import nipype.interfaces.io as nio
from nipype.interfaces.freesurfer.preprocess import ReconAll
from nipype.interfaces.utility import Function
import nipype.interfaces.utility as util  # utility
import os

# this is a python folder that should be in the same directory
from hippSeg import CustomHippoSeg # this is a costum made node - so you'll need the file hippSeg.py in the same folder
data_dir = '/gpfs/gibbs/pi/levy_ifat/Nachshon/KPE' # change this to the location of your data
subjects_dir = '/gpfs/gibbs/pi/levy_ifat/Nachshon/KPE/freesurfer7.1_ses3/' # this is FreeSurfer's subject dir. i.e output

wf = pe.Workflow(name="l1workflow")
wf.base_dir = os.path.abspath(subjects_dir)

# Create a simple function that takes recon_all output and returns a string 
def changeToString(arr):
    return arr[0]

# adjust to your subjects
subject_list = ['008', '1223', '1253', '1293', '1307', '1315', '1322', '1339', '1343', '1351', '1356', '1364', '1369', '1387', '1390', '1403', '1419', '1464', '1468', '1480', '1499', '1561', '1573', '1578', '1587', '1612']

# I ran it seperatly for each subject as it overwritten each session
session_list  = ['3']#['1', '2', '3']

# Map field names to individual subject runs.
infosource = pe.Node(util.IdentityInterface(fields=['subject_id'
                                            ],
                                    ),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]


infosource_task = pe.Node(util.IdentityInterface(fields = ['session']),
                                                 name = "infosource_task")
infosource_task.iterables = [('session', session_list)]

# asjust the template to thelocation of the T1 
templates = {'anat': '/gpfs/gibbs/pi/levy_ifat/Nachshon/KPE/sub-{subject_id}/ses-{session}/anat/sub-{subject_id}_ses-{session}_T1w.nii.gz'}


selectfiles = pe.Node(nio.SelectFiles(templates,
                               base_directory=data_dir),
                   name="selectfiles")

recon_all = pe.MapNode(
    interface=ReconAll(),
    name='recon_all',
    iterfield=['subject_id'])
recon_all.inputs.subject_id = subject_list
recon_all.inputs.directive = "all"
if not os.path.exists(subjects_dir):
    os.mkdir(subjects_dir)
recon_all.inputs.subjects_dir = subjects_dir #Here we use specific directory, in order to avoid crash when trying to create simlinks. 
#recon_all.inputs.hippocampal_subfields_T1 = True # add hippocampal subfields

# home made Node to run hippocampus and amygdala segmentation.
## Now we should add another node that will run the hippocampal subfield script:
## Look here for instructions on how to run and wrap it in a node?
## https://surfer.nmr.mgh.harvard.edu/fswiki/HippocampalSubfieldsAndNucleiOfAmygdala

hippSeg = pe.Node(interface = CustomHippoSeg(), name = 'hippSeg')
#hippSeg.inputs.subject_dir = subjects_dir

changeToString= pe.Node(name='changeToString',
               interface=Function(input_names=['arr'],
                                  output_names=['arr'],
                                  function=changeToString))
  
wf.connect([(infosource, selectfiles, [('subject_id', 'subject_id')]),
            (infosource, recon_all, [('subject_id', 'subject_id')]),
            (infosource_task, selectfiles, [('session','session')]),
            (selectfiles, recon_all, [('anat','T1_files')]),
            (infosource, hippSeg, [('subject_id', 'subject_id')]),
            (recon_all, changeToString, [('subjects_dir', 'arr')]),
            (changeToString, hippSeg, [('arr','subject_dir')])
        ])


wf.run("MultiProc", plugin_args={'n_procs': 13})