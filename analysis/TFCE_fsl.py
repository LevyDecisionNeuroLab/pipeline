#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 2022

TFCE correction for SPM first level.
inputs:
    SPM contrasts
    mask

Outputs:
    randomise_vox_tstat1
    randomise_tfce_tstat1

This script doesn't need too much resources and can be run using srun. 
To run this script:
1. adjust lines 41-47
2. create an interactive session: srun --pty -t 4:00:00 --mem=10G -c 4 -p interactive bash
3. load miniconda:                module load miniconda
4. activate conda enviroment:     conda activate fmri -> adjust to your enviroment
5. load MATLAB:                   module load MATLAB -> probably not needed
6. Load FSL:                      module load FSL
7. source FSL:                    . /gpfs/ysm/apps/software/FSL/6.0.4-centos7_64/etc/fslconf/fsl.sh


@author: Nachshon Korem PhD
"""

# libraries needed to run the script
import os
from nilearn.plotting import plot_glass_brain
from nilearn.plotting import plot_stat_map
from  nipype.interfaces import fsl
import nipype.pipeline.engine as pe  # pypeline engine
import nilearn.plotting
from glob import glob
import shutil

fsl.FSLCommand.set_default_output_type('NIFTI_GZ')

base_dir = '/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/results_obj_rand/' # where the output should go
contrast_num = '12' # number of the contrast (spmT_0001.nii) - you can also just put it in the template.
contrast_name = 'money_loss_bin' # output folder name

#templates adjust to project
con_images = glob('/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/results_obj_6/l1spm_resp/_subject_id_*/contrastestimate/spmT_00' + contrast_num + '.nii')
brainmasks = glob('/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/Aging_Bids/derivatives/sub-*/ses-1/func/sub-*_ses-1_task-task1_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz')

###############################
### change at your own risk ###
###############################

# collect contrasts from all participants
copes = list(con_images)    
copes_concat = nilearn.image.concat_imgs(con_images, auto_resample=True)
copes_concat.to_filename(base_dir + contrast_name + '.nii.gz')

# create mean mask
mean_mask = nilearn.image.mean_img(brainmasks)
group_mask = nilearn.image.math_img("a>=0.95", a=mean_mask)
group_mask = nilearn.image.resample_to_img(group_mask, copes_concat, interpolation='nearest')
group_mask.to_filename(base_dir + '/group_mask.nii.gz')

# run fsl randomise - TFCE
randomize = pe.Node(interface = fsl.Randomise(), base_dir = base_dir,
                    name = 'randomize')
randomize.inputs.in_file = base_dir + contrast_name + '.nii.gz' # choose which file to run permutation test on
randomize.inputs.mask = base_dir + 'group_mask.nii.gz' # group mask file (was created earlier)
randomize.inputs.one_sample_group_mean = True
randomize.inputs.tfce = True
randomize.inputs.vox_p_values = True
randomize.inputs.num_perm = 1000

randomize.run()

# move files to contrast spesific folder
os.mkdir(base_dir + contrast_name)
dest = base_dir + contrast_name
for file in glob(base_dir + r'randomize/*.nii.gz'):
    shutil.copy(file, dest)
