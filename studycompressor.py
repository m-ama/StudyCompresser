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
import hashlib

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
                    default='500M',
                    type=str)
parser.add_argument('-t', '--type',
                    help='output type to write (excel or csv)',
                    default='csv',
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

if 'csv' not in args.type and 'excel' not in args.type:
    raise Exception('Invalid output type choce. Please enter either '
                    ' "csv" or "excel". Otherwise, leave blank.')

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
file_dir = []
file_list = []
file_size = []
for root, dirs, files in os.walk( args.input ):
    file_dir.extend( root for f in files )
    file_list.extend( f for f in files )
    file_size.extend(int(op.getsize(op.join( root,f))) for f in files )
if sizeLimit < min(file_size):
    raise Exception('Compression size {} is lower than the smallest '
                    'file detected ({}{}). Please update compression '
                    'size to accomodate this.'.format(args.size,
                    min(file_size)/bytemul,
                    args.size[-1]))
if sizeLimit < max(file_size):
    raise Exception('It appears that you are attempting to specify '
                    'a compression size smaller than the max file '
                    'size ({}{}). Please update the filesize '
                    'flag.'.format(max(file_size)/bytemul, args.size[-1]))
numFiles = len(file_list)
print('Found a total of {} files'.format(numFiles))

# Compression loop using two while loops
# The parent while loop iterates over all files. The child while loop
# check filesize of compressed archive.
i = 0
zip_name = []
checksum = []
numComp = 0
pbar = tqdm(total=numFiles - 1,
            desc='Compressing',
            ncols=70,
            unit='files')
while i < (numFiles - 1):
    compSize = 0
    zPath = op.join(args.output,
                        args.name + '.part' + str(numComp) + '.zip')
    tqdm.write('Creating {}.part{}.zip'.format(args.name, numComp))
    with zipfile.ZipFile(zPath, 'w') as zipMe:
        while compSize < sizeLimit:
            file2comp = op.join(file_dir[i], file_list[i])
            zipMe.write(file2comp, compress_type=zipfile.ZIP_DEFLATED)
            compSize += op.getsize(zPath)
            zip_name.append(args.name + '.part' + str(numComp) + '.zip')
            checksum.append(hashlib.md5(open(zPath, 'rb').read()).hexdigest())
            i += 1
            pbar.update(1)
            if i == numFiles:
                break
    zipMe.close()
    numComp += 1
file_size = [round(i/bytemul, 2) for i in file_size]
dFrame = pd.DataFrame({'MD5 Checksum': checksum,
                       'Archive Name': zip_name,
                       'Filesize ({})'.format(args.size[-1]): file_size,
                       'Directory':file_dir,
                       'Filename': file_list})
if 'csv' in args.type:
    dFrame.to_csv(op.join(args.output, args.name + '.csv'))
    tqdm.write('File saved: {}'.format(op.join(args.output, args.name + '.csv')))
elif 'excel' in args.type:
    dFrame.to_excel(op.join(args.output, args.name + '.xlsx'))
    tqdm.write('File saved: {}'.format(op.join(args.output, args.name + '.xlsx')))
else:
    raise Exception('Unable to save to the ouput file type.')