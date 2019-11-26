"""
This script will be used to classify platform incident records into structural, weather, or human related
by looking for key terms in the incident summary. The team has created a list of key words to look for in
each category and are located in a csv. The output will be the input incidents csv with added columns
for structural, weather, and human related with ones for true or zeros for false in each category.
In addition, there are 'no damage' keywords that the script will be looking for to help out with
categorizing.

If only structural keywords are found in the summary, then the script will assume that the incident
is only structural related and not weather or human related.

If only human keywords are found, then the script will assume that the incident is only human related.

If a mix of structural, weather, human, and no damage keywords are found, an input in the run console
will pop up giving the incident summary, whether or not the incident was categorized as weather or
human related by the creator, and found keywords for each category. The user will then need to enter
an input of 3 digits, separated by commas, in quotes. The digits can only be 1 for true or 0 for false.
The order of the digits is structural, weather, and lastly human.

For example, if you perceive the incident to by structural and human related, then you would enter
"1,0,1" (with quotes!!!) into the prompt and press 'enter' key.
"""

import csv
import re
import sys

Incident_csv = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\03_Analysis\Incidents\Categorized by Overall Cause\Classification 10222019\Group Classification\Classification_Alec\Unclassified_Alec.csv"
Keywords_csv = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\03_Analysis\Incidents\Categorized by Overall Cause\Classification 10222019\Group Classification\Classification_Alec\Classification_Keywords.csv"
Output_csv = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\03_Analysis\Incidents\Categorized by Overall Cause\Classification 10222019\Group Classification\Classification_Alec\Re_Classified_Alec.csv"

human_error_field_index = 94
weather_field_index = 95
summary_field_index = 21

"""First, grab all of the keywords from the keywords csv for structural, weather, and human.
The indexing here is assuming a certain organization of the csv.
"""
keyword_lines = []
with open(Keywords_csv,'r') as file_A:
    reader_A = csv.reader(file_A)
    for line in reader_A:
        keyword_lines.append(line)
structural_keywords = tuple(keyword_lines[1][0].split(','))
weather_keywords = tuple(keyword_lines[1][1].split(','))
human_keywords = tuple(keyword_lines[1][2].split(','))
no_damage_keywords = tuple(keyword_lines[1][3].split(','))

# in order to be able to start on the incident where the user left off,
# need to grab a list of all the incident summaries in the output csv
# since this is the only true unique identifier here.
inc_summary_list = []
header = False
try:
    with open(Output_csv,'r') as file:
        reader = csv.reader(file)
        for line in reader:
            # since this opened, it must have a header. Take note so another header is not added
            header = True
            if line[0] != "":
                # grab summary into list
                inc_summary_list.append(line[summary_field_index].lower())
except IOError:
    print('')

# grab the number of incident records
with open(Incident_csv,'r') as file_B:
    reader_B = csv.reader(file_B)
    row_length = sum(1 for row in reader_B) - 1
# also keep track of the incident row number
i = 0

