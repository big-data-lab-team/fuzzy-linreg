#!/usr/bin/env python

import os
import glob
import json
import argparse
import sys

def find_t1s(base):
#   regexp = os.path.join(base, 'sub-*', 'ses-*', 'anat', '*_T1w.nii.gz')
  regexp = os.path.join(base, '*.nii.gz')
  t1s = glob.glob(regexp)
  return t1s

def extract_fields(t1_path):
  base = t1_path.split('/OAS')[0]
  t1 = t1_path.split('/')[-1].split('.')[0]

#   base, t1 = t1_path.split(os.sep)
  return {
    'base': base,
    't1': t1,
    'full_path': t1_path}

def extract_sessions(t1_paths):
  subject_t1_map = {}
  for t1 in t1_paths:
    fields = extract_fields(t1)

    subject_t1_map[fields['t1']] = fields['full_path']
    
    # subject = fields['subject']
    # session = fields['session']
    # if session == 'ses-1':
    #   subject_t1_map[subject] = subject_t1_map.get(subject, {})
    #   subject_t1_map[subject]['session-1'] = t1
    # elif session == 'ses-2':
    #   subject_t1_map[subject] = subject_t1_map.get(subject, {})
    #   subject_t1_map[subject]['session-2'] = t1
    
  return subject_t1_map

def create_flirt_invocation(subject, subject_t1_map, output_directory="", dofs=12):
  in_file = subject_t1_map[subject]
#   reference = subject_t1_map[subject]['session-2']
  out_file = os.path.join(output_directory, f'{subject}.nii.gz')
  out_mat_file = os.path.join(output_directory, f'{subject}.mat')

  invocation = {
    'in_file': in_file,
    'reference': '/home/ine5/scratch/creatis_fsl_flirt/MNI152_T1_1mm.nii.gz',
    'out_filename': out_file,
    'out_mat_filename': out_mat_file
  }
  return invocation


def write_invocation(invocation, output_dir, output_file, dry_run=False):
  output_path = os.path.join(output_dir, output_file)
  if dry_run:
    print(f"\nwrite invocation in {output_path}")
    json.dump(invocation, sys.stdout, indent=4)
    return
  with open(output_path, 'w') as outfile:
    json.dump(invocation, outfile, indent=4)


def create_ieee_invocations(subject_t1_map, invocations_directory, results_directory, dry_run=False, dofs=12):
  ieee_results_dir = os.path.join(results_directory, f'anat-{dofs}dofs', 'ieee')
  ieee_invocations_dir = os.path.join(invocations_directory, f'anat-{dofs}dofs', 'ieee')
  if dry_run:
    print(f'\ncreate ieee invocations in {ieee_results_dir}')
  else:
    os.makedirs(ieee_results_dir, exist_ok=True)

  for subject in subject_t1_map.keys():
    invocation = create_flirt_invocation(subject, subject_t1_map, output_directory=ieee_results_dir, dofs=12)
    write_invocation(invocation, ieee_invocations_dir, f'{subject}.json', dry_run=dry_run)


def create_mca_invocations(subject_t1_map, invocations_directory, results_directory, repetitions, dry_run=False, dofs=12):

  for i in range(1, repetitions + 1):
    mca_results_dir = os.path.join(results_directory, f'anat-{dofs}dofs', 'mca', str(i))
    mca_invocations_dir = os.path.join(invocations_directory, f'anat-{dofs}dofs', 'mca', str(i))
    if dry_run:
      print(f'\ncreate mca invocations in {mca_results_dir}')
    else:
      os.makedirs(mca_results_dir, exist_ok=True)
    for subject in subject_t1_map.keys():
      invocation = create_flirt_invocation(subject, subject_t1_map, output_directory=mca_results_dir, dofs=dofs)
      write_invocation(invocation, mca_invocations_dir, f'{subject}.json', dry_run=dry_run)

def create_flirt_invocations(subject_t1_map, args):
  for dofs in [12]:
    create_ieee_invocations(subject_t1_map, args.invocations_directory, args.output_directory, args.dry_run, dofs=dofs)
    create_mca_invocations(subject_t1_map,  args.invocations_directory, args.output_directory, args.mca_repetitions, args.dry_run, dofs=dofs)

def parse_args():
  parser = argparse.ArgumentParser(description='Create invocations for IEEE and MCA')
  parser.add_argument('--base', type=str, default='CORR', help='Base directory')
  parser.add_argument('--invocations-directory', type=str, default='invocations', help='Invocations directory')
  parser.add_argument('--output-directory', type=str, default='results', help='Results directory')
  parser.add_argument('--mca-repetitions', type=int, default=10, help='Number of repetitions for MCA')
  parser.add_argument('--dry-run', action='store_true', help='Dry run')
  return parser.parse_args()

def main():
  args = parse_args()
  t1s = find_t1s(args.base)
#   print(t1s)
  subject_t1_map = extract_sessions(t1s)
#   print(subject_t1_map)

#   if args.dry_run:    
#     for subject, sessions in subject_t1_map.items():
#       for session, t1 in sessions.items():
#         print(f'{subject} {session} {t1}')

  create_flirt_invocations(subject_t1_map, args)
  

if '__main__' == __name__:
  main()
  