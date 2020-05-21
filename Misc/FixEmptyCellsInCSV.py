import csv

filePath = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\02_DataWorking\Incident_Platform_Matching\Matching Ver 3\All_Platforms_Ver3_reformatted.csv"
fileOut = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\02_DataWorking\Incident_Platform_Matching\Matching Ver 3\All_Platforms_Ver3_reformatted_Edit.csv"

length = 234

with open(fileOut, "wb") as outFile:
	writer = csv.writer(outFile)
	
	with open(filePath, "r") as inFile:
		reader = csv.reader(inFile)
		
		for line in reader:
			
			newLine = line
			
			while len(newLine) < length:
				newLine.append('')
				
			writer.writerow(line)