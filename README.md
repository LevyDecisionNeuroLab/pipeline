# pipeline
A repository for pipeline scripts - including organizing files, prepossessing and analyses

# simple script to run and operate python 3.7 in anaconda within the Farnam HPC.

module load miniconda &

### if you want to know which enviornments are ther
conda info --env


### activate an enviornment (this env was already created before)
source activate py37_dev (or your name of env)


### run jupyter
jupyter notebook &
