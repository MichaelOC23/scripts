#!Function to connect to the specified database

from calendar import c
import psycopg2
import csv
import pandas as pd
import urllib.parse as up
import os
import shared.functions_constants as constants
import streamlit as st


database_to_use = os.environ["ELEPHANTSQL_DB_URL"]
temp_directory = 'temp/'

#!Function to connect to the database
def get_connection_to_db():
    try: 
        up.uses_netloc.append("postgres")
        url = up.urlparse(database_to_use)

        conn = psycopg2.connect(database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
        )

    except psycopg2.Error as e:
        print("Cannot connect to database. Error below:")
        print(e)
        exit()

    return conn

#!Function to properly escape special characters in postgresql
def escape_postgres_params(params):
  
  escaped_params = []
  
  for param in params:
    if isinstance(param, str):
      new_param = param.replace('#', '##')
      new_param = new_param.replace('\\', '\\\\')
      new_param = new_param.replace('\'', '\'\'')
      escaped_params.append(new_param)
    else:
      escaped_params.append(param)

  return tuple(escaped_params)


#! Function to execute a SQL Command (not for SELECT statements)
def execute_sql(sql):
    try:
        #Connect
        conn = get_connection_to_db()
        cursor = conn.cursor()
        
        #Execute the SQL 
        cursor.execute(sql)
        
        if sql[:6] == "SELECT":

            #Fetch all results
            rows = cursor.fetchall()
            # print(len(rows))
            
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows, columns=columns)

            conn.close()
            return df
        else:
           
            conn.commit()
            conn.close()
        
            return True
    
    except psycopg2.Error as e:
        print(f'Error Running SQL Command: {sql}')
        print(e)
        return False


#! Function to create the document table
def create_document_table():
    try:
        conn = get_connection_to_db()
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS documents;")
        cursor.execute("""
                        CREATE TABLE documents (
                        id SERIAL PRIMARY KEY,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        expired_at TIMESTAMP,
                        filename VARCHAR(255),
                        content TEXT
                        );""")
        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        print("Error creating table")
        print(e)
        exit()  

# Function to upload file content to PostgreSQL
def upload_file_to_db(file_path, filename):
    with open(file_path, 'r') as file:
        content = file.read()
    

    conn = get_connection_to_db()
    cur = conn.cursor()
    cur.execute("UPDATE documents SET expired_at = CURRENT_TIMESTAMP WHERE expired_at IS NULL and filename = %s", (filename,))
    cur.execute("INSERT INTO documents (filename, content) VALUES (%s, %s)", (filename, content))
    
    conn.commit()
    cur.close()
    conn.close()

#
# Function to upload file content to PostgreSQL
def get_file_from_db(filename): 

    conn = get_connection_to_db()
    cur = conn.cursor()

    cur.execute("SELECT content FROM text_files WHERE expired_at is null and filename = %s", (filename,))
    file = cur.fetchone()[0]

    path_to_file = f'{temp_directory}{filename}'
    with open(path_to_file, 'w') as f:
        f.write(file)

    
    cur.close()
    conn.close()
    return  file, path_to_file

def get_file_list_from_Db(): 

    conn = get_connection_to_db()
    cur = conn.cursor()

    cur.execute("SELECT id, filename FROM documents WHERE expired_at is null")
    all_files = cur.fetchall()

    files_dataframe = pd.DataFrame(all_files, columns=['File #', 'File Name'])

    cur.close()
    conn.close()

    return files_dataframe
    

def file_storage_main():
    st.header('File Upload to PostgreSQL', divider='gray')
    st.write(get_file_list_from_Db())
    file =  st.file_uploader("Upload Files", type=['json', 'txt', 'csv'])
    if file is not None:
        file_details = {"FileName":file.name,"FileType":file.type,"FileSize":file.size}
        st.write(file_details)
        uid = constants.UNIQUE_DATE_TIME_STRING()
        uploaded_file_path = os.path.join(temp_directory, f"{uid}_{file.name}")
        with open(uploaded_file_path, 'w') as f:
            f.write(file.read().decode('utf-8'))
        upload_file_to_db(uploaded_file_path, f'{file.name}')
        st.success("File Uploaded Successfully")

# Example usage
#upload_file_to_db('/path/to/your/file.txt', 'file.txt')
    
# create_document_table()
# uid = constants.UNIQUE_DATE_TIME_STRING()
# upload_file_to_db('/Volumes/code/vscode/cool-tools/temp/dataframe/Attribute.json', f'test{uid}.json')
# conn = get_connection_to_db()
# cursor = conn.cursor()
# cursor.execute("drop table if exists documents;")
# create_document_table()
if __name__ == "__main__":     
    file_storage_main()



