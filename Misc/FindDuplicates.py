import csv

file = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\02_DataWorking\Incident_Platform_Matching\Matching Ver 3\All_Platforms_Ver3_reformatted.csv"
index = 0
found = []
f = 0

with open(file, 'r') as records:
	reader = csv.reader(records)
	for line in reader:
		if line[index] in found:
			print(line[index])
			print('--------------------')
			f += 1
		else:
			found.append(line[index])

print('Number of duplicates found: ' + format(f))