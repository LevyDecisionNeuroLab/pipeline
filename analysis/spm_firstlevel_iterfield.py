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
from nipype import Node, Workflow, MapNode, JoinNode
#from nipype.algorithms.misc import Gunzip #ADDED FROM RUONAN'S SCRIPT

from nipype.interfaces import fsl
from nipype.interfaces import spm
from nipype.interfaces.matlab import MatlabCommand
from nipype.interfaces.utility import Function

# SPM and FSL initiation

MatlabCommand.set_default_paths('/gpfs/gibbs/pi/levy_ifat/shared/MATLAB/spm12/') # set SPM12 path in the shared folder on the HPC 
fsl.FSLCommand.set_default_output_type('NIFTI')

#%%

##########################
### Start editing here ###
##########################
# Adjust locations

data_dir =   '/gpfs/gibbs/pi/levy_ifat/Or/alexData/'
output_dir =  data_dir + '_results2/' 
work_dir = '/home/oad4/scratch60/work'

# subject list

subject_list = ['2717'] # Map field names to individual subject runs.

task_id = [1,2]


templates = {'func':       data_dir + 'sub-{subject_id}/ses-1/func/sub-{subject_id}_ses-1_task-Med{task_id}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz',
           #  'mask':       data_dir + '/RAMDMolderadults_BIDS/derivatives/sub-{subject_id}/ses-1/func/sub-{subject_id}_ses-1_task-{task_id}_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz',
             'regressors': data_dir + 'sub-{subject_id}/ses-1/func/sub-{subject_id}_ses-1_task-Med{task_id}_desc-confounds_timeseries.tsv',
             'events':     data_dir + '/sub-{subject_id}_task-task{task_id}_cond_v3.csv'}

# basic experiment properties

fwhm = 6 # full width at half maximum a.k.a smoothing in mm3
tr = 1 # Length of TR in seconfs
removeTR = 4 # how many TRs should be removed from the beginning of the scan
highpass = 128. # high pass filter should be a float
motion_params = 6 # number of motion parameters to include in the GLM should be 0, 6 or 25
fd = 1 # Do you want to enter FD to the GLM? 1 yes 0 no 
dvars = 1 # Do you want std_dvars in the model? 1 yes 0 no 
n_comp_corr = 6 # how many comp corr do you want in your model? valid values are 0 and 6
n_procs = 2 # number of parallel process



#%% contrasts

# set contrasts, depend on the condition
cond_names = ['Med_amb', 'Med_risk', 'Mon_amb', 'Mon_risk']

cont1 = ('Med_Amb', 'T', ['Med_amb'], [1])
cont2 = ('Med_Risk', 'T', ['Med_risk'], [1])
cont3 = ('Med_Amb>Risk', 'T', cond_names, [1, -1, 0, 0])
cont4 = ('Mon_Amb', 'T', ['Mon_amb'], [1])
cont5 = ('Mon_Risk', 'T', ['Mon_risk'], [1])
cont6 = ('Mon_Amb>Risk', 'T', cond_names, [0, 0, 1, -1])
cont7 = ('Med>Mon_Amb', 'T', cond_names, [1, 0, -1, 0])
cont8 = ('Med>Mon_Risk', 'T', cond_names, [0, 1, 0, -1])
cont9 = ('Med>Mon', 'T', cond_names, [1, 1, -1, -1])
cont10 = ('Mon>Med', 'T', cond_names, [-1, -1, 1, 1])

contrasts = [cont1]#, cont2, cont3]#, cont4, cont5, cont6, cont7, cont8, cont9, cont10]

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
    events = pd.read_csv(events_file, sep='\t')
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

    domain = list(set(events.condition.values))[0] # domain of this task run, should be only one, 'Mon' or 'Med'
    trial_types = list(set(events.trial_type.values))
        
    runinfo = Bunch(
        scans=in_file,
        conditions=[domain + '_' + trial_type for trial_type in trial_types],
        # conditions = ['Med_amb', 'Med_risk', 'Mon_amb', 'Mon_risk'],
        **{k: [] for k in bunch_fields})
    
    for condition in runinfo.conditions:
        event = events[events.trial_type.str.match(condition[4:])]

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
# FROM RUONAN'S SCRIPT:
#infosource = pe.Node(util.IdentityInterface(fields=['subject_id', 'task_id']), 
#                  name="infosource")
#infosource.iterables = [('subject_id', subject_list), ('task_id', task_list)]


    
infosource = pe.Node(util.IdentityInterface(fields=['subject_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]


# Flexibly collect data from disk to feed into flows.

selectfiles = pe.Node(nio.SelectFiles(templates,
                      base_directory=data_dir),
                      name="selectfiles")

selectfiles.inputs.task_id = task_id #ALSO PART OF RUONAN'S SCRIPT

runinfo = MapNode(util.Function(
    input_names=['in_file', 'events_file', 'regressors_file', 'regressors_names', 'removeTR', 'motion_columns'],
    function=_bids2nipypeinfo, output_names=['info', 'realign_file']),
    name='runinfo',
    iterfield = ['in_file', 'events_file', 'regressors_file'])

      
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

#gunzip = MapNode(Gunzip(), name='gunzip', iterfield=['in_file']) #ADDED FROM RUONAN'S SCRIPT
    
#extract = Node(fsl.ExtractROI(), name="extract")
extract = pe.MapNode(fsl.ExtractROI(), name="extract", iterfield = ['in_file'])
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
#wfSPM.run('Linear', plugin_args={'n_procs': 1})