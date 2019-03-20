#!/bin/bash
#SBATCH --partition=general
#SBATCH --job-name=fmriPrepKPE008
#SBATCH --ntasks=1 --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8000
#SBATCH --time=12:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=or.duek@yale.edu


echo "Running script"

singularity run --cleanenv /project/ysm/levy_ifat/fmriPrep/fmriprep-latest.simg \
/home/oad4/scratch60/kpeBIDS/kpe_forFmriPrep /home/oad4/scratch60/kpeOutput \
participant \
--skip_bids_validation \
--fs-license-file /home/oad4/freesurferLicense/license.txt \
-w /home/oad4/scratch60/work \
--nthreads 8 \
--ignore slicetiming \
--participant_label 008




