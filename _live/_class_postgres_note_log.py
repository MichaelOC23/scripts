import os
import pandas as pd
from datetime import datetime, timezone
import logging
import json
import psycopg2
print("Loaded NoteLog Imports")



class NoteLog:
    def __init__(self, start_folder_path=None, schema='notes', likely_key_names=None, table_prefix='', column_prefix='c'):
        self.connection_str = os.environ.get('POSTGRES_AWS_PRODUCT_DB_CONN_STRING')
        self.schema = schema
        self.notes_table_name = 'notelog'
        self.likely_key_names = likely_key_names or []
        self.table_prefix = table_prefix
        self.column_prefix = column_prefix
        # self._create_schema()
        # self._create_table()

    def connect(self):
        return psycopg2.connect(self.connection_str)
    
    def _create_schema(self):
        with self.connect() as conn:
            with conn.cursor() as cursor:
                try:
                    sql = f'CREATE SCHEMA IF NOT EXISTS {self.schema}'
                    cursor.execute(sql)
                    conn.commit()
                except Exception as e:
                    print(f"Error creating schema {self.schema}: {e}")
    
    def _create_table(self):
        self._create_schema()
        create_query = f'''
            CREATE TABLE IF NOT EXISTS {self.schema}.{self.notes_table_name}(
                id uuid DEFAULT uuid_generate_v4() NOT NULL,
                key TEXT NOT NULL UNIQUE,
                createdon TIMESTAMP NOT NULL,
                modifiedon TIMESTAMP,
                name TEXT NULL,
                path TEXT NULL,
                json_data JSONB[] NULL,
                word_history JSONB[] NULL,  
                statement_history JSONB[] NULL,  
                note TEXT  NULL,
                summary TEXT  NULL
            );'''
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_query)
                conn.commit()
            
    def fetch_note_list(self, filters=None):
        filters = filters or {}
        where_clause = ""
        params = []
        if filters:
            conditions = []
            for i, (key, value) in enumerate(filters.items()):
                conditions.append(f"{key} = %s")
                params.append(value)
            where_clause = f"WHERE {' AND '.join(conditions)}"

        query = f"SELECT * FROM {self.schema}.{self.notes_table_name} {where_clause};"
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                colnames = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=colnames)
        return df

    def fetch_note_body(self, id=None, key=None):
        if not id and not key:
            return pd.DataFrame()
        try:
            params = []
            if id is not None:
                sql = f"SELECT * FROM {self.schema}.{self.notes_table_name} WHERE id = %s;"
                params.append(id)
            elif key is not None:
                sql = f"SELECT * FROM {self.schema}.{self.notes_table_name} WHERE key = %s;"
                params.append(key)
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    rows = cursor.fetchall()
                    if not rows:
                        return pd.DataFrame()
                    colnames = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows, columns=colnames)
            return df
        except Exception as e:
            print(f"Error during SQL query execution: {e}")
            return pd.DataFrame()
    
    def insert_note(self, key, name='', path='', json_data={}, word_history=[], statement_history=[], note='', summary='', createdon=None):
        """
        Inserts a new note into the notelog table.

        Parameters:
            key (str): Unique identifier for the note.
            name (str): Name of the note.
            path (str): File path or any relevant path information.
            json_data (str): JSON-formatted string or dictionary containing additional data.
            note (str): The main content of the note.
            summary (str): A brief summary of the note.
            createdon (datetime, optional): Timestamp for when the note was created.
                                            Defaults to current UTC time if not provided.

        Returns:
            int: The ID of the inserted note if successful.
            None: If the insertion fails.
        """
        if not key:
            raise ValueError("The 'key' parameter must not be empty.")
        if createdon is None:
            createdon = datetime.now(timezone.utc)
        try:
            # Ensure json_data is a JSON string
            if isinstance(json_data, dict):
                json_data = json.dumps(json_data)
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    sql = f'''
                        INSERT INTO {self.schema}.{self.notes_table_name} 
                        (key, createdon, name, path, json_data, word_history, statement_history, note, summary)
                        VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb[], %s::jsonb[], %s, %s)
                        RETURNING id;
                    '''
                    cursor.execute(sql, (key, createdon, name, path, json_data, word_history, statement_history, note, summary))
                    inserted_id = cursor.fetchone()[0]
                    conn.commit()
                    return inserted_id
        except Exception as e:
            logging.error(f"Error inserting note: {e}")
            return None
    
    def upsert_note(self, key, name='', path='', json_data={}, word_history=[], statement_history=[], note='', summary='', createdon=None):
        """
        Inserts a new note or updates an existing one in the notelog table based on the key.

        Parameters:
            key (str): Unique identifier for the note.
            name (str): Name of the note.
            path (str): File path or any relevant path information.
            json_data (str or dict): JSON-formatted string or dictionary containing additional data.
            speaker_history (list): A list of dictionaries representing speaker history entries.
            note (str): The main content of the note.
            summary (str): A brief summary of the note.
            createdon (datetime, optional): Timestamp for when the note was created.
                                            Defaults to current UTC time if not provided.

        Returns:
            int: The ID of the inserted or updated note if successful.
            None: If the operation fails.
        """
        if not key:
            raise ValueError("The 'key' parameter must not be empty.")
        if createdon is None:
            createdon = datetime.now(timezone.utc)
        modifiedon = datetime.now(timezone.utc)  # Set modifiedon to current time

        try:           
            #json_data may be just a dict so convert it to a string and add to list if so:
            if isinstance(json_data, dict):
                json_data = [json_data]
                json_data_jsonb = json.dumps(json_data)
                # json_data_jsonb = [json.dumps(json_data)]
            else:
                json_data_jsonb = json.dumps(json_data)
                # json_data_jsonb = [json.dumps(item) for item in json_data]  # Convert each dict to JSON string
            
            # Convert speaker_history list of dictionaries to JSONB[]
            # word_history_jsonb = [json.dumps(item) for item in word_history]  # Convert each dict to JSON string
            word_history_jsonb = json.dumps(word_history)
            # statement_history_jsonb = [json.dumps(item) for item in statement_history]  # Convert each dict to JSON string
            statement_history_jsonb = json.dumps(statement_history)

            with self.connect() as conn:
                with conn.cursor() as cursor:
                    sql = f'''
                        INSERT INTO {self.schema}.{self.notes_table_name} 
                        (key, createdon, name, path, json_data, word_history, statement_history, note, summary)
                        (key, createdon, name, path, note, summary)
                        VALUES (%s, %s, %s, %s, %s::jsonb[], %s::jsonb[], %s::jsonb[], %s, %s)
                        ON CONFLICT (key) DO UPDATE SET
                            modifiedon = EXCLUDED.modifiedon,
                            name = EXCLUDED.name,
                            path = EXCLUDED.path,
                            json_data = {self.schema}.{self.notes_table_name}.json_data || EXCLUDED.json_data,
                            word_history = {self.schema}.{self.notes_table_name}.word_history || EXCLUDED.word_history,
                            statement_history = {self.schema}.{self.notes_table_name}.statement_history || EXCLUDED.statement_history,
                            note = EXCLUDED.note,
                            summary = EXCLUDED.summary
                        RETURNING id;
                    '''
                    cursor.execute(sql, (
                        key, createdon, modifiedon, name, path, json_data_jsonb, word_history_jsonb, statement_history_jsonb, note, summary
                    ))
                    upserted_id = cursor.fetchone()[0]
                    conn.commit()
                    return upserted_id
        except Exception as e:
            logging.error(f"Error upserting note: {e}")
            return None

print("Loaded NoteLog Module")
if __name__ == "__main__":
    pass
    # note = NoteLog()
    # note.upsert_note("test", "test", "test", json.dumps({"test": "test"}), "test", "test")