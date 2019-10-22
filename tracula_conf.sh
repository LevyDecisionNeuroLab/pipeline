#!/bin/bash

#SBATCH --job-name=Tracula_trial
#SBATCH --output=Tracula_conf_batch.txt
#SBATCH --error=Tracula_conf_error.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1G
#SBATCH --time=00:05:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nachshon.korem@yale.edu
#SBATCH --array=0-2

# load FreeSurfer and activate
module load FreeSurfer/6.0.0-centos6_x86_64
source $FREESURFER_HOME/SetUpFreeSurfer.sh
export SUBJECTS_DIR=/home/nk549/project/DTI # change this to fit your dataset home
export RECONS=$SUBJECTS_DIR/recons # where to find the FreeSurfer recons
export DTROOT=$SUBJECTS_DIR/diffusion # output folder for tracula
cd $SUBJECTS_DIR

# subject list make sure array = 0-number of subject-1
# this will run 3 subjects in prallel
SUBJ=(sub-3 sub-008 sub-30)

# create config file and folder
config=$DTROOT/${SUBJ[$SLURM_ARRAY_TASK_ID-1]}/configfile/dmrirc.conf
mkdir -p $DTROOT/${SUBJ[$SLURM_ARRAY_TASK_ID-1]}/configfile/

# write to config file tracula configurations
> $config
echo "setenv SUBJECTS_DIR $RECONS" >> $config # where to find recon-all
echo "set dtroot = $DTROOT" >> $config  # output folder
echo "set subjlist = (${SUBJ[$SLURM_ARRAY_TASK_ID-1]})" >> $config # only 1 subject
echo "set dcmlist = ($SUBJECTS_DIR/Rounan/${SUBJ[$SLURM_ARRAY_TASK_ID-1]}/dwi/${SUBJ[$SLURM_ARRAY_TASK_ID-1]}_dwi.nii.gz)" >> $config # where to find the nii.gz/dcm file
echo "set bvecfile = ($SUBJECTS_DIR/Rounan/${SUBJ[$SLURM_ARRAY_TASK_ID-1]}/dwi/${SUBJ[$SLURM_ARRAY_TASK_ID-1]}_dwi.bvec)" >> $config # if not using DCM must add bvec and bval
echo "set bvalfile = ($SUBJECTS_DIR/Rounan/${SUBJ[$SLURM_ARRAY_TASK_ID-1]}/dwi/${SUBJ[$SLURM_ARRAY_TASK_ID-1]}_dwi.bval)" >> $config

# you can enter more configurations like do not use eddy currents here.
