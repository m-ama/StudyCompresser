#----------------------------------------------------------------------
# Package Management
#----------------------------------------------------------------------

import os
import os.path as op
import textwrap
import argparse
import pandas as pd

#----------------------------------------------------------------------
# Parse Arguments
#----------------------------------------------------------------------
# Initialize ArgumentParser
parser = argparse.ArgumentParser(
        prog='studycompressor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''\
Appendix
--------

                                '''))

# Specify parser arguments
# Mandatory
parser.add_argument('input',
                    help='directory path to compress',
                    type=str)

parser.add_argument('output',
                    help='directory to output compressed chunks',
                    type=str)

# Optional
parser.add_argument('-n', '--name',
                    help='name to give to compressed outputs',
                    type=str)
parser.add_argument('-s', '--size',
                    help='file size of each chunk',
                    default='10G',
                    type=str)

# Process arguments
args = parser.parse_args()

#----------------------------------------------------------------------
# Validate Arguments
#----------------------------------------------------------------------

if not op.isdir(input):
    raise NotADirectoryError('Specified input directory not found. '
                             'Please ensure  that the directory {} '
                             'exists.'.format(input))

if not op.isdir(output):
    raise NotADirectoryError('Specified output directory not found. '
                             'Please ensure  that the directory {} '
                             'exists.'.format(input))

if not args.size[-1].isalpha():
    raise Exception('Please specify a size multiple. Specify either "M" '
                    'or "G".')


if not any(x in size[-1] for x in ['M', 'G']):
    raise Exception('Invalid file size multiple. Please use either "M" '
                    'for megabytes and "G" for gigabytes')

