import os
import tarfile

main_dir = r'C:\Users\dyera\Documents\Task 6\Data\Elevation\NCEI Bathymetry\Mass Processing'
os.chdir(main_dir)

for file in os.listdir(main_dir):
    file_open = tarfile.open(file)
    file_open.extractall('./{}'.format(file.replace('.gz', '')))
    file_open.close()
    print('{} decompression completed'.format(file))