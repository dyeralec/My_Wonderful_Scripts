import csv

path_A = r"C:\Users\dyera\Documents\Offshore Task 3\GradientBoostingRegressor\1.DATA\Removed_Platforms_Version5_ValidationSet_2.csv"
path_B = r"C:\Users\dyera\Documents\Offshore Task 3\GradientBoostingRegressor\1.DATA\Removed_Platforms_Version5_Full_YNedits_StormEdits_2.csv"
output_csv = r"C:\Users\dyera\Documents\Offshore Task 3\GradientBoostingRegressor\1.DATA\Training_IDs.csv.csv"

origin_list = []

with open(path_A, 'r') as original:
	reader = csv.reader(original)
	for line in reader:
		inc_A = line[0] # + '_' + line[5]
		origin_list.append(inc_A)

# keeping track of the number of differences.
n = 0

with open(output_csv, 'w', newline='') as out:
	writer = csv.writer(out)
	writer.writerow(['ID'])

	with open(path_B, 'r') as new:
		reader_B = csv.reader(new)

		for row in reader_B:
			inc_B = row[0]
			if inc_B not in origin_list:
				writer.writerow([inc_B])
				print(inc_B)
				
# print(format(n) + format(' difference(s) found.'))