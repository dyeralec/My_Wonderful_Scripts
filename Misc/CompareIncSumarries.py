import csv

path_A = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\01_DataOriginals\Incidents\2006_2017_DataMerged_9_27_18.csv"
path_B = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\03_Analysis\Incidents\Categorized by Overall Cause\Classification 10222019\Group Classification\Reclassified_Merged.csv"
output_csv = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\03_Analysis\Incidents\Categorized by Overall Cause\Classification 10222019\Group Classification\Found_missing_incidents_b.csv"
index_A = 19
index_B = 21

origin_list = []

with open(path_B, 'r') as original:
	reader = csv.reader(original)
	for line in reader:
		inc_B = line[0] + '_' + line[1]
		origin_list.append(inc_B)
		
new_list = []

with open(path_A, 'r') as new:
	reader_B = csv.reader(new)
	
	with open(output_csv,'w',newline='') as out_file:
		writer = csv.writer(out_file)
		
		for row in reader_B:
			inc_A = row[0] + '_' + row[1]
			if inc_A not in origin_list:
				writer.writerow(row)