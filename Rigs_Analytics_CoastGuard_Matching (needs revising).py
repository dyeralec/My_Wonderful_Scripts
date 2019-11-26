"""Combine the Rig Analytics and Coast Guard Rig data."""
"""Keep all columns"""
"""Match names using fuzzy wuzzy and give each rig a unique ID. If no ID yet, create one for that rig."""
"""if FW >50%, then use command prompt (Y/N) in debugger to say yes match or not. Send each match to seperate files of yes's and no's"""

# import modules
import sys
import csv
from fuzzywuzzy import fuzz

# First, open the rig data sets and write them to individual lists.

# open and read Rigs Analytics
RigsAnalytics = open('Data/RigsAnalytics_Offshore_noSpaceHeaders.csv', 'r')
RigsAn_reader = csv.DictReader(RigsAnalytics)
RigsAn_dict = []
for line in RigsAn_reader:
    RigsAn_dict.append(line)
RigsAnalytics.close()

# open and read Coast Guard Rigs
RigsCG = open('Data/OilRigMovementTables-CoastGuard_QAQC_AD.csv', 'r')
RigsCG_reader = csv.DictReader(RigsCG)
RigsCG_dict = []
for line in RigsCG_reader:
    RigsCG_dict.append(line)
RigsCG.close()

# create header list from Rigs Analytics
RigsAnalytics = open('Data/RigsAnalytics_Offshore_noSpaceHeaders.csv', 'r')
RigsAn_KeyReader = csv.reader(RigsAnalytics)
headerA = []
for line in RigsAn_KeyReader:
    headerA.append(line)
    break
RigsAnalytics.close()

# create header list from Coast Guard Rigs
RigsCG = open('Data/OilRigMovementTables-CoastGuard_QAQC_AD.csv', 'r')
RigsCG_KeyReader = csv.reader(RigsCG)
headerB = []
for line in RigsCG_KeyReader:
    headerB.append(line)
    break
RigsCG.close()

# remove the extra brackets in the headers
headerA = headerA[0]
headerB = headerB[0]
# remove name, latitude, and longitude keys from headerB
headerB.pop(13)
headerB.pop(12)
headerB.pop(5)
headerB.pop(6)

# write matched DictWriter file with new headers
RigsMatched = open('Outputs/RigsMatched_Analytics_CoastGuard', 'wb')
fieldnames = headerA + headerB
RigsMatched_writer = csv.DictWriter(RigsMatched, fieldnames=fieldnames)
# write the header
RigsMatched_writer.writeheader()

# write Rigs Analytics into RigsMatched
for line in RigsAn_dict:
    RigsMatched_writer.writerow(line)
# write Coast Guard Rigs into RigsMatched
for row in RigsCG_dict:
    RigsMatched_writer.writerow(row)
# close RigsMatched
RigsMatched.close()

"""Here is the tricky part... Need to give IDs to Coast Guard data. If same name as in Rigs Analtyics, give the Rigs Analytics ID to the CG rig of the same name.
If there is no name match, then give a new ID to it starting at 5819. """

"""Need to use fuzzy wuzzy for matching. I will create a boolean prompt to say yes or now for matching if the fuzzy ratio is >= 75%. 
I should use 50% match or greater, but there will be too many matches and it would take forever to finish the executing. 
If I say yes, it will do the name match and also write the two words into the YesMatch file. If not a match, write the two words into the NoMatch file. 
Then, before even trying the fuzzy wuzzy match, loop through the Yes and No matchfiles to decide if two words should be a match or not. This will make the code efficient."""

# try to read YesMatch file containing past fuzzy matches if available
try:
    YesMatch_Past = open('Outputs/YesMatch.csv', 'r')
    YesMatch_Past_reader = csv.reader(YesMatch_Past)
    YesMatch_list = []
    # write YesMatch.csv to a list so that it can be referenced later
    for match in YesMatch_Past_reader:
        YesMatch_list.append(match)

    YesMatch_Past.close()

# if reading file results in an error, there is no file and one will need to be written.
except:
    # write yes match file
    YesMatch = open('Outputs/YesMatch.csv', 'ab')
    # create list to append to before writing to the file at the end
    YesMatch_list = []
    # now that the file is created, I can close it and open it later for appending
    YesMatch.close()

# try to read NoMatch file containing past fuzzy matches if available
try:
    NoMatch_Past = open('Outputs/NoMatch.csv', 'r')
    NoMatch_Past_reader = csv.reader(NoMatch_Past)
    NoMatch_list = []
    # write NoMatch.csv to a list so that it can be referenced later
    for no_match in NoMatch_Past_reader:
        NoMatch_list.append(no_match)

    NoMatch_Past.close()

# if reading file results in an error, there is no file and one will need to be written.
except:
    # write no match file
    NoMatch = open('Outputs/NoMatch.csv', 'ab')
    # create list to append to before writing to the file at the end
    NoMatch_list = []
    NoMatch.close()

# set ID to begin after largest ID already found in Rig Analytics
ID = 5819

"""Not sure if I'm going to use this... Update: didn't need"""
# counts to check
matchCount = 0
unmatchedCount = 0

"""Not sure if I'm going to use this... Update: didn't need"""
matchChecks = []

# create list of special characters to be taken out for matching
replaceStr_Items = ["'","-",".","(",")","_","#","(DOT)"," "]

# open RigsMatched for amending
RigsMatched = open('Outputs/RigsMatched_Analytics_CoastGuard.csv', 'r') # open for appending or reading????
# create new reader for RigsMatched
RigsMatched_DictReader = csv.DictReader(RigsMatched)
RigsMatched_dict = []
for line in RigsMatched_DictReader:
    RigsMatched_dict.append(line)
