"""
This script will act as a simple way to join two tables by a unique ID field
on a ONE-TO-ONE basis.
Info from the appending csv will be added to the main csv and a new CSV
will be created

Created by: Alec Dyer
Contact info: alec.dyer@netl.doe.gov, (541) 918-4475

"""

import csv

main_csv = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\02_DataWorking\Incident_Platform_Matching\Matching Ver 3\Matched_Platforms_wSeverity_wAge_Ver3_reformatted.csv"
appending_csv = r"P:\01_DataOriginals\GOM\Metocean\Stats_For_NLP\plat_currents_stats.csv"
output_csv = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\02_DataWorking\Incident_Platform_Matching\Matching Ver 3\Matched_Platforms_wSeverity_wAge_Ver3_reformatted_wCurrents.csv"

main_ID_index = 13
appending_ID_index = 0
main_first_column_name = 'FID'

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
with open(output_csv,'wb') as output_file:
	writer = csv.writer(output_file)
	
	# open main csv to loop through
	with open(main_csv,'r') as main_file:
		reader = csv.reader(main_file)
		
		for line in reader:
			
			# grab platform ID from main file line
			main_ID = line[main_ID_index]
			
			# now loop through appending records and look for matches
			for record in Appending_Records:
				
				# check if this is the header and add appending header to line header
				if line[0] == main_first_column_name:
					for rec in record:
						line.append(rec)
					writer.writerow(line)
					break
				
				appending_ID = record[appending_ID_index]
				
				# check if the IDs match
				if appending_ID == main_ID:
					
					m += 1
					
					# if a match, append record to main line and write to output
					for rec in record:
						line.append(rec)
			
			if line[0] != main_first_column_name:
				r += 1
				writer.writerow(line)
			
print(format(m) + ' matches found out of ' + format(r) + ' total records.')