import csv

file = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\02_DataWorking\Incident_Platform_Matching\Matching Ver 5\All_Platforms_Version5_Full.csv"
index = 2
index2 = 3
found = []
f = 0

with open(file, 'r') as records:
	reader = csv.reader(records)
	for line in reader:
		value = line[index] + line[index2]
		if value in found:
			print(line[index])
			print('--------------------')
			f += 1
		else:
			found.append(value)

print('Number of duplicates found: ' + format(f))