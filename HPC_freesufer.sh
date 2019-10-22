#!/bin/bash

#SBATCH --job-name=FreeSurfer_trial
#SBATCH --output=FreeSurfer_batch.txt
#SBATCH --error=FreeSurfer_error.log
#SBATCH --ntasks=3
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=3G
#SBATCH --time=12:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nachshon.korem@yale.edu
#SBATCH --array=0-2

#load and activate FreeSurfer
module load FreeSurfer/6.0.0-centos6_x86_64
source $FREESURFER_HOME/SetUpFreeSurfer.sh
export SUBJECTS_DIR=/home/nk549/project/DTI/ # FreeSurfer home on the HPC
cd $SUBJECTS_DIR

# subject list make sure the array = 0-number of subjects
SUBJ=(008 030 003)

# make sure to change folder locations according to your project
recon-all -all -s sub-${SUBJ[$SLURM_ARRAY_TASK_ID-1]} -i $SUBJECTS_DIR/bids/sub-${SUBJ[$SLURM_ARRAY_TASK_ID-1]}/anat/sub-${SUBJ[$SLURM_ARRAY_TASK_ID-1]}_T1w.nii.gz
