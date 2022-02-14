
# pipeline
A repository for pipeline scripts - including organizing files, prepossessing and analyses

## Conda environemnt
### Conda - Why?
To run some of the code in this repository certain packages requires installation. 
One way to do that is go one by one - This takes time and also makes the installation applies the whole system in which it is installed. 
A different approach, is to define dedicated environments (e.g. per project; e.g. for the project of running the pipeline). [Conda] (https://docs.conda.io/en/latest/) allows the definition of such independent environments, and the easy installation of packages in that environment. Conda can be installed on a local PC (your computer) and is already installed and ready to use on the HPC.

### Conda - HowTo?
 Simple script to run and operate python 3.7 in anaconda within the Farnam HPC.
#### Load conda 
HPC has a specific version of conda called miniconda. The following command "switches conda on"  (runs the miniconda module):

`module load miniconda &`

#### What environments exist?
Many conda environments may exist on a machine (the ones you define). To learn which environments exist on the current machine run:

`conda info --env`


#### Activate an existing environment
Activating one of the the existing  environments (those listed by _conda info --env_). With this command you "enter" the specified environment (e.g. you can run python commands that use packages installed in the environment.

`source activate [py37_dev]` (replace _py37_dev_ with the name of the environment you wish to activate)

#### Export environment's definition
Say you have an environment ready with all kinds of packages and you want to share it (with a colleague, or with a publication to assist others with running your code). You can list all the requirements of the current environment by running the command:

`conda list`

 And to save it into a file, e.g. one named _requirements.txt_, run the command:

` conda list -e > requirements.txt`


## run jupyter
jupyter notebook &


into conda mode
