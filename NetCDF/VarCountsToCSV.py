"""
This script can be used to read a list of NetCDF files, count the number of observations
of each variable, and write out to CSV with name or file and the variable count.
"""

from netCDF4 import Dataset
from glob import iglob
import csv
import json
import os

# recipe will hold glob format of all netcdf file paths in json format
recipe_file = r'P:\01_DataOriginals\GOM\Metocean\NewMetoceanData_11_26_19\example_recipe.json'

# specify output csv location
output_csv = r'metoceanWaves_obs_counts.csv'

# open JSON recipe
with open(recipe_file, 'r') as f:
	recipe = json.load(f)

# create list of result to write to csv at the end
results = []

dirs = recipe['directives'][0]['files']

for glob in dirs:
	iter_filenames = iglob(glob)
	for path in iter_filenames:

		result = []
		result.append(path.split('/',1)[0])
		result.append(path.split('\\',1)[1])
		
		nc = Dataset(path)
		
		var_list = nc.variables
		
		for var in var_list:
			
			v = nc.variables[var]
			
			result.extend([var, v.size])
			
		results.append(result)
		
with open(output_csv,'w', newline='') as out:
	writer = csv.writer(out)
	for record in results:
		writer.writerow(record)