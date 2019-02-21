#!/bin/bash
#SBATCH --partition=general
#SBATCH --job-name=fmriPrep1346
#SBATCH --ntasks=1 --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8000
#SBATCH --time=12:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=or.duek@yale.edu


echo "Running script"

singularity run --cleanenv /home/oad4/fmriprep/fmriprep-latest.simg \
/home/oad4/scratch60/r_a_ptsd/ /home/oad4/scratch60/output \
participant \
--skip_bids_validation \
--fs-license-file /home/oad4/freesurferLicense/license.txt \
-w /home/oad4/scratch60/work \
--nthreads 24 \
--participant-label 1346

