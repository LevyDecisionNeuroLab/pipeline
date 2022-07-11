#!/bin/bash
#SBATCH --partition=general
#SBATCH -J spm_1st_level # name of your experiment
#SBATCH --output=spm.txt
#SBATCH --error=spm.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4 # should correspond to number of tasks in the python file.
#SBATCH --mem-per-cpu=10G
#SBATCH -t 24:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nachshon.korem@yale.edu # change to your email


echo "Running script"

module load miniconda
module load FSL
module load MATLAB/2021b

source activate aging # change to an enviroment that has nipype installed

. /gpfs/ysm/apps/software/FSL/6.0.4-centos7_64/etc/fslconf/fsl.sh

python /home/nk549/Documents/CB1/SPM_first_level.py > spm.log