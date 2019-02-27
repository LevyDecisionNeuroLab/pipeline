#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 09:37:50 2019

@author: or
"""

```python
from nilearn.plotting import plot_glass_brain
from nilearn.plotting import plot_stat_map
import nilearn.plotting

plot_glass_brain(
    '/media/Data/work/datasink/2ndLevel/_contrast_id_con_0001/spmT_0001.nii', colorbar=True,
     threshold=3.6, display_mode='lyrz', black_bg=True, vmax=11.6);       
        
        
                
nilearn.plotting.plot_glass_brain(nilearn.image.smooth_img('/media/Data/work/datasinkFSL/flameo/_flameo0/zstat1.nii.gz', 6),
                                      display_mode='lyrz', colorbar=True, plot_abs=False, threshold=1, title = "Gain vs. Amb ")
```

