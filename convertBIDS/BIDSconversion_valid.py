#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue June 23 2026
@author: Nachshon Korem
Based on the script by Or Duek
Convert dicom to bids
"""

import os, re, shutil, json, subprocess
from pathlib import Path
from nipype.interfaces.dcm2nii import Dcm2niix

# =============================================================================
# USER CONFIGURATION
# Edit the variables below before running the script.
# =============================================================================

# 1. Output Directory for the BIDS dataset
BIDS_ROOT = '/home/nachshon/Documents/PSUB2/'

# 2. Dataset Metadata (used to generate dataset_description.json)
DATASET_DESC = {
    "Name": "Project name",
    "BIDSVersion": "1.9.0",
    "DatasetType": "raw",
    "License": "CC0",
    "Authors": ["Nachshon Korem and I"],
    "Acknowledgements": "Yale University / Reichman University",
    "HowToAcknowledge": "Please cite the authors and acknowledge the funding source.",
    "Funding": [""],
    "ReferencesAndLinks": [""],
    "DatasetDOI": ""
}

# 3. Generic Task Template 
# This will be generated as a single file in the BIDS root (e.g., task-<name>_bold.json)
# to take advantage of BIDS inheritance. TaskName will be auto-filled by the script.
TASK_TEMPLATE = {
    "RepetitionTime": 1,
    "TaskName": "", 
    "TaskDescription": "please enter task description here",
    "Instructions": "What was the subject told to do?.",
    "TrialStructure": {
        "BlocksPerSession": 1,
        "TrialsPerBlock": 1,
        "Sessions": 1,
        "CatchTrialsPerBlock": 1
    },
    "BehavioralMeasures": ["proportion of something", "reaction time accuracy?"],
    "Conditions": ["condition1", "condition2", "Catch"]
}

# 4. Subject List and DICOM Paths
sublist = [
    {'subNumber': '1863',
      'sessionDict': {'ses-1': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-1863/sub-1863_day-1',
                      'ses-2': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-1863/sub-1863_day-2',
                      'ses-3': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-1863/sub-1863_day-3',
                      'ses-4': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-1863/sub-1863_day-4',
                      'ses-5': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-1863/sub-1863_day-5',
                      'ses-6': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-1863/sub-1863_day-6'}},
     {'subNumber': '2004',
      'sessionDict': {'ses-1': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2004/sub-2004_day1',
                      'ses-2': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2004/sub-2004_day2',
                      'ses-3': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2004/sub-2004_day3',
                      'ses-4': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2004/sub-2004_day4',
                      'ses-5': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2004/sub-2004_day5',
                      'ses-6': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2004/sub-2004_day6'}},
     {'subNumber': '2067',
      'sessionDict': {'ses-1': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2067/sub-2067_day1',
                      'ses-2': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2067/sub-2067_day2',
                      'ses-3': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2067/sub-2067_day3',
                      'ses-4': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2067/sub-2067_day4',
                      'ses-5': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2067/sub-2067_day5',
                      'ses-6': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2067/sub-2067_day6'}},
     {'subNumber': '2078',
      'sessionDict': {'ses-1': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2078/sub-2078_day1',
                      'ses-2': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2078/sub-2078_day2',
                      'ses-3': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2078/sub-2078_day3',
                      'ses-4': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2078/sub-2078_day4',
                      'ses-5': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2078/sub-2078_day5',
                      'ses-6': '/media/Data/Lab_Projects/PSUB2/neuroimaging/RAWDICOM/sub-2078/sub-2078_day6'}}
]

# =============================================================================
# CORE LOGIC (Do not edit below this line unless modifying pipeline behavior)
# =============================================================================

# ----------------------------
# dcm2niix conversion 
# ----------------------------
def convert(source_dir, output_dir, subName, session):
    os.makedirs(os.path.join(output_dir, subName, session), exist_ok=True)
    converter = Dcm2niix()
    converter.inputs.source_dir = source_dir
    converter.inputs.compression = 7
    converter.inputs.output_dir = os.path.join(output_dir, subName, session)
    converter.inputs.out_filename = subName + '_' + '%2s' + "_" + '%p'
    print(f"[dcm2niix] {subName} {session}: start")
    converter.run()
    print(f"[dcm2niix] {subName} {session}: complete")

# ----------------------------
# helpers
# ----------------------------
TASK_PAT = re.compile(r'_task-([a-z0-9]+)(?:_run-\d+)?_bold$', re.I)

def _split_baseext(fname):
    """Return (base, ext) where ext can be '.nii.gz'."""
    base, ext = os.path.splitext(fname)
    if ext == '.gz' and base.endswith('.nii'):
        return base[:-4], '.nii.gz'
    return base, ext

def _task_from_stem(stem: str) -> str:
    """
    Task from either:
      - BIDS-style:  ..._task-<task>[_run-#]_bold
      - dcm2niix:    ...bold_<task>([_...])
    Returns lowercase alnum token (first token if underscores).
    """
    s = stem.lower()
    if 'rest' in s:
        return 'rest'
    m = TASK_PAT.search(s)
    if m:
        return m.group(1)
    if 'bold_' in s:
        raw = s.split('bold_', 1)[1]
        raw = re.sub(r'[^a-z0-9]+', '', raw)
        return (raw or 'unknown')
    return 'unknown'

def _log(fullPath, old_path, new_path):
    logf = os.path.join(fullPath, 'rename_log.txt')
    with open(logf, 'a', encoding='utf-8') as fh:
        fh.write(f"{os.path.basename(old_path)} >> {os.path.basename(new_path)}\n")

# ----------------------------
# BOLD: move → sort → rename with run-#, never overwrite; keep pairs in sync
# ----------------------------
def rename_bold_simple(fullPath: str, subName: str, session: str):
    func_dir = os.path.join(fullPath, 'func')
    os.makedirs(func_dir, exist_ok=True)
    
    tasks_found = set()

    # 1) move all bold from root to func
    for f in sorted(os.listdir(fullPath)):
        src = os.path.join(fullPath, f)
        if os.path.isfile(src) and ('bold' in f.lower()):
            shutil.move(src, os.path.join(func_dir, f))

    # 2) collect stems (nii/nii.gz/json)
    stems = {}
    for f in os.listdir(func_dir):
        p = os.path.join(func_dir, f)
        if not os.path.isfile(p):
            continue
        if not (f.endswith('.nii') or f.endswith('.nii.gz') or f.endswith('.json')):
            continue
        if 'bold' not in f.lower():
            continue
        base, ext = _split_baseext(f)
        stems.setdefault(base, {})[ext] = p

    # 3) sort by base name; rename sequentially
    for base in sorted(stems.keys()):
        stem = os.path.basename(base)
        task = _task_from_stem(stem)
        
        if task != 'unknown':
            tasks_found.add(task)

        # choose first free run index across all sidecars
        run = 1
        while True:
            target_base = f"{subName}_{session}_task-{task}_run-{run}_bold"
            exists = any(os.path.exists(os.path.join(func_dir, target_base + ext))
                         for ext in stems[base].keys())
            if not exists:
                break
            run += 1

        # stage to temps then finalize
        tmp_map = {}
        for ext, src in stems[base].items():
            tmp = os.path.join(func_dir, f".tmp_{os.path.basename(base)}{ext}")
            os.rename(src, tmp)
            tmp_map[ext] = tmp

        for ext, tmp in tmp_map.items():
            dst = os.path.join(func_dir, f"{target_base}{ext}")
            os.rename(tmp, dst)
            _log(fullPath, tmp.replace(func_dir+os.sep, ''), dst)
            
    return tasks_found

# ----------------------------
# DWI/DTI: move → sort → rename to run-1/run-2..., keep pairs (.nii/.json/.bval/.bvec)
# ----------------------------
def rename_dwi_simple(fullPath: str, subName: str, session: str):
    dwi_dir = os.path.join(fullPath, 'dwi')
    os.makedirs(dwi_dir, exist_ok=True)

    # move all dwi/dti from root to dwi
    for f in sorted(os.listdir(fullPath)):
        src = os.path.join(fullPath, f)
        if os.path.isfile(src) and (('diff' in f.lower()) or ('dti' in f.lower())):
            shutil.move(src, os.path.join(dwi_dir, f))

    # collect stems including bval/bvec/json
    stems = {}
    for f in os.listdir(dwi_dir):
        p = os.path.join(dwi_dir, f)
        if not os.path.isfile(p):
            continue
        base, ext = _split_baseext(f)
        if ext not in {'.nii', '.nii.gz', '.json', '.bval', '.bvec'}:
            continue
        stems.setdefault(base, {})[ext] = p

    # sort by base name; always assign run-#
    for base in sorted(stems.keys()):
        run = 1
        while True:
            target_base = f"{subName}_{session}_run-{run}_dwi"
            exists = any(os.path.exists(os.path.join(dwi_dir, target_base + ext))
                         for ext in stems[base].keys())
            if not exists:
                break
            run += 1

        # stage → finalize
        tmp_map = {}
        for ext, src in stems[base].items():
            tmp = os.path.join(dwi_dir, f".tmp_{os.path.basename(base)}{ext}")
            os.rename(src, tmp)
            tmp_map[ext] = tmp

        for ext, tmp in tmp_map.items():
            dst = os.path.join(dwi_dir, f"{target_base}{ext}")
            os.rename(tmp, dst)
            _log(fullPath, tmp.replace(dwi_dir+os.sep, ''), dst)

# ----------------------------
# ANAT 
# ----------------------------
def handle_anat(fullPath, subName, session):
    entries = sorted(next(os.walk(fullPath))[2])
    for n in entries:
        if ('MPRAGE' in n) or ('t1_flash' in n) or ('t1_fl2d' in n) or ('GRE_3D_Sag_Spoiled' in n):
            print(f"[anat] {n}")
            src = os.path.join(fullPath, n)
            anat_dir = os.path.join(fullPath, 'anat')
            os.makedirs(anat_dir, exist_ok=True)
            dst = os.path.join(anat_dir, n)
            shutil.move(src, dst)
            ext = _split_baseext(n)[1]
            if 'MPRAGE' in n:
                newname = f"{subName}_{session}_acq-mprage_T1w{ext}"
            elif 't1_flash' in n:
                newname = f"{subName}_{session}_acq-flash_T1w{ext}"
            elif 't1_fl2d' in n:
                newname = f"{subName}_{session}_acq-fl2d1_T1w{ext}"
            else:
                newname = f"{subName}_{session}_acq-gre_spoiled_T1w{ext}"
            final = os.path.join(anat_dir, newname)
            os.rename(dst, final)
            _log(fullPath, n, final)

# ----------------------------
# organizer
# ----------------------------
def organizeFiles(output_dir, subName, session):
    fullPath = os.path.join(output_dir, subName, session)
    os.makedirs(os.path.join(fullPath, 'dwi'),  exist_ok=True)
    os.makedirs(os.path.join(fullPath, 'anat'), exist_ok=True)
    os.makedirs(os.path.join(fullPath, 'func'), exist_ok=True)
    os.makedirs(os.path.join(fullPath, 'misc'), exist_ok=True)

    # clear/create log
    open(os.path.join(fullPath, 'rename_log.txt'), 'w').close()

    # 1) ANAT
    handle_anat(fullPath, subName, session)

    # 2) DWI/DTI → run-#
    rename_dwi_simple(fullPath, subName, session)

    # 3) BOLD → run-# (returns tasks found)
    tasks_found = rename_bold_simple(fullPath, subName, session)

    # 4) everything else → misc
    for f in sorted(next(os.walk(fullPath))[2]):
        src = os.path.join(fullPath, f)
        if os.path.isfile(src):
            dst = os.path.join(fullPath, 'misc', f)
            if not os.path.exists(dst):
                shutil.move(src, dst)
            else:
                print(f"[warning] {f} already exists in misc. Skipping.")
                
    return tasks_found

# ----------------------------
# driver
# ----------------------------
def fullBids(subNumber, sessionDict):
    subName = 'sub-' + subNumber
    all_session_tasks = set()
    
    for session, source_dir in sessionDict.items():
        if not os.path.isdir(source_dir):
            print(f"[skip] {subName} {session}: Source directory not found ({source_dir})")
            continue
        
        print(f"[run] {subName} {session} from {source_dir}")
        convert(source_dir, BIDS_ROOT, subName, session)
        tasks = organizeFiles(BIDS_ROOT, subName, session)
        all_session_tasks.update(tasks)
        
    return all_session_tasks

# ----------------------------
# Final Cleanup & Validation
# ----------------------------
def generate_root_bids_files(processed_subs, discovered_tasks):
    """
    Creates dataset_description.json, participants.tsv, .bidsignore, README, CHANGES,
    and root-level task JSONs for BIDS inheritance.
    """
    os.makedirs(BIDS_ROOT, exist_ok=True)
    
    # 1. dataset_description.json 
    desc_path = os.path.join(BIDS_ROOT, 'dataset_description.json')
    if not os.path.exists(desc_path):
        with open(desc_path, 'w', encoding='utf-8') as f:
            json.dump(DATASET_DESC, f, indent=4)
        print("[metadata] Created dataset_description.json")

    # 2. .bidsignore 
    ignore_path = os.path.join(BIDS_ROOT, '.bidsignore')
    if not os.path.exists(ignore_path):
        with open(ignore_path, 'w', encoding='utf-8') as f:
            f.write("**/misc/\n**/rename_log.txt\n")
        print("[metadata] Created .bidsignore")

    # 3. README and CHANGES
    readme_path = os.path.join(BIDS_ROOT, 'README')
    if not os.path.exists(readme_path):
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"{DATASET_DESC['Name']}\n===================\n\nRaw DICOMs converted to BIDS via dcm2niix.")
    
    changes_path = os.path.join(BIDS_ROOT, 'CHANGES')
    if not os.path.exists(changes_path):
        with open(changes_path, 'w', encoding='utf-8') as f:
            f.write("1.0.0\n - Initial release.")

    # 4. participants.tsv
    if processed_subs:
        tsv_path = os.path.join(BIDS_ROOT, 'participants.tsv')
        existing_subs = set()
        
        if os.path.exists(tsv_path):
            with open(tsv_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if parts:
                        existing_subs.add(parts[0])
        else:
            with open(tsv_path, 'w', encoding='utf-8') as f:
                f.write("participant_id\n")

        with open(tsv_path, 'a', encoding='utf-8') as f:
            for sub in sorted(processed_subs):
                sub_id = f"sub-{sub}"
                if sub_id not in existing_subs:
                    f.write(f"{sub_id}\n")
                    
    # 5. Generate missing root task JSONs based on the global TASK_TEMPLATE
    for task in discovered_tasks:
        json_path = os.path.join(BIDS_ROOT, f"task-{task}_bold.json")
        if not os.path.exists(json_path):
            # Create a localized copy of the template and update the name
            task_metadata = TASK_TEMPLATE.copy()
            task_metadata["TaskName"] = task
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(task_metadata, f, indent=4)
            print(f"[metadata] Created {os.path.basename(json_path)}")

def run_bids_validator():
    """
    Attempts to run the node-based bids-validator via command line.
    """
    print("\n[validator] Running BIDS Validator...")
    try:
        result = subprocess.run(['bids-validator', BIDS_ROOT], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print("[validator] SUCCESS: BIDS validation passed with no errors.")
        else:
            print("[validator] WARNING: BIDS validation found issues. Check output above.")
            
    except FileNotFoundError:
        print("[validator] SKIPPED: 'bids-validator' command not found on system.")
        print(" -> To enable this, install Node.js and run: npm install -g bids-validator")

# ----------------------------
# Main Execution
# ----------------------------
if __name__ == "__main__":
    import concurrent.futures
    max_workers = min(len(sublist) if sublist else 1, 3) 

    def _run_one(sub):
        try:
            tasks = fullBids(sub['subNumber'], sub['sessionDict'])
            return (sub['subNumber'], "ok", tasks)
        except Exception as e:
            return (sub['subNumber'], f"error: {e}", set())

    if sublist:
        successfully_processed_subs = set()
        global_tasks = set()
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as ex:
            futures = [ex.submit(_run_one, sub) for sub in sublist]
            for fut in concurrent.futures.as_completed(futures):
                subnum, status, tasks = fut.result()
                print(f"[done] {subnum}: {status}")
                if status == "ok":
                    successfully_processed_subs.add(subnum)
                    global_tasks.update(tasks)
        
        print("\n[metadata] Writing root BIDS files...")
        generate_root_bids_files(successfully_processed_subs, global_tasks)
        print("[metadata] Complete.")
        
        run_bids_validator()
        
    else:
        print("sublist is empty; add subjects to the User Configuration section and rerun.")