#!/bin/bash
#SBATCH --job-name=RCF_Twosubs
#SBATCH --output=RCF_twosubs.txt
#SBATCH --error=RCF_twosubs.err
#SBATCH -n 1
#SBATCH --cpus-per-task=12
#SBATCH --mem-per-cpu=4G
#SBATCH --time=16:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=or.duek@yale.edu
#SBATCH --array=1-2

SUBJ=(002 004)
singularity run --cleanenv /project/ysm/levy_ifat/fmriPrep_new/fmriprep-latest.simg \
      /gpfs/ysm/scratch60/oad4/RCF_BidsConversion /gpfs/ysm/scratch60/oad4/RCF_output participant\
      --skip_bids_validation \
      --participant-label ${SUBJ[$SLURM_ARRAY_TASK_ID-1]} --low-mem --stop-on-first-crash \
      -w /gpfs/ysm/scratch60/oad4/work_RCF \
      --medial-surface-nan --use-aroma --cifti-output --notrack \
      --output-space template fsaverage5 --fs-license-file /home/oad4/freesurferLicense/license.txt \
      --omp-nthreads 8 --nthreads 12 --mem_mb 30000




