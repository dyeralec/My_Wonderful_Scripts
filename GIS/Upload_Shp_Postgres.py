import psycopg2
from osgeo import ogr
import pandas as pd
import ogr2ogr

#database connection properties This tests that you connection to postgres is sucessful.
#hostname = '10.50.45.73'
#username = 'postgres'
#password = 'postgres'
#database = 'BOEM_IAA'
#conn = psycopg2.connect( host=hostname, user=username, password=password, dbname=database )
#df = pd.read_sql_query("SELECT * FROM spatial_ref_sys LIMIT 12;", conn)
#print(df)

# using ogr2ogr in python this function will upload a shp file to the postgres database
def upload_file(filename):
    #note: main is expecting sys.argv, where the first argument is the script name
    #so, the argument indices in the array need to be offset by 1
    ogr2ogr.main(["","-f", "PostgreSQL", "PG:host=10.50.45.73 user=postgres dbname=BOEM_IAA password=postgres", filename])

# this is the path to the shp file and then executing the function to load the data to postgres
# this can be converted to loop through shape files through a folder.
shpfilepath = r"E:\GOM\GomStates\gom_states.shp"
upload_file(shpfilepath)