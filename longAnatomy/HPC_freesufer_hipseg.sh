#!/bin/bash

#SBATCH --job-name=FS_hip
#SBATCH -o %x-%A-%a.out
#SBATCH -e %x-%A-%a.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8G
#SBATCH --time=4:00:00
#SBATCH --mail-type=ALL
#SBATCH --array=1-26

#load and activate FreeSurfer
module load FreeSurfer/7.1.0-centos7_x86_64
source $FREESURFER_HOME/SetUpFreeSurfer.sh
export SUBJECTS_DIR=/gpfs/gibbs/pi/levy_ifat/Nachshon/KPE/freesurfer7.1 # adjust to location of your data
cd $SUBJECTS_DIR

# subject list make sure the array = 1-number of subjects

SUBJ=(008 1223 1253 1293 1307 1315 1322 1339 1343 1351 1356 1364 1369 1387 1390 1403 1419 1464 1468 1480 1499 1561 1573 1578 1587 1612)

# If you need to rerun the script run this line as well
#rm /gpfs/gibbs/pi/levy_ifat/Nachshon/KPE/freesurfer7.1/${SUBJ[$SLURM_ARRAY_TASK_ID-1]}/scripts/IsRunningLongHPsub.lh+rh

# runs once on the base dir and creates outputs in each of the long folders.
segmentHA_T1_long.sh ${SUBJ[$SLURM_ARRAY_TASK_ID-1]}