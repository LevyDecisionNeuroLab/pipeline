#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 09:31:04 2019

@author: or
"""

from nilearn import datasets

from nilearn import plotting
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from nilearn import image


dataset = datasets.fetch_atlas_harvard_oxford('cort-maxprob-thr25-2mm')
atlas_filename = dataset.maps
labels = dataset.labels

print('Atlas ROIs are located in nifti image (4D) at: %s' %
      atlas_filename)  # 4D data

# One subject of resting-state data
data = datasets.fetch_adhd(n_subjects=1)
fmri_filenames = data.func[0]



from nilearn.input_data import NiftiLabelsMasker
masker = NiftiLabelsMasker(labels_img=atlas_filename, standardize=True,
                           memory='nilearn_cache', verbose=5)

# Here we go from nifti files to the signal time series in a numpy
# array. Note how we give confounds to be regressed out during signal
# extraction
time_series = masker.fit_transform(fmri_filenames, confounds=data.confounds)

time_series.shape

from nilearn.connectome import ConnectivityMeasure
correlation_measure = ConnectivityMeasure(kind='correlation', vectorize = True)
correlation_matrix = correlation_measure.fit_transform([time_series])[0]

# Mask the main diagonal for visualization:
np.fill_diagonal(correlation_matrix, 0)

# Plot correlation matrix - note: matrix is ordered for block-like representation
plotting.plot_matrix(correlation_matrix, figure=(10, 8), labels=labels,
                     vmax=0.8, vmin=-0.8, reorder=True);
                     

#%% Try with one kpe subject
kpe_file = '/media/Data/KPE_fmriPrep_preproc/kpeOutput/fmriprep/sub-1223/ses-1/func/sub-1223_ses-1_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'
confound_file = '/home/or/nilearn_data/kpe1223conf.csv'
timeKpe = masker.fit_transform(kpe_file, confounds = confound_file)


correlation_matrix1223 = correlation_measure.fit_transform([timeKpe])[0]

# Mask the main diagonal for visualization:
np.fill_diagonal(correlation_matrix1223, 0)

# Plot correlation matrix - note: matrix is ordered for block-like representation
plotting.plot_matrix(correlation_matrix1223, figure=(10, 8), labels=labels,
                     vmax=0.8, vmin=-0.8, reorder=True);

#%% 
msdl = datasets.fetch_atlas_msdl("msdl_rois")
msdl_atlas = msdl.maps
# Extract only default mode network nodes
dmn_nodes = image.index_img(msdl_atlas, [3, 4, 5, 6])

plotting.plot_prob_atlas(dmn_nodes, cut_coords=(0, -60, 29), draw_cross=False,
                         annotate=False, title="DMN nodes in MSDL atlas")
#%%
from nilearn.input_data import NiftiMapsMasker
masker = NiftiMapsMasker(maps_img=msdl_atlas, standardize=True, verbose=1,
                         memory="nilearn_cache", memory_level=2)

# Extract the signal from the regions
timeKpe = masker.fit_transform(kpe_file, confounds=confound_file)

# Compute the correlation matrix
correlation_matrix1223= correlation_measure.fit_transform([timeKpe])[0]
#%% read labels and coordinations to build a connectome graph
labels = msdl.labels
coords  = msdl.region_coords
# Mask the main diagonal for visualization
np.fill_diagonal(correlation_matrix1223, 0)
plotting.plot_connectome(correlation_matrix1223, coords, edge_threshold="80%",
                         colorbar=True)

plotting.view_connectome(correlation_matrix, coords, threshold="80%", cmap='bwr',
                         symmetric_cmap=False, linewidth=6.0, marker_size=3.0)