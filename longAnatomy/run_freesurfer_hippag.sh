#!/bin/bash
#SBATCH --partition=general
#SBATCH -J KPE_ses23
#SBATCH --output=KPE13.txt
#SBATCH --error=KPE13.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=13 # this number should correspond to "n_procs" in reconAll.py
#SBATCH --mem-per-cpu=8G
#SBATCH -t 16:00:00 # adjust to have 8 hours per subject (you can calculate number of roundup(subs/n_cpus) * 8)
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nachshon.korem@yale.edu # change to yours


echo "Running script"

module load miniconda
module load FreeSurfer/7.1.0-centos7_x86_64 #make sure this is the version you want

source activate fmri # make sure you have a conda env with all the python modules installed.

python /home/nk549/Documents/KPE/reconAll.py > log_kpe.log # adjust location of the python script. the ">" creates a log file
