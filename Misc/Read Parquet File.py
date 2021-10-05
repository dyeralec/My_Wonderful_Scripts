import pyarrow.parquet as pq
from sqlalchemy import create_engine
import os

in_path = r"P:\02_DataWorking\Carbon Storage Data\SmartSearch results 9_20_2021\output_cs_smartsearch\paige1602_sid761c30552e7906b210d516e6ef7c876d_spark_recommendations_parquet_52"
database_name = 'geohazard'

if os.path.isfile(in_path):
    # open parquet file and convert to pandas dataframe
    df = pq.read_table(in_path)
    df = df.to_pandas()

    # lowercase all columns
    df.columns = [c.lower() for c in df.columns]  # postgres doesn't like capitals or spaces
    # link to database on postgres server
    engine = create_engine('postgresql://postgres:l1v1ngD4t4b4s3!@10.67.10.38:5005/{}'.format(database_name))
    # create name for table export
    export_name = in_path.replace('.parquet', '')
    # send df to postgres database
    df.to_sql(export_name, engine)

else:
    # change directory
    os.chdir(in_path)
    # loop over all files in directory
    for file in os.listdir(in_path):
        # only open file if it is a parquet
        if file.endswith('.parquet'):

            print(file)

            # open parquet file and convert to pandas dataframe
            df = pq.read_table(file)
            df = df.to_pandas()

            # lowercase all columns
            df.columns = [c.lower() for c in df.columns]  # postgres doesn't like capitals or spaces
            # link to database on postgres server
            engine = create_engine('postgresql://postgres:l1v1ngD4t4b4s3!@10.67.10.38:5005/{}'.format(database_name))
            # send df to postgres database
            df.to_sql(file.replace('.parquet', ''), engine)