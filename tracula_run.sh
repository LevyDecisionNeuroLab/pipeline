#!/bin/bash

#SBATCH --job-name=Tracula_trial
#SBATCH --output=Tracula_run_batch.txt
#SBATCH --error=Tracula_run_error.log
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4G
#SBATCH --time=15:00:00
#SBATCH --mail-type=ALL
# #SBATCH --mail-user=nachshon.korem@yale.edu
#SBATCH --array=0-2

# load and activate FreeSurfer and FSL
module load FreeSurfer/6.0.0-centos6_x86_64
module load FSL/6.0.1-centos7_64
. /gpfs/ysm/apps/software/FSL/6.0.1-centos7_64/etc/fslconf/fsl.sh
source $FREESURFER_HOME/SetUpFreeSurfer.sh
export SUBJECTS_DIR=/home/nk549/project/DTI # home folder on the HPC
export RECONS=$SUBJECTS_DIR/recons  # where to find recon-all output
export DTROOT=$SUBJECTS_DIR/diffusion #output folder
cd $SUBJECTS_DIR

# subject list make sure the array equals 0-number of subject-1
SUBJ=(sub-3 sub-008 sub-30)

# runs all 3 tracula processes one after the other
trac-all -prep -c $DTROOT/${SUBJ[$SLURM_ARRAY_TASK_ID-1]}/configfile/dmrirc.conf && trac-all -bedp -c $DTROOT/${SUBJ[$SLURM_ARRAY_TASK_ID-1]}/configfile/dmrirc.conf && trac-all -path -c $DTROOT/${SUBJ[$SLURM_ARRAY_TASK_ID-1]}/configfile/dmrirc.conf
