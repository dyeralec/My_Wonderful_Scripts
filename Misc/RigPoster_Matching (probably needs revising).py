""""""
"""This code will match the rig poster dataset to the already made matched data set containing the drillinginfo.com (RigsAnalytics) and Coast Guard Rig data sets."""
"""Get list of poster headers and append into the matched csv header"""
"""loop through each rig in rig poster through  matched data set. If name match, give the poster attributes to that rig in the matched csv."""

# import modules
import csv
from fuzzywuzzy import fuzz

# open and read matched data set to a list
RigsMatched = open('Outputs/RigsMatched_Analytics_CoastGuard.csv', 'r')
RigsMatched_reader = csv.DictReader(RigsMatched)
RigsMatched_dict = []
for line in RigsMatched_reader:
    RigsMatched_dict.append(line)
RigsMatched.close()

# open and read poster data set to a list
Poster = open('Data/OffshoreRigs_Poster_HeaderEdits.csv', 'r')
Poster_reader = csv.DictReader(Poster)
Poster_dict = []
for line in Poster_reader:
    Poster_dict.append(line)
Poster.close()

# create header list from Rigs Matched
RigsMatched = open('Outputs/RigsMatched_Analytics_CoastGuard.csv', 'r')
RigsMatched_KeyReader = csv.reader(RigsMatched)
headerA = []
for line in RigsMatched_KeyReader:
    headerA.append(line)
    break
RigsMatched.close()

# create header list from poster
Poster = open('Data/OffshoreRigs_Poster_HeaderEdits.csv', 'r')
Poster_KeyReader = csv.reader(Poster)
headerB = []
for line in Poster_KeyReader:
    headerB.append(line)
    break
Poster.close()

# remove the extra brackets in the headers
headerA = headerA[0]
headerB = headerB[0]

# create new matched file with additional headers from the poster
Matched_AddHeader = open ('Outputs/Poster_Matching/Matched_AddHeader.csv', 'wb')
# want the header to have the headers from the matched rigs and poster data sets
fieldnames = headerA + headerB
# write the headers and the matched rigs dictionary to the csv
Matched_AddHeader_writer = csv.DictWriter(Matched_AddHeader, fieldnames=fieldnames)
Matched_AddHeader_writer.writeheader()
for line in RigsMatched_dict:
    Matched_AddHeader_writer.writerow(line)
Matched_AddHeader.close()

"""If name is a match, but into the YesMatch.csv. If name is not a match, I will put it into NoMatch.csv"""

# read file containing past fuzzy matches if available
try:
    YesMatch = open('Outputs/Poster_Matching/YesMatch.csv', 'r')
    YesMatch_Past_reader = csv.reader(YesMatch)
    YesMatch_list = []
    # write YesMatch.csv to a list so that it can be referenced later
    for match in YesMatch_Past_reader:
        YesMatch_list.append(match)
    YesMatch.close()

# if reading file results in an error, there is no file and one will need to be written.
except:
    # write yes match file
    YesMatch = open('Outputs/Poster_Matching/YesMatch.csv', 'ab')
    YesMatch_writer = csv.writer(YesMatch) # pretty sure this isn't needed here but oh well doesn't hurt...
    # create a YesMatch list to append to which can later be written into the csv
    YesMatch_list = []
    YesMatch.close()

# read file containing past fuzzy non-matches if available
try:
    NoMatch = open('Outputs/Poster_Matching/NoMatch.csv', 'r')
    NoMatch_Past_reader = csv.reader(NoMatch)
    NoMatch_list = []
    # write NoMatch.csv to a list so that it can be referenced later
    for no_match in NoMatch_Past_reader:
        NoMatch_list.append(no_match)
    NoMatch.close()

# if reading file results in an error, there is no file and one will need to be written.
except:
    # write no match file
    NoMatch = open('Outputs/Poster_Matching/NoMatch.csv', 'ab')
    NoMatch_writer = csv.writer(NoMatch) # pretty sure this isn't needed here but oh well doesn't hurt...
    # create a NoMatch list to append to which can later be written into the csv
    NoMatch_list = []
    NoMatch.close()

# create list of special characters to be taken out for matching
replaceStr_Items = ["'","-",".","(",")","_","#","(DOT)"," "]

# loop through each poster dictionary record
for row in Poster_dict:
    found = False
    # create new name variable
    # RigsMatched name
    Name_A = row['Name']
    # edit out unwanted characters for matching
    for item in replaceStr_Items:
        Name_A = Name_A.replace(item, "")
    # lowercase all names
    Name_A = Name_A.lower()

    # loop through RigsMatched dictionary
    for line in RigsMatched_dict:
        # Poster name
        Name_B = line['Rig_Name']
        # edit out unwanted characters for matching
        for item in replaceStr_Items:
            Name_B = Name_B.replace(item, "")

        # lowercase all names
        Name_B = Name_B.lower()

        # create variable with name matching format
        NameMatch = [(Name_A + " --- " + Name_B + '\n')]

        # check Yes and No match lists to see if this name pair is already in it
        if (NameMatch not in YesMatch_list) and (NameMatch not in NoMatch_list):
            # fuzzy ratio
            ratio = fuzz.ratio(Name_A, Name_B)

            # if the match is 100% then I know that it is a correct match
            if (ratio == 100):
                # add NameMatch to the YesMatch_list
                YesMatch_list.append(NameMatch)
                # delete name value from poster row
                #row.pop('Name')
                # append poster information to the RigsMatched line
                line.update(row)
                found = True
                #break

            if found == False:
                if (ratio >=60.0):
                    # check here using tkinker to put record in matched or unmatched
                    BaseText = '\n' + "Knowing the two names, do they match?" + '\n' + "Fuzzy Ratio = " + format(ratio) + "; " + format(Name_A) + ", " + format(Name_B) + '\n' + 'Type "t" for true or anything else with with quotes for false.'

                    try:
                        boolean = input(BaseText)
                    except:
                        boolean = input(BaseText)

                    # If there is a match...
                    if boolean == "t" or boolean == "T":
                        # add NameMatch to the YesMatch_list
                        YesMatch_list.append(NameMatch)
                        # delete name value from poster row
                        #row.pop('Name')
                        # append poster information to the RigsMatched line
                        line.update(row)
                        found = True
                        #break
                    # if not a match...
                    else:
                        # add NameMatch to the NoMatch_list
                        NoMatch_list.append(NameMatch)
        # if match is already found in YesMatch list...
        if(NameMatch in YesMatch_list):
            # delete name value from poster row
            #row.pop('Name')
            # append poster information to the RigsMatched line
            line.update(row)

# write YesMatch_list to the csv
YesMatch = open('Outputs/Poster_Matching/YesMatch.csv', 'ab')
YesMatch_writer = csv.writer(YesMatch)
for line in YesMatch_list:
    YesMatch_writer.writerow(line)
YesMatch.close()

# write NoMatch_list to the csv
NoMatch = open('Outputs/Poster_Matching/NoMatch.csv', 'ab')
NoMatch_writer = csv.writer(NoMatch)
for line in NoMatch_list:
    NoMatch_writer.writerow(line)
NoMatch.close()

# create a new file to write the appended RigsMatched dictionary too
RigsMatched_Attributes = open('Outputs/Final_Tables/RigsMatched_Attributes.csv', 'wb')
fieldnames = headerA + headerB
Rigs_writer = csv.DictWriter(RigsMatched_Attributes, fieldnames=fieldnames)
# write the header in
Rigs_writer.writeheader()
# write in RigsMatched data
for line in RigsMatched_dict:
    Rigs_writer.writerow(line)
RigsMatched_Attributes.close()