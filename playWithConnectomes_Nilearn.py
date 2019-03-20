#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 10:33:10 2019

@author: Or Duek
Nilearn connectivity analysis. 
Taken from Nilearn site and from:
    https://github.com/miykael/workshop_cambridge/blob/master/notebooks/functional_connectivity.ipynb
"""
from nilearn import datasets

adhd_dataset = datasets.fetch_adhd(n_subjects=30)
func_filenames = adhd_dataset.func  # list of 4D nifti files for each subject

# print basic information on the dataset
print('First functional nifti image (4D) is at: %s' %
      func_filenames[0])  # 4D data

from nilearn.decomposition import CanICA

canica = CanICA(n_components=20, smoothing_fwhm=6.,
                memory="nilearn_cache", memory_level=2,
                threshold=3., verbose=10, random_state=0)
canica.fit(func_filenames)

# Retrieve the independent components in brain space. Directly
# accesible through attribute `components_img_`. Note that this
# attribute is implemented from version 0.4.1. For older versions,
# see note section above for details.
components_img = canica.components_img_
# components_img is a Nifti Image object, and can be saved to a file with
# the following line:
components_img.to_filename('canica_resting_state.nii.gz')


from nilearn.plotting import plot_prob_atlas

# Plot all ICA components together
plot_prob_atlas(components_img, title='All ICA components')

from nilearn.image import iter_img
from nilearn.plotting import plot_stat_map, show

for i, cur_img in enumerate(iter_img(components_img)):
    plot_stat_map(cur_img, display_mode="z", title="IC %d" % i,
                  cut_coords=1, colorbar=False)


#%% Try with ketamine
subList = ['008', '1223' , '1253' , '1293' ,'1307','1322','1339','1343','1387']

import os
# Reading all resting state file for 
rest_files = ['/media/Data/KPE_fmriPrep_preproc/kpeOutput/fmriprep/sub-%s/ses-2/func/sub-%s_ses-2_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz' % (sub,sub) for sub in subList]
# gather confound files
confound_files = ['/media/Data/KPE_fmriPrep_preproc/kpeOutput/fmriprep/sub-%s/ses-2/func/sub-%s_ses-2_task-rest_desc-confounds_regressors.tsv' % (sub,sub) for sub in subList]



from shutil import copyfile
for i in confound_files:
    print (i)
    fileName = i.split('/')
    fileName = fileName[9] 
    copyfile(i, 'nilearn/' + fileName)


confoundReal_files = ['/home/or/nilearn/sub-%s_ses-2_task-rest_desc-confounds_regressors.tsv' % (sub) for sub in subList]
canica = CanICA(n_components=20, smoothing_fwhm=6.,
                memory="/media/Data/nilearn", memory_level=2,
                threshold=3., verbose=10, random_state=0)#, mask = "/media/Data/work/custom_modelling_spm/group_mask.nii.gz")
canica.fit(rest_files)
components_img = canica.components_img_
# Plot all ICA components together
plotting.plot_prob_atlas(components_img, draw_cross=False, linewidths=None,
                         cut_coords=[0, 0, 0], title='All ICA components');

#%%
from nilearn.plotting import plot_prob_atlas

# Plot all ICA components together
plot_prob_atlas(components_img, title='All ICA components')

from nilearn.image import iter_img
from nilearn.plotting import plot_stat_map, show

for i, cur_img in enumerate(iter_img(components_img)):
    plot_stat_map(cur_img, display_mode="z", title="IC %d" % i,
                  cut_coords=1, colorbar=False)

show()

#%% Do the same with session 1
rest_files_s1 = ['/media/Data/KPE_fmriPrep_preproc/kpeOutput/fmriprep/sub-%s/ses-1/func/sub-%s_ses-1_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz' % (sub, sub) for sub in subList]
canica.fit(rest_files_s1)

#%% Dictionary learning
# Import dictionary learning algorithm
from nilearn.decomposition import DictLearning
# Initialize DictLearning object
dict_learn = DictLearning(n_components=20,
                          smoothing_fwhm=6.,
                          random_state=0,
                          memory = "nilearn",
                          verbose=1, memory_level=2)

dict_learn.fit(rest_files)
components_img = dict_learn.components_img_
# Plot all ICA components together
plotting.plot_prob_atlas(components_img, draw_cross=False, linewidths=None,
                         cut_coords=[0, 0, 0], title='Dictionary Learning maps');



plotting.plot_glass_brain(dict_learn.components_img_.slicer[..., 16], black_bg=True,
                          title='DictLearning component - Auditory Cortex', colorbar=True)

plotting.plot_glass_brain(canica.components_img_.slicer[..., 16], black_bg=True,
                          plot_abs=False, symmetric_cbar=False,
                          title='CanICA component - Auditory Cortex', colorbar=True)

plotting.plot_stat_map(canica.components_img_.slicer[..., 0], display_mode='ortho',
                       cut_coords=[0, -75, 4], colorbar=True, draw_cross=False,
                       title='CanICA component - Visual Cortex')
plotting.plot_stat_map(dict_learn.components_img_.slicer[..., 3], display_mode='ortho',
                       cut_coords=[0, -75, 4], colorbar=True, draw_cross=False,
                       title='DictLearning component - Visual Cortex')


#%% Extracting connectomes using dict learning

from nilearn.regions import RegionExtractor

extractor = RegionExtractor(dict_learn.components_img_, threshold=0.2,
                            thresholding_strategy='ratio_n_voxels',
                            extractor='local_regions', verbose=1,
                            standardize=True, min_region_size=1350)
extractor.fit()
# Total number of regions extracted
n_regions_extracted = extractor.regions_img_.shape[-1]
n_regions_extracted
regions_extracted_img = extractor.regions_img_
# Each region index is stored in index_
regions_index = extractor.index_
title = ('%d regions are extracted from %d components.'
         '\nEach separate color of region indicates extracted region'
         % (n_regions_extracted, 20))
plotting.plot_prob_atlas(regions_extracted_img, view_type='filled_contours',
                         title=title)

from nilearn import plotting
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from nilearn import image

from nilearn.connectome import ConnectivityMeasure

# Initializing ConnectivityMeasure object with kind='correlation'
connectome_measure = ConnectivityMeasure(kind='correlation')

# Iterate over the subjects and compute correlation matrix for each
correlations = []
for filename, confound in zip(rest_files, confoundReal_files):
    
    timeseries_each_subject = extractor.transform(filename, confounds=confound)
    
    correlation = connectome_measure.fit_transform([timeseries_each_subject])
    
    correlations.append(correlation)

# Get array in good numpy structure
correlations = np.squeeze(correlations)

# Computing the mean correlation matrix
mean_correlations = np.mean(correlations, axis=0)

# Plot the average correlation matrix
title = 'Correlation between %d regions' % n_regions_extracted
plotting.plot_matrix(mean_correlations, vmax=1, vmin=-1, colorbar=True,
                     labels=['IC %0d' % i for i in range(n_regions_extracted)],
                     title=title, reorder=True)

# Find the center of the regions with find_xyz_cut_coords
coords_connectome = [plotting.find_xyz_cut_coords(img)
                     for img in image.iter_img(extractor.regions_img_)]

# Plot the functional connectome on the glass brain
plotting.plot_connectome(mean_correlations, coords_connectome,
                         edge_threshold='99%', title=title)


#%%
# First, we plot a network of index=4 without region extraction (left plot)
from nilearn import image

img = image.index_img(components_img, 4)
coords = plotting.find_xyz_cut_coords(img)
display = plotting.plot_stat_map(img, cut_coords=coords, colorbar=False,
                                 title='Showing one specific network')


# For this, we take the indices of the all regions extracted related to original
# network given as 4.
regions_indices_of_map3 = np.where(np.array(regions_index) == 4)

display = plotting.plot_anat(cut_coords=coords,
                             title='Regions from this network')

# Add as an overlay all the regions of index 4
colors = 'rgbcmyk'
for each_index_of_map3, color in zip(regions_indices_of_map3[0], colors):
    display.add_overlay(image.index_img(regions_extracted_img, each_index_of_map3),
                        cmap=plotting.cm.alpha_cmap(color))

plotting.show()


#%% Function to choose specigic confounds from fmriPrep confound list
def removeVars (confoundFile):
    import pandas as pd
    confound = pd.read_csv(confoundFile,sep="\t", na_values="n/a")
    finalConf = confound[['csf', 'white_matter', 'global_signal', 'a_comp_cor_00', 'a_comp_cor_01',	'a_comp_cor_02', 'a_comp_cor_03', 'a_comp_cor_04', 
                          'a_comp_cor_05', 'trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z']]
    return finalConf

#%% Run on Midazolam group
subListMidazolam = ['1253','1263','1351','1356','1364','1369','1390','1403']

import os
# Reading all resting state file for 
rest_filesMid = ['/media/Data/KPE_fmriPrep_preproc/kpeOutput/fmriprep/sub-%s/ses-2/func/sub-%s_ses-2_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz' % (sub,sub) for sub in subListMidazolam]
# gather confound files
confound_filesMid = ['/media/Data/KPE_fmriPrep_preproc/kpeOutput/fmriprep/sub-%s/ses-2/func/sub-%s_ses-2_task-rest_desc-confounds_regressors.tsv' % (sub,sub) for sub in subListMidazolam]

#%% dictionary learning
from nilearn.decomposition import DictLearning
# Initialize DictLearning object
dict_learn = DictLearning(n_components=20,
                          smoothing_fwhm=6.,
                          random_state=0,
                          memory = "/media/Data/nilearn",
                          verbose=1, memory_level=2)

dict_learn.fit(rest_filesMid)

components_img = dict_learn.components_img_
#%% Extraction 
from nilearn.regions import RegionExtractor

extractor = RegionExtractor(dict_learn.components_img_, threshold=0.2,
                            thresholding_strategy='ratio_n_voxels',
                            extractor='local_regions', verbose=1,
                            standardize=True, min_region_size=1350)
extractor.fit()

correlations = []
for filename, confound in zip(rest_filesMid, confound_filesMid):
    
    confoundClean = removeVars(confound)
   # confoundClean.to_csv('nilearn/confound.csv', sep = '\t', index = False)
    confoundArray = confoundClean.values
    timeseries_each_subject = extractor.transform(filename, confounds=confoundArray)
    
    correlation = connectome_measure.fit_transform([timeseries_each_subject])
    
    correlations.append(correlation)

# Get array in good numpy structure
correlations = np.squeeze(correlations)
# Computing the mean correlation matrix
mean_correlations = np.mean(correlations, axis=0)

title = 'Correlation between %d regions' % n_regions_extracted
plotting.plot_matrix(mean_correlations, vmax=1, vmin=-1, colorbar=True,
                     labels=['IC %0d' % i for i in range(n_regions_extracted)],
                     title=title, reorder=True)
# Find the center of the regions with find_xyz_cut_coords
coords_connectome = [plotting.find_xyz_cut_coords(img)
                     for img in image.iter_img(extractor.regions_img_)]

# Plot the functional connectome on the glass brain
plotting.plot_connectome(mean_correlations, coords_connectome,
                         edge_threshold='99%', title=title)