# open incident csv
with open(Incident_csv,'r') as file_B:
    reader_B = csv.reader(file_B)
    # open output csv to write to
    with open(Output_csv,'ab') as file_C:
        writer = csv.writer(file_C)
        
        # loop through all incident records
        for row in reader_B:
    
            # keep track of the start of the classification indexes
            start_index = len(row)
            
            # check if the line is the header
            if (row[summary_field_index] == 'Incident Summary') and (header == False):
                # add new columns
                row.append('Structure Related (0/1')
                row.append('Weather Related (0/1')
                row.append('Human Related (0/1')

                # now write the row to the output csv
                writer.writerow(row)
                
                i += 1

                continue
                
            inc_summary = row[summary_field_index].lower()
                
            # check if this incident summary is in the inc_summary_list. If it is,
            # then this incident has already been completed and does not need to be delt with
            if inc_summary not in inc_summary_list:
            
                # since we are assuming all incidents are structural and not human or weather related to begin with,
                # add those values to the row so that they can be indexed and changed easily later
                row.append(1)
                row.append(0)
                row.append(0)
                # keeping track if the incident reported human cuased or weather cuased
                human_caused = False
                weather_caused = False
                # loop for whether or not the input human and weather caused fields contain a 1
                if row[weather_field_index] == '1':
                    row[start_index + 1] = 1
                    weather_caused = True
                if row[human_error_field_index] == '1':
                    row[start_index + 2] = 1
                    human_caused = True
    
                """This next section will look for keywords in the incident summary for weather, human,
                and the self defined no damage keywords. a list will be kept for the keywords that are found
                for each category, then if any are found a prompt in the console will pop up displaying the
                incident summary, keywords found, and prompt the user to answer yes or no for structural,
                weather, and human causes.
                """
    
                found_structural_keys = set()
                found_weather_keys = set()
                found_human_keys = set()
                found_no_damage_keys = set()
    
                # loop for structural keys
                for key in structural_keywords:
                    if key in inc_summary:
                        found_structural_keys.add(key)
    
                # loop for weather keys
                for key in weather_keywords:
                    if key in inc_summary:
                        found_weather_keys.add(key)
    
                # loop for human keys
                for key in human_keywords:
                    if key in inc_summary:
                        found_human_keys.add(key)
    
                # loop for no damage keys
                for key in no_damage_keywords:
                    if key in inc_summary:
                        found_no_damage_keys.add(key)
                        
                # there are only human keywords, assume only human related and not structural or weather related
                if (len(found_structural_keys) == 0) and (len(found_weather_keys) == 0) and (len(found_human_keys) != 0) and (len(found_no_damage_keys) == 0):
                    row[start_index] = 0
                    row[start_index + 1] = 0
                    row[start_index + 2] = 1
                    i += 1
                    continue

                # if it only finds structural and weather key words, then mark as only structural and weather
                if (len(found_structural_keys) != 0) and (len(found_weather_keys) != 0) and (len(found_human_keys) == 0) and (len(found_no_damage_keys) == 0):
                    row[start_index] = 1
                    row[start_index + 1] = 1
                    row[start_index + 2] = 0
                    # writer.writerow(row)
                    i += 1
                    continue
                    
                if (len(found_weather_keys) != 0) or (len(found_human_keys) != 0) or (len(found_no_damage_keys) != 0):
    
                    print('Incident ' + format(i) + ' out of ' + format(row_length) + '\n\n'\
                          + 'Human Caused: ' + format(human_caused) + '\n'\
                          + 'Weather Caused: ' + format(weather_caused) + '\n\n'\
                          + 'Incident Summary:\n' + inc_summary.replace('.','.\n') + '\n\n'\
                          + 'Found structural keywords:\n' + format(found_structural_keys) + '\n\n'\
                          + 'Found weather keywords:\n' + format(found_weather_keys) + '\n\n'\
                          + 'Found human-related keywords:\n' + format(found_human_keys) + '\n\n'\
                          + 'Found no damage-related keywords:\n' + format(found_no_damage_keys) + '\n\n')
    
                    # ask if structurally related
                    structural_test = 'Based on the incident summary, is it structural, weather, and/or human related?\n' \
                            + 'Enter 3 digits (1 or 0), separated by commas, in quotes. 1 is true, 0 is false. Example: "1,0,1"\n'\
                            + 'The first digit is for structural, then weather, and lastly human.\n'
                    
                    accept = False
                    while accept == False:
                        try:
                            boolean = str(input(structural_test))
                            # check if the input is valid format using Regex
                            if re.match('[0-1],[0-1],[0-1]', boolean):
                                accept = True
                            if boolean.lower() == 'stop':
                                sys.exit()
                        except NameError:
                            pass
    
                    # separate boolean answer into a list
                    answer = boolean.split(',')
    
                    # if noted NOT structural, than change the value
                    if answer[0] == '0':
                        row[start_index] = 0
    
                    # if noted weather related, change the value to 1
                    if answer[1] == '1':
                        row[start_index + 1] = 1
    
                    # if noted human related, change the value to 1
                    if answer[2] == '1':
                        row[start_index + 2] = 1
    
                    print('\n-----------------------------------\n')
    
                    # write row to output
                    writer.writerow(row)
                    
                    i += 1
                    
                    continue
                    
                writer.writerow(row)
    
            i += 1