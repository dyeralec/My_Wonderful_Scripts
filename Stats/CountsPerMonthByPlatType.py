"""
This script will calculate the number of records per rig type per month and export a table as a csv.

Can also be used for any categorical variable besides just type!

Required inputs and parameters:
	input spreadsheet
	output spreadsheet
	rig/platform type index
	date index
	datetime format
	beginning year
	ending year
	indication of platform or incident count for the header
"""

import csv
from datetime import datetime
from collections import Counter

# FILL OUT THESE VARIABLES!!!
input_spreadsheet = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\03_Analysis\Incidents\Categorized by Overall Cause\Struct_Weather_Incs_2008-2018_Classified.csv"
output_spreadsheet = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\03_Analysis\Incidents\Incident Counts by Type\Struct_Weather_Incs_2008-2018_Stats.csv"
type_field_index = 16
date_field_index = 0
date_format = '%m/%d/%Y'
beginning_year = 2008
ending_year = 2018
record_type = 'PlatIncCount'

# open input spreadsheet and write to a list
with open(input_spreadsheet,'r') as input:
	records = []
	reader = csv.reader(input)
	for line in reader:
		records.append(line)
		
# create the header format
header = ['Month','Year','M/Y',record_type]

# get list of all the possible rig types
RigTypes = []
for row in records:
	if row != records[0]:
		type = row[type_field_index]
		
		# if type if blank, call it unknown
		if type == "":
			type = 'UNKNOWN'
		
		# add type to RigType list if not already in it
		if type not in RigTypes:
			RigTypes.append(type)
	
# now add list of types to the header
for t in RigTypes:
	header.append(t)
	
# start a master list that will contain the lines for the output spreadsheet
master_list = []

master_list.append(header)
	
# start looping through the years and months
for year in range(beginning_year,ending_year+1):
	for month in range(1,13):
		type_list = []
		total_count = 0
		
		for record in records:
			if record != records[0]:
				
				# grab the date information
				date_object = datetime.strptime(record[date_field_index],date_format)
				y = date_object.year
				m = date_object.month
				
				# check if the record year and month matches the current loop
				if (y == year) and (m == month):
					
					# grab type string from record
					rig_type = record[type_field_index]
					# if type is blank, call it unknown
					if rig_type == "":
						rig_type = 'UNKNOWN'
						
					# add type to type_list
					type_list.append(rig_type)
					
					# add to total count
					total_count += 1
					
		# create a counter for the number of each rig type within the type_list
		recordsTypeCounts = Counter(type_list)
		
		# create list with correct formatting to match the header
		new_record = [month,year,str(format(month) + '/' + format(year)),total_count]
		for T in RigTypes:
			new_record.append(recordsTypeCounts[T])
			
		# append new record list to the master list
		master_list.append(new_record)
		
# finally, write master list to output spreadsheet
with open(output_spreadsheet,'w',newline="") as output:
	writer = csv.writer(output)
	writer.writerows(master_list)