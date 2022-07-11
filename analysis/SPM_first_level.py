#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 09:52:15 2022

Basic first level analysis GLM using SPM

@author: Nachshon Korem PhD
"""

#%%
# General python libraries

import os
import pandas as pd
import numpy as np

# nipype libraries


import nipype.interfaces.io as nio  # Data i/o
import nipype.interfaces.utility as util  # utility
import nipype.pipeline.engine as pe  # pypeline engine
import nipype.algorithms.modelgen as model  # model specification
from nipype import Node, Workflow, MapNode

from nipype.interfaces import fsl
from nipype.interfaces import spm
from nipype.interfaces.matlab import MatlabCommand
from nipype.interfaces.utility import Function

# SPM and FSL initiation

MatlabCommand.set_default_paths('/gpfs/gibbs/pi/levy_ifat/shared/MATLAB/spm12/') # set SPM12 path in the shared folder on the HPC 
fsl.FSLCommand.set_default_output_type('NIFTI_GZ')

#%%

##########################
### Start editing here ###
##########################

# Adjust locations
data_dir =   '/gpfs/gibbs/pi/levy_ifat/Nachshon/CB1/'
output_dir =  data_dir + 'results/' 
work_dir = '/home/nk549/scratch60/work'

# subject list
subject_list = ['14032', '1547', '1554', '1571', '1575', '1586', '1593', '1599', 
                '1609', '1623', '1631', '1643', '1649', '1652', '1653', '1656', '1666', '1695', 
                '1707', '1708', '1710', '17122', '1713', '1714'] # Map field names to individual subject runs. 

templates = {'func':       data_dir + 'BIDS/derivatives/sub-{subject_id}/ses-1/func/sub-{subject_id}_ses-1_task-task{task_id}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz',
             'mask':       data_dir + 'BIDS/derivatives/sub-{subject_id}/ses-1/func/sub-{subject_id}_ses-1_task-task{task_id}_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz',
             'regressors': data_dir + 'BIDS/derivatives/sub-{subject_id}/ses-1/func/sub-{subject_id}_ses-1_task-task{task_id}_desc-confounds_timeseries.tsv',
             'events':     data_dir + '/eventfiles/cb1Reversal_{subject_id}.csv'}

task_ids = [1] # a list of task ids


# basic experiment properties
fwhm = 6 # full width at half maximum a.k.a smoothing in mm3
tr = 1 # Length of TR in seconfs
removeTR = 4 # how many TRs should be removed from the beginning of the scan
highpass = 128. # high pass filter should be a float
motion_params = 6 # number of motion parameters to include in the GLM should be 0, 6 or 25
fd = 1 # Do you want to enter FD to the GLM? 1 yes 0 no 
dvars = 1 # Do you want std_dvars in the model? 1 yes 0 no 
n_comp_corr = 6 # how many comp corr do you want in your model? valid values are 0 and 6
n_procs = 1 # number of parallel process


## Building contrasts
# set contrasts, depend on the condition
# the condition names (cond_names) should correspond to the names of the event file.
# contrasts should be ('name of contrast - string', 'T (can also be F)', [a list of condition names], [a list of integers]) 
cond_names = ['CSplusUS1', 'CSminusUS2', 'CSplus1', 'CSplus2', 'CSminus1', 'CSminus2'] # CS+US vs CS+ all
cont1 = ('Shock_NoShockCS+', 'T', cond_names, [.5, .5, -.5, 0, 0, -.5]) # add CS+ vs. CS- all exp.
cont2 = ('CS+ > CS-', 'T', cond_names, [0, 0, .5, -.5, -.5 , .5]) # CS+ vs. baseline all
cont3 = ('CS+ > nothing', 'T', cond_names, [0, 0, .5, 0, 0, .5]) # CS+US vs CS+ 1st half
cont4 = ('Shock_NoShockCS+1stHalf', 'T', cond_names, [1, 0, -1, 0, 0, 0]) # CS+US vs CS+ 2nd Half
cont5 = ('Shock_NoShockCS+2tHalf', 'T', cond_names, [0, 1, 0, 0, 0, -1]) # add CS+ vs. CSminus 1st half.
cont6 = ('CS+ > CS-1stHalf', 'T', cond_names, [0, 0, 1, -1, 0 , 0]) # CS+ vs. CS- 2nd half
cont7 = ('CS+ > CS-2stHalf', 'T', cond_names, [0, 0, 0, -1, 0, 1]) # CS- vs. baseline all 
cont8 = ('CS- > baselineAll', 'T', cond_names, [0, 0, 0, .5, .5, 0]) # CS- vs. baseline 1st half
cont9 = ('CS- > baseline1stHalf', 'T', cond_names, [0, 0, 0, 1, 0 , 0]) # CS- vs. baseline 2nd half
cont10 = ('CS- > baseline2ndHalf', 'T', cond_names, [0, 0, 0, 0, 1, 0]) 
## adding CS+ vs. baseline in the two halfs
cont11 = ('CS+ > nothing_1stHalf', 'T', cond_names, [0, 0, 1, 0, 0 ,0])
cont12 = ('CS+ > nothing_2ndHalf', 'T', cond_names, [0, 0, 0, 0, 0, 1])
cont13 = ('stim', 'T', cond_names, [1, 1, 1, 1, 1, 1])

contrasts = [cont1, cont2, cont3, cont4, cont5, cont6, cont7, 
cont8, cont9, cont10, cont11, cont12, cont13]

#############################################
### Edit below this line at your own risk ###
#############################################

#%% regressors for design matrix

def _bids2nipypeinfo(in_file, events_file, regressors_file,
                     regressors_names=None,
                     motion_columns=None, removeTR = 4,
                     decimals=3, amplitude=1.0):
    
    from pathlib import Path
    from nipype.interfaces.base.support import Bunch
    import pandas as pd
    import numpy as np

    # Process the events file
    events = pd.read_csv(events_file, sep = ',')
    bunch_fields = ['onsets', 'durations', 'amplitudes']

    if not motion_columns:
        from itertools import product
        motion_columns = ['_'.join(v) for v in product(('trans', 'rot'), 'xyz')]

    out_motion = Path('motion.par').resolve()
    regress_data = pd.read_csv(regressors_file, sep=r'\s+')
    np.savetxt(out_motion, regress_data[motion_columns].values[removeTR:,], '%g')
    
    if regressors_names is None:
        regressors_names = sorted(set(regress_data.columns) - set(motion_columns))

    if regressors_names:
        bunch_fields += ['regressor_names']
        bunch_fields += ['regressors']

    runinfo = Bunch(
        scans=in_file,
        conditions=list(set(events.trial_type.values)),
        **{k: [] for k in bunch_fields})

    for condition in runinfo.conditions:
        event = events[events.trial_type.str.match(condition)]

        runinfo.onsets.append(np.round(event.onset.values-removeTR, 3).tolist()) # added -removeTR to align to the onsets after removing X number of TRs from the scan
        runinfo.durations.append(np.round(event.duration.values, 3).tolist())
        if 'amplitudes' in events.columns:
            runinfo.amplitudes.append(np.round(event.amplitudes.values, 3).tolist())
        else:
            runinfo.amplitudes.append([amplitude] * len(event))

    if 'regressor_names' in bunch_fields:
        runinfo.regressor_names = regressors_names
        runinfo.regressors = regress_data[regressors_names].fillna(0.0).values[removeTR:,].T.tolist() # adding removeTR to cut the first rows

    return runinfo, str(out_motion)

#%%
infosource = pe.Node(util.IdentityInterface(fields=['subject_id']),
                  name="infosource")

infosource.iterables = [('subject_id', subject_list)]

# Flexibly collect data from disk to feed into flows.

selectfiles = pe.Node(nio.SelectFiles(templates,
                      base_directory=data_dir),
                      name="selectfiles")

selectfiles.inputs.task_id = task_ids   

runinfo = Node(util.Function(
    input_names=['in_file', 'events_file', 'regressors_file', 'regressors_names', 'removeTR', 'motion_columns'],
    function=_bids2nipypeinfo, output_names=['info', 'realign_file']),
    name='runinfo')

      
regressors = ['std_dvars'*dvars, 'framewise_displacement'*fd] + ['a_comp_cor_%02d' % i for i in range(n_comp_corr)]

while('' in regressors) :
    regressors.remove('')

runinfo.inputs.regressors_names = regressors

runinfo.inputs.removeTR = removeTR                                  
 
motion = ['trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z'] + \
         ['trans_x_derivative1', 'trans_y_derivative1', 'trans_z_derivative1', 'rot_x_derivative1', 'rot_y_derivative1', 'rot_z_derivative1'] + \
         ['trans_x_derivative1_power2', 'trans_y_derivative1_power2', 'trans_z_derivative1_power2', 'rot_x_derivative1_power2', 'rot_y_derivative1_power2', 'rot_z_derivative1_power2'] + \
         ['trans_x_power2', 'trans_y_power2', 'trans_z_power2', 'rot_x_power2', 'rot_y_power2', 'rot_z_power2']

runinfo.inputs.motion_columns   = motion[:motion_params]
    
extract = Node(fsl.ExtractROI(), name="extract")
extract.inputs.t_min = removeTR
extract.inputs.t_size = -1
extract.inputs.output_type='NIFTI' 

smooth = Node(spm.Smooth(), name="smooth", fwhm = fwhm)


modelspec = Node(interface=model.SpecifySPMModel(), name="modelspec") 
modelspec.inputs.concatenate_runs = False
modelspec.inputs.input_units = 'scans' # supposedly it means tr
modelspec.inputs.output_units = 'scans'
modelspec.inputs.time_repetition = 1.  # make sure its with a dot 
modelspec.inputs.high_pass_filter_cutoff = highpass

level1design = pe.Node(interface=spm.Level1Design(), name="level1design") #, base_dir = '/media/Data/work')
level1design.inputs.timing_units = modelspec.inputs.output_units
level1design.inputs.interscan_interval = 1.
level1design.inputs.bases = {'hrf': {'derivs': [0, 0]}}
level1design.inputs.model_serial_correlations = 'AR(1)'



level1estimate = pe.Node(interface=spm.EstimateModel(), name="level1estimate")
level1estimate.inputs.estimation_method = {'Classical': 1}

#%% contrasts



contrastestimate = pe.Node(
    interface=spm.EstimateContrast(), name="contrastestimate")
contrastestimate.overwrite = True
contrastestimate.config = {'execution': {'remove_unnecessary_outputs': False}}
contrastestimate.inputs.contrasts = contrasts      
         
#%% Connect workflow
wfSPM = Workflow(name="l1spm_resp", base_dir=output_dir)
wfSPM.connect([
        (infosource,     selectfiles,      [('subject_id',     'subject_id')]),
        (selectfiles,    runinfo,          [('events',         'events_file'),
                                            ('regressors',     'regressors_file')]),
        (selectfiles,    extract,          [('func',           'in_file')]),
        (extract,        smooth,           [('roi_file',       'in_files')]),
        (smooth,         runinfo,          [('smoothed_files', 'in_file')]),
        (smooth,         modelspec,        [('smoothed_files', 'functional_runs')]),   
        (runinfo,        modelspec,        [('info',           'subject_info'), 
                                            ('realign_file',   'realignment_parameters')]),
        (modelspec,      level1design,     [('session_info',   'session_info')]),
        (level1design,   level1estimate,   [('spm_mat_file',   'spm_mat_file')]),
        (level1estimate, contrastestimate, [('spm_mat_file',   'spm_mat_file'), 
                                            ('beta_images',    'beta_images'),
                                            ('residual_image', 'residual_image')]),
        ])

#%% Run workflow
wfSPM.run('MultiProc', plugin_args={'n_procs': n_procs})                                