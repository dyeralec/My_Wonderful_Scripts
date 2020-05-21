import csv

path_A = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\02_DataWorking\Incident_Platform_Matching\Matching Ver 3\base data\Platforms_BSEE_Dec19.csv"
path_B = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\02_DataWorking\Incident_Platform_Matching\Matching Ver 3\Matched_Incidents_wSeverity_wAge_Ver3_reformatted.csv"
output_csv = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\02_DataWorking\Incident_Platform_Matching\Matching Ver 3\ExtraPlatRecordsInReformatted.csv"

origin_list = []

with open(path_B, 'r') as original:
	reader = csv.reader(original)
	for line in reader:
		inc_B = line[0] # + '_' + line[5]
		origin_list.append(inc_B)

# keeping track of the number of differences.
n = 0

with open(path_A, 'r') as new:
	reader_A = csv.reader(new)
	
	with open(output_csv,'wb') as out_file:
		writer = csv.writer(out_file)
		
		for row in reader_A:
			inc_A = row[1] + '_' + row[5]
			if inc_A not in origin_list:
				n += 1
				writer.writerow(row)
				
print(format(n) + format(' difference(s) found.'))