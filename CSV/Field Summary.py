"""
For a csv calculate the summary stats for fields.
"""

import csv
import numpy as np
import pandas as pd

def CSV_to_list(csv_path):
    import csv

    list = []
    with open(csv_path, 'r') as Record:
        reader = csv.reader(Record)
        for line in reader:
            list.append(line)

    return (list)

in_csv = r'Removed_Platforms_Ver3_Reformatted_wMetocean.csv'
out_csv = r'Removed_Platforms_Ver3_Reformatted_wMetocean_FieldSummary.csv'

records = CSV_to_list(in_csv)

fields = records[0]

values_array = pd.DataFrame(records[1:])

df = pd.read_csv(in_csv)

with open(out_csv, 'w', newline='') as outgoing:

    writer = csv.writer(outgoing)

    writer.writerow(['Feature', 'Type', 'Number of Fields', 'Total Blank Fields',\
                     'Min', 'Max', 'Mean', 'Median',\
                     'Number of Unique Fields'])

    for feat in df:

        to_write = []
        to_write.append(feat)

        values = df[feat]

        t = values.dtype

        to_write.append(t)

        if (t == 'float64') or (t == 'int64'):

            to_write.append(len(values))
            to_write.append(values.isnull().sum())
            to_write.append(values.min())
            to_write.append(values.max())
            to_write.append(values.mean())
            to_write.append(values.median())
            to_write.append(len(set(values)))


        if t == 'object':
            to_write.extend([
                len(values),
                values.isnull().sum(),
                '',
                '',
                '',
                '',
                len(set(values))
            ])

        writer.writerow(to_write)