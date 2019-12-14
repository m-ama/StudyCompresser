#----------------------------------------------------------------------
# Package Management
#----------------------------------------------------------------------

import os
import os.path as op
import textwrap
import argparse
import pandas as pd
import re
import zipfile
from tqdm import tqdm, trange

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
                    default='comprssr_archive',
                    type=str)

parser.add_argument('-s', '--size',
                    help='file size of each chunk',
                    default='2G',
                    type=str)

# Process arguments
args = parser.parse_args()

#----------------------------------------------------------------------
# Validate Arguments
#----------------------------------------------------------------------

if not op.isdir(args.input):
    raise NotADirectoryError('Specified input directory not found. '
                             'Please ensure  that the directory {} '
                             'exists.'.format(input))

if not op.isdir(args.output):
    raise NotADirectoryError('Specified output directory not found. '
                             'Please ensure  that the directory {} '
                             'exists.'.format(input))

if not args.size[-1].isalpha():
    raise Exception('Please specify a size multiple. Specify either '
                    '"M" or "G".')


if not any(x in args.size[-1] for x in ['M', 'G']):
    raise Exception('Invalid file size multiple. Please use either '
                    '"M" for megabytes and "G" for gigabytes')

#----------------------------------------------------------------------
# Declare Variables
#----------------------------------------------------------------------
if 'M' in args.size[-1]:
    bytemul = 1E6
elif 'G' in args.size[-1]:
    bytemul = 1E9
    
size = int(args.size[:-1])
sizeLimit = size * bytemul

#----------------------------------------------------------------------
# Begin Code
#----------------------------------------------------------------------

def compressfile(file):
    """
    Compresses a file into an 
    """
# Init Pandas Dataframe
file_dir = []
file_list = []
file_size = []
for root, dirs, files in os.walk( args.input ):
    file_dir.extend( root for f in files )
    file_list.extend( f for f in files )
    file_size.extend( op.getsize( op.join( root,f ) ) for f in files )

numFiles = len( file_list )
print('Found a total of {} files'.format(numFiles))

output_name = []
i = 0
numCompressed = 1
while i < numFiles:
    print('>> ' + str(i))
    j = 0
    files2compress = []
    while j < sizeLimit:
        # for k in range(len(filesindir)):
        files2compress.append( op.join( file_dir[i],
                                        file_list[i] ) )
        output_name.append( args.name + '.part' + str ( numCompressed ) )
        j += file_size[i]                         
        i += 1
    # print('Zip {}: {} file'.format(numCompressed, len(files2compress)))
    inputs = trange(len(files2compress),
    desc=args.name + '.part' + str ( numCompressed ) + '.zip',
    ncols=70,
    unit='files')
    with zipfile.ZipFile(
        op.join(
            args.output, args.name + '.part' + str ( numCompressed ) + '.zip'),
            'w') as zipMe:        
        for idx in inputs:
            zipMe.write(files2compress[idx], compress_type=zipfile.ZIP_DEFLATED)
    print('    size: {}{}'.format(j/bytemul, args.size[-1]))
    numCompressed += 1
    print(str(i) + '<<')
print(numCompressed)