""""""
"""This script can be used to take the MM/DD/YYYY format of a date field in a csv and create new csv files for each month of each year."""
"""All of the original headers will be conserved in the process"""

from datetime import datetime
import csv
import os
import shutil

# create function that checks if a directory exists and if not creates one
def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

"""Change these values. NOTE THAT THERE ARE BACKSLASHES NOT FORWARD SLASHES!!!"""
inputCSV = open('P:/02_DataWorking/GOM/Infrastructure/Rigs/RigMatchingScripts/Outputs/Final_Tables/Rigs_Matched_Final_WGS84_NoDatesDeleted_ArcMapHeaders_LatLongEdit.csv', 'r')
# index number for the date field of the csv
dateField = 176
dateFormat = '%m/%d/%Y'
outputFolder = 'P:/02_DataWorking/GOM/Infrastructure/Rigs/RigMovements/Month_Year/Tables/'  #no apostrophe as end! that comes later
""""""

# create a list of the inputCSV
inputCSVreader = csv.reader(inputCSV)
inputCSVlist = []
for line in inputCSVreader:
    inputCSVlist.append(line)
inputCSV.close()

# index the header for later
header = inputCSVlist[0]

# create year and month lists to append to later. This will help with creating sub-folders
year_list = []
month_list = []

# loop through each record but not the header
for line in inputCSVlist:
    if line != inputCSVlist[0]:
        # index the date field
        dateStr = line[dateField]
        # use this function to create the date object of a certain format identified in the beginning
        recordDate = datetime.strptime(dateStr, dateFormat)
        # create variables for the month and year
        dateMonth = recordDate.month
        dateYear = recordDate.year
        # look for a csv that has the format year_month and either append it or create a new one. (binary!)
        with open(format(outputFolder) + format(dateYear) + '_' + format(dateMonth) + ".csv", 'ab+') as outputCSV:
            outputCSVwriter = csv.writer(outputCSV)
            outputCSVreader = csv.reader(outputCSV)
            outputCSVlist = []
            for row in outputCSVreader:
                outputCSVlist.append(row)
            # if the list is empty, that means that this is a new csv and the header needs to be written in.
            if not outputCSVlist:
                outputCSVwriter.writerow(header)
            # write the line into the csv
            outputCSVwriter.writerow(line)

        year_month = format(dateYear) + '_' + format(dateMonth)
        if dateYear not in year_list:
            year_list.append(dateYear)
        if dateMonth not in month_list:
            month_list.append(dateMonth)

# now move the csv files to folders based on year
for year in year_list:
    for month in month_list:
        # try to put the csv into the correct folder. However, if a year does not have a file for one of the months, just give an notice that there isn't one.
        try:
            fileLocation = format(outputFolder) + format(year) + '_' + format(month )+ '.csv'
            newFolder = format(outputFolder) + format(year) + '/'
            assure_path_exists(newFolder)
            shutil.move(fileLocation, newFolder)
        except:
            print('No csv file for this year and mont:' + format(year) + '_' + format(month) + '\n' + 'No folder was created')