<h1>Longitudinal anatomy analysis using freesurfer on the HPC</h1>


1. Organize all anatomical data in a bids compatible way
2. Run recon-all on all participants
    1. adjust the python code (reconAll.py)
        1. Make sure you have a conda env with all the needed libraries
        2. Adjust the code based on your experiment
            1. Anatomical location
            2. Subjects number
            3. Adjust output dir 
            4. Make sure not to overwrite your files (recon-all each session to its own directory)
    2. Adjust the Run the run_freesurfer_hippag.sh script </br>
    3. Add suffix of the session number to the directory 
        2. Subject 1000 session 1 should turn to sub-1000_ses-1</br>
            1. You can do that from the terminal using the following commands:</br>
            2. cd to the output directory of the reconAll.py code</br>
            3. In the terminal write:</br>
            4. $ find . -maxdepth 1 -type d ! -name '.' | while read -r subdir; do   new_name="${subdir}_ses-2";   mv "$subdir" "$new_name"; done
            5. Change to ses-2 and repeat
    3. move all anatomical folders to the same folder</br></br>

3. Create a subject specific template </br>
    1. Run the base script: HPC_freesurfer_base.sh</br>
        1. Adjust the subjects folder</br>
        2. In the array adjust how many subjects: 1-?</br>
        3. Insert subjects numbers in SUBJ=()</br>
        4. Adjust the base command</br>
            1. recon-all -base &lt;output folder name> -tp &lt;session 1 folder> -tp &lt;session 2 folder> -tp &lt;3> -tp &lt;4> -all</br></br>
            
4. Adjust the anatomical data based on the template</br>
    1. Run the long script HPC_freesurfer_long.sh</br>
        1. Adjust the subjects folder</br>
        2. In the array adjust how many subjects: 1-?</br>
        3. Insert subjects numbers in SUBJ=()</br>
        4. Adjust the long command</br>
            1. recon-all -long &lt;folder to adjust> &lt;template folder> -all</br>
    2. This script runs separately for each session</br></br>
    
5. Create sub regions of the hippocampus and the amygdala</br>
    1. Run the HPC_freesurfer_hipseg.sh script</br>
        1. Adjust the subjects folder</br>
        2. In the array adjust how many subjects: 1-?</br>
        3. Insert subjects numbers in SUBJ=()</br>
        4. Adjust the segmentHA_T1_long command</br>
        5. Point to the template dir and it will run separately on each longitudinal folder separately.</br>
        6. Results will be in the each long folder in the mri subfolder</br></br>
        
6. Run the quantifyHAsubregions.sh script (part of the freesurfer package)</br>
    1. quantifyHAsubregions.sh &lt;prefix> &lt;suffix> &lt;output file> &lt;subfolder></br>
        1. Prefix is either for hippocampus or amygdala</br>
            1. hippoSf </br>
            2. amygNuc </br>
        2. Suffix will be the session name</br>
            1. If the file name is lh.amygNucVolumes-T1.long.v21.txt</br>
            2. T1.long will be the suffix</br>
    2. Needs to be run once for the amygdala and once for the hippocampus outputs both left and right hemisphere </br>
    3. Once you run the export command at the beginning no need to specify it again in the script</br></br></br>


helpful links:</br>
https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/LongitudinalTutorial </br>
https://surfer.nmr.mgh.harvard.edu/fswiki/HippocampalSubfieldsAndNucleiOfAmygdala </br>
https://bookdown.org/u0243256/tbicc/freesurfer.html
