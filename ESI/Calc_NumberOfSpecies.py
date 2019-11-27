from osgeo import ogr
import csv
import os

folder = r'C:\Users\dyera\Desktop\Atlantic Biofiles'

species = []

for filename in os.listdir(folder):
    csv_path = os.path.join(folder, filename)
    f = open(csv_path,'r')
    r = csv.reader(f)
    for line in r:
        name = line[3]
        if filename == 'ChesapeakeBay_biofile.csv':
            name = line[4]
        if name not in species:
            species.append(name)
            
species.remove('GEN_SPEC')
species.remove("")
            
print(len(species))