RigsMatched.close()

# use fuzzy wuzzy to match names and give appropriate IDs
# loop through all the rows in the matched rigs dictionary
for row in RigsMatched_dict:
    found = False
    # perform this following operation only if the rigId field is empty
    if row['rigId'] == '':
        # loop through all the lines in the matched rigs dictionary
        for line in RigsMatched_dict:
            # only look at lines that do have a rig ID
            if line['rigId'] != '':
                # create new name variable
                Name_A = row['Rig_Name']
                Name_B = line['Rig_Name']
                # edit out unwanted characters for matching
                for item in replaceStr_Items:
                    Name_A = Name_A.replace(item, "")
                for item in replaceStr_Items:
                    Name_B = Name_B.replace(item, "")

                # lowercase all names
                Name_A = Name_A.lower()
                Name_B = Name_B.lower()

                # create new name variable
                Type_A = row['Rig_Type']
                Type_B = line['Rig_Type']
                # edit out unwanted characters for matching
                for item in replaceStr_Items:
                    Type_A = Type_A.replace(item, "")
                for item in replaceStr_Items:
                    Type_B = Type_B.replace(item, "")

                # lowercase all types
                Type_A = Type_A.lower()
                Type_B = Type_B.lower()

                # now combine name and type for fuzzy matching
                Name_Type_A = Name_A + Type_A
                Name_Type_B = Name_B + Type_B

                # create variabels for the name matching format
                NameMatch = [(Name_A + "(" + Type_A + ")"+ " --- " + Name_B + "(" + Type_B + ")"+ '\n')]
                # check YesMatch and NoMatch lists to see if this name pair is already in it
                if (NameMatch not in YesMatch_list) and (NameMatch not in NoMatch_list):

                    # fuzzy ratio
                    ratio = fuzz.ratio(Name_Type_A, Name_Type_B)
                    # if there is a close match for the name, prompt me to say yes or no on the match based on NAME and TYPE.
                    if (ratio >= 75.0):

                        # check here using tkinker to put record in matched or unmatched
                        BaseText = '\n' + "Knowing the two names and their type, do they match?" + '\n' + "Fuzzy Ratio = " + format(ratio) + "; " + format(Name_A) + "(" + format(Type_A) + "), " + format(Name_B) + "(" + format(Type_B) + ")" + '\n' + 'Type "t" for true or anything else with with quotes for false.'

                        try:
                            boolean = input(BaseText)
                        except:
                            boolean = input(BaseText)

                        # If there is a match...
                        if boolean == "t" or boolean == "T":
                            # open YesMatch file for appending and create a writer for it
                            YesMatch_Future = open('Outputs/YesMatch.csv', 'ab')
                            YesMatch_Future_writer = csv.writer(YesMatch_Future)
                            # append the match to the YesMatch list
                            YesMatch_list.append([(Name_A + "(" + Type_A + ")"+ " --- " + Name_B + "(" + Type_B + ")"+ '\n')])
                            # append the name format to YesMatch.csv
                            YesMatch_Future_writer.writerow([(Name_A + "(" + Type_A + ")"+ " --- " + Name_B + "(" + Type_B + ")"+ '\n')])
                            YesMatch_Future.close()
                            #RigMatch = 1
                            # set the rigId of the row equal to the rigId from the line
                            row['rigId'] = line['rigId']
                            found = True
                            break

                        # if it is not a match, put that name format into the NoMatch list and csv so that if it sees that same name match again it will know that its not a match and move on
                        else:
                            # open NoMatch.csv for appending and create a writer for it
                            NoMatch_Future = open('Outputs/NoMatch.csv', 'ab')
                            NoMatch_Future_writer = csv.writer(NoMatch_Future)
                            # append the name format to the NoMatch list
                            NoMatch_list.append([(Name_A + "(" + Type_A + ")"+ " --- " + Name_B + "(" + Type_B + ")"+ '\n')])
                            # write the name format to the NoMatch csv
                            NoMatch_Future_writer.writerow([(Name_A + "(" + Type_A + ")"+ " --- " + Name_B + "(" + Type_B + ")"+ '\n')])
                            NoMatch_Future.close()
                # if the name match is already in YesMatch list, then give that line ID to the row ID
                if (NameMatch in YesMatch_list):
                    RigMatch = 1
                    row['rigId'] = line['rigId']
                    found = True
                    break
        # if there is no name match at all, give a new ID to that rig
        if found == False:
            row['rigId'] = ID
            ID += 1

"""Now write the updated Rigs Matched list to the Matched csv file"""
RigsMatched = open('Outputs/RigsMatched_Analytics_CoastGuard.csv', 'wb')
writer = csv.DictWriter(RigsMatched, fieldnames=fieldnames)
writer.writeheader()
for line in RigsMatched_dict:
    writer.writerow(line)
RigsMatched.close()

# Need to write the YesMatch and NoMatch LISTS to their appropriate csv files
YesMatch_Future = open('Outputs/YesMatch_Redo_Test.csv', 'w') # need wb?
YesMatch_Future_writer = csv.writer(YesMatch_Future)
for line in YesMatch_list:
    YesMatch_Future_writer.writerow(line)
YesMatch_Future.close()

NoMatch_Future = open('Outputs/NoMatch_Redo_Test.csv', 'w') # need wb?
NoMatch_Future_writer = csv.writer(NoMatch_Future)
for line in NoMatch_list:
    NoMatch_Future_writer.writerow(line)
NoMatch_Future.close()

""" Finished! """