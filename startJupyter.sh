#!/bin/bash
#SBATCH --partition general
#SBATCH --nodes 1
#SBATCH --ntasks-per-node 8
#SBATCH --mem-per-cpu 8G
#SBATCH --time 2-0:00:00
#SBATCH --job-name jupyter-notebook
#SBATCH --output jupyter-notebook-%J.log
#SBATCH --mail-type=ALL
#SBATCH --mail-user=or.duek@yale.edu

# get tunneling info
XDG_RUNTIME_DIR=""
port=$(shuf -i8000-9999 -n1)
node=$(hostname -s)
user=$(whoami)
cluster=$(hostname -f | awk -F"." '{print $2}')

# print tunneling instructions jupyter-log
echo -e "
MacOS or linux terminal command to create your ssh tunnel:
ssh -N -L ${port}:${node}:${port} ${user}@${cluster}.hpc.yale.edu

For more info and how to connect from windows,
   see research.computing.yale.edu/jupyter-nb
Here is the MobaXterm info:

Forwarded port:same as remote port
Remote server: ${node}
Remote port: ${port}
SSH server: ${cluster}.hpc.yale.edu
SSH login: $user
SSH port: 22

Use a Browser on your local machine to go to:
localhost:${port}  (prefix w/ https:// if using password)
"

# load modules or conda environments here
# e.g. farnam:
# module load Python/2.7.13-foss-2016b
module load miniconda &
source activate py37_dev &

# DON'T USE ADDRESS BELOW.
# DO USE TOKEN BELOW
jupyter-notebook --no-browser --port=${port} --ip=${node}
