"""
This script will act as a simple way to join two tables by a unique ID field
on a ONE-TO-ONE basis.
Info from the appending csv will be added to the main csv and a new CSV
will be created

The user will provide a main csv that will be matched to along with an index of where the matching
field is in the header (count starting at 0 from left to right).
The user will also provide the appending csv paths and matching field index as a list, i.e. [r"path.csv", 0],
and there can be multiple CSVs to append in this list.

User needs to assign a no data value (string or number) that will be used to fill spaces if no match is found.

Lastly, user needs to provide where to write the output csv

NOTE: all fields will be appended, so the user may need to go into the output and delete duplicate fields as needed.

Created by: Alec Dyer
Contact info: alec.dyer@netl.doe.gov

"""

import csv
import os

##### INPUTS #####

main_csv = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\03_Analysis\Full Dataset\platforms_03092022_wMetocean_wProduction.csv"
main_ID_index = 0

appending_info = [
	[r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\02_DataWorking\Metocean\Corrosion Ambients\BioGeoChemical\BioGeoChemical.csv", 0],
	]

no_data_value = ''

output_csv = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\03_Analysis\Full Dataset\platforms_03092022_wMetocean_wProduction_wBioGeoChem.csv"

##########

# first open the main CSV and put into a list
with open(main_csv, 'r') as main_file:
	reader = csv.reader(main_file)
	Main_Records = [line for line in reader]

# read each appending csv to list
appending_records = []
for app_file, idx in appending_info:
	with open(app_file, 'r') as app_in:
		reader = csv.reader(app_in)
		recs = [line for line in reader]
		appending_records.append([recs, idx])

# keep track of the rows in main csv
i = 0

# keep output records
records_out = []

# loop over each line in the main records
for main_line in Main_Records:

	newLine = main_line # .copy()

	# grab platform ID from main file line
	main_ID = main_line[main_ID_index]

	# now loop through appending records and look for matches
	for app_record, app_idx in appending_records:

		match = False

		# check if this is the header and add appending header
		if i == 0:
			match = True
			for v in app_record[0]:
				newLine.append(v)
			continue
		else:
			# loop over each record in the appending record
			for app_line in app_record:

				appending_ID = app_line[app_idx]

				# check if the IDs match
				if appending_ID == main_ID:
					# match found
					match = True
					# append record to main line and write to output
					for v in app_line:
						newLine.append(v)

			# if a match was never found, add null spaces
			if match == False:
				newLine.extend([no_data_value]*len(app_record[0]))

	records_out.append(newLine)
	i += 1

# now open the output csv
with open(output_csv, 'w', newline='') as output_file:
	writer = csv.writer(output_file)
	writer.writerows(records_out)
			
print('Matching Completed!')