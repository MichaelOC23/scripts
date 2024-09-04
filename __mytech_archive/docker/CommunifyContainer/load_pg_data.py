import os
import pandas as pd
import psycopg2
from psycopg2 import sql, extras
import re
import random
import string

# Connection details
user = "mytech"
password = "mytech"
host = "localhost"
port = "5400"
dbname = "tempdb"





# Connect to PostgreSQL
conn = psycopg2.connect(user=user, password=password, host=host, port=port, dbname=dbname)
# Connect to PostgreSQL
cur = conn.cursor()
# Directory containing the CSV files
csv_directory = '/Volumes/4TBSandisk/samplefiles'


# Function to sanitize table and column names
def sanitize_name(name):
    # Replace invalid characters with underscores and convert to lowercase
    sanitized = re.sub(r'\W+', '_', name).lower()
    # If the name is a single character or a number, append random characters
    if len(sanitized) == 1 or sanitized.isdigit():
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        sanitized = f"{sanitized}_{suffix}"
    return sanitized


# Drop all non-system tables from the tempdb database
cur.execute("""
    DO $$ DECLARE
        r RECORD;
    BEGIN
        FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
            EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
        END LOOP;
    END $$;
""")
conn.commit()

# Iterate through each file in the designated folder
for filename in os.listdir(csv_directory):
    if filename.endswith('.csv'):
        # Create the table name from the filename
        table_name = sanitize_name(os.path.splitext(filename)[0])

        # Load the CSV into a DataFrame
        file_path = os.path.join(csv_directory, filename)
        df = pd.read_csv(file_path)

        # Sanitize column names
        df.columns = [sanitize_name(col) for col in df.columns]

        # Generate the CREATE TABLE statement
        columns = ', '.join([f'"{col}" TEXT' for col in df.columns])
        create_table_query = sql.SQL(f'CREATE TABLE IF NOT EXISTS {table_name} ({columns});')

        # Execute the CREATE TABLE statement
        cur.execute(create_table_query)

        # Generate the INSERT INTO statement
        insert_query = sql.SQL(f'INSERT INTO {table_name} ({", ".join(df.columns)}) VALUES %s')

        # Convert DataFrame rows to list of tuples
        rows = [tuple(row) for row in df.values]

        # Use psycopg2.extras.execute_values for fast insertion
        extras.execute_values(cur, insert_query, rows)

        # Commit the transaction
        conn.commit()

# Close the cursor and connection
cur.close()
conn.close()