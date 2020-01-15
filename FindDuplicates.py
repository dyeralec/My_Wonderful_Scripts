import csv

file = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\03_Analysis\Incidents\Categorized by Overall Cause\Classification 10222019\Group Classification\Reclassified_Merged.csv"
index = 21
found = []

with open(file, 'r') as records:
	reader = csv.reader(records)
	for line in reader:
		if line[index] in found:
			print(line[21])
			print('--------------------')
		else:
			found.append(line[21])