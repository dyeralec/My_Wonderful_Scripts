"""
This script will act as a simple way to join two tables by a unique ID field
on a ONE-TO-ONE basis.
Info from the appending csv will be added to the main csv and a new CSV
will be created

Created by: Alec Dyer
Contact info: alec.dyer@netl.doe.gov, (541) 918-4475

"""

import csv

main_csv = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\03_Analysis\Machine Learning\1.DATA\Training_IDs.csv"
appending_csv = r"C:\Users\dyera\Documents\Offshore Task 3\GradientBoostingRegressor\RISK PREDICTION\Bins\Removed_Platforms_OCS_Inc_Risk_Quartiles_5Bins.csv"
output_csv = r"C:\Users\dyera\Documents\Offshore Task 3\GradientBoostingRegressor\RISK PREDICTION\Bins\Removed_Platforms_OCS_Inc_Risk_Quartiles_5Bins_TrainingSet.csv"

main_ID_index = 0
other_ID_index = None
appending_ID_index = 0
main_first_column_name = 'ID'

# first open the appending CSV and put into a list
with open(appending_csv, 'r') as appending_file:
	Appending_Records = []
	reader = csv.reader(appending_file)
	for line in reader:
		Appending_Records.append(line)

# keep track of the number of matches found
m = 0
# keep track of total amount of records in the main csv
r = 0
# keep track of which Platform IDs are already completed
completed = []
# now open the output csv
with open(output_csv,'w', newline='') as output_file:
	writer = csv.writer(output_file)
	
	# open main csv to loop through
	with open(main_csv,'r') as main_file:
		reader = csv.reader(main_file)
		
		for line in reader:
			
			newLine = line
			
			# grab platform ID from main file line
			main_ID = line[main_ID_index] # + line[other_ID_index]
			
			# now loop through appending records and look for matches
			for record in Appending_Records:
				
				# check if this is the header and add appending header to line header
				if line[0] == main_first_column_name:
					for rec in record:
						newLine.append(rec)
					writer.writerow(newLine)
					break

				r += 1
				
				appending_ID = record[appending_ID_index]
				
				# check if the IDs match
				if appending_ID == main_ID:
					
					m += 1
					
					# if a match, append record to main line and write to output
					for rec in record:
						newLine.append(rec)

			writer.writerow(newLine)
			
print(format(m) + ' matches found out of ' + format(r) + ' total records.')