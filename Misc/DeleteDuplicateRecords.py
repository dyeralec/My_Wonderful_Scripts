import csv

inFile = r"P:\01_DataOriginals\GOM\Infrastructure\Emissions\2017_Gulfwide_Platform_Inventory_20190705_CAP_GHG\2017_Gulfwide_Platform_20190705_CAP_GHG.csv"
outFile = r"P:\01_DataOriginals\GOM\Infrastructure\Emissions\2017_Gulfwide_Platform_Inventory_20190705_CAP_GHG\2017_Gulfwide_Platforms_NoDuplicatePlatforms.csv"
index = 1
found = []
f = 0

with open(outFile, 'w', newline='') as output:
	writer = csv.writer(output)
	
	with open(inFile, 'r') as records:
		reader = csv.reader(records)
		for line in reader:
			if line[index] in found:
				f += 1
			else:
				found.append(line[index])
				writer.writerow(line)

print('Number of duplicates found: ' + format(f))