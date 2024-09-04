import psycopg2
import json
from datetime import datetime, timezone
import decimal
import os
import uuid
import csv

class DataLoader:

    def __init__(self, connection_string, default_table=None):
        self.connection_string = 'postgresql://postgres:test@localhost:5432/platform' #Communify Local
        # self.connection_string = 'postgresql://mytech:mytech@localhost:5400/mytech' # Personal/MyTech Local
        self.default_table = default_table
        self.required_system_fields = ["UpdatedBy", "CreatedBy", "UpdatedOn", "CreatedOn", "NGUpdatedBy", "NGCreatedBy", "NGUpdatedOn", "NGCreatedOn", "id", "Id"]
        self.required_bus_fields = ["LocalCurrencyCode"]
        
        self.from_environment_dict = {
            "local":    {"connection_string": f'postgresql://postgres:test@localhost:5432/platform'},
            "test":     {"connection_string": f'postgresql://postgres:{"df"}@communify-test.ch6qakwu269h.us-east-1.rds.amazonaws.com/platform'},
            "product":  {"connection_string": f"postgresql://postgres:lnRipjfDXV07KjgiWXyvv@michael.ch6qakwu269h.us-east-1.rds.amazonaws.com:5432/postgres"},
            "prod":     {"connection_string": f"postgresql://postgres:lnRipjfDXV07KjgiWXyvv@michael.ch6qakwu269h.us-east-1.rds.amazonaws.com:5432/postgres"},
            }
        
        self.to_environment_dict = {
            "local":    {"connection_string": f'postgresql://postgres:test@localhost:5432/platform'},
            "test":     {"connection_string": f'postgresql://postgres:{"df"}@communify-test.ch6qakwu269h.us-east-1.rds.amazonaws.com/platform'},
            "product":  {"connection_string": f"postgresql://postgres:lnRipjfDXV07KjgiWXyvv@michael.ch6qakwu269h.us-east-1.rds.amazonaws.com:5432/postgres"},
           
            }
        
        self.table_col_defs = {}

    def get_connection(self):
        conn = psycopg2.connect(self.connection_string)
        return conn

    def isnull_or_empty(self, value):
        return value is None or value == "" 

    def get_column_types_dict(self):
        if self.table_col_defs:
            return self.table_col_defs

        conn = self.get_connection()
        query = """SELECT table_name, column_name, data_type, udt_name
                    FROM information_schema.columns c 
                    WHERE c.table_name NOT LIKE 'pg%'
                    AND c.table_schema <> 'information_schema';"""
        cur = conn.cursor()

        cur.execute(query)
        column_types = cur.fetchall()

        column_types_by_table = {}
        for record in column_types:
            table_name, column_name, data_type, udt_name = record
            if table_name not in column_types_by_table:
                column_types_by_table[table_name] = {}
            column_types_by_table[table_name][column_name] = udt_name

        with open("column_types_by_table.json", "w") as f:
            json.dump(column_types_by_table, f, indent=4)

        cur.close()
        conn.close()
        self.table_col_defs = column_types_by_table
        return self.table_col_defs

    def csv_to_list_of_dicts(self, file_path):
        with open(file_path, mode='r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            return [row for row in reader]
    
    def apply_upsert(self, base_row, new_row, merge_or_replace="MERGE"):
        if merge_or_replace == "REPLACE":
            return new_row

        for key in base_row.keys():
            if new_row.get(key) is not None:
                if merge_or_replace == "APPEND":
                    if not self.isnull_or_empty(new_row[key]):
                        if not isinstance(new_row[key], list):
                            base_row[key] = new_row[key]
                        else:
                            if base_row[key] != new_row[key] and new_row[key] not in base_row[key]:
                                base_row[key].append(new_row[key])
                elif merge_or_replace == "MERGE":
                    if not self.isnull_or_empty(new_row[key]):
                        base_row[key] = new_row[key]

        for key in new_row.keys():
            if key not in base_row:
                base_row[key] = new_row[key]
        return base_row

    def get_safe_insert_value(self, value, field_type, field_name):
        if value is None or value == "":
            return None

        try:
            if field_type == "smallint":
                return int(value)
            
            if field_type == "name":
                return str(value)
            
            if field_type == "boolean" or field_type == "bool":
                return bool(value)
            
            if field_type == "numeric":
                return decimal.Decimal(value)
            
            if field_type in ["timestamp with time zone", "timestamptz"]:
                if isinstance(value, datetime):
                    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
                return datetime.fromisoformat(value)
            
            if field_type == "bigint":
                return int(value)
            
            if field_type == "date":
                return datetime.strptime(value, '%Y-%m-%d').date()
            
            if field_type == "xid":
                return int(value)
            
            if field_type == "char":
                return str(value)
            
            if field_type in ["character varying", "text"]:
                return str(value)
            
            if field_type in ["anyarray", "ARRAY", "_ARRAY", "_text"] or field_type.startswith("_"):
                if isinstance(value, list): 
                    return value
                return [value]
            
            if field_type == "double precision" or field_type == "real":
                return float(value)
            
            if field_type in ["jsonb", "_jsonb"]:
                return json.dumps(value) if field_type == 'jsonb' else [json.dumps(item) for item in value]
            
            if field_type == "bytea":
                return bytes(value, 'utf-8')  # Ensure value is byte encoded
            
            if field_type in ["integer", "int4"]:
                return int(value)
            
            return value  # Default case, return the value as is

        except Exception as e:
            print(f"Error converting {value} in filed {field_name} of type {field_type}: {e}")
            return None

    def load_data(self, data_items, table_name, schema="metadata", operation="TRUNCATE", column_name_of_current_record_key=None, merge_or_replace="MERGE"):
        
        conn = self.get_connection()

        try:
            with conn:
                cur = conn.cursor()

                if operation == "TRUNCATE":
                    cur.execute(f'TRUNCATE TABLE {schema}."{table_name}";')
                    rows_to_load = data_items

                elif operation == "UPSERT":
                    rows_to_load = []
                    for item in data_items:
                        row_to_upsert = item.copy()
                        if column_name_of_current_record_key and item.get(column_name_of_current_record_key):
                            cur.execute(f'SELECT * FROM {schema}."{table_name}" WHERE "{column_name_of_current_record_key}" = %s',
                                        (item[column_name_of_current_record_key],))
                            existing_data = cur.fetchone()
                            if existing_data:
                                existing_data = dict(existing_data)
                                row_to_upsert = self.apply_upsert(existing_data, item, merge_or_replace)
                        rows_to_load.append(row_to_upsert)

                table_def = self.get_column_types_dict().get(table_name, {})
                load_guid = f"{uuid.uuid4()}"
                
                for row in rows_to_load:
                    for sysfield in self.required_system_fields:
                        if sysfield in table_def.keys():
                            print(f"Setting {sysfield} of type {table_def.get(sysfield)}")
                            if sysfield in[ 'Id', 'id']: 
                                row[sysfield] = f"{uuid.uuid4()}"
                                continue
                            if table_def.get(sysfield) == 'timestamptz': 
                                row[sysfield] = datetime.now()
                            else:
                                row[sysfield] = load_guid
                                
                key_list = [key for key in row.keys() if key in table_def.keys()]
                columns_list_of_dicts = [{key: f'"{key}"'} for key in key_list]
                placeholder_list = [f"%s" for _ in columns_list_of_dicts]
                values_list = []
                columns_list = []
                insert_log_list = []

                for row in rows_to_load:
                    row_values = []
                    row_columns = []
                    for col in columns_list_of_dicts:
                        col_key = list(col.keys())[0]
                        row_columns.append(col[col_key])
                        if col_key in self.required_system_fields:
                            pass
                        value = self.get_safe_insert_value(row[col_key], table_def[col_key], col_key)
                        row_values.append(value)
                        insert_log_list.append([col[col_key], value, table_def[col_key]])

                    insert_query = f'''
                        INSERT INTO {schema}."{table_name}" 
                        ({', '.join(row_columns)})
                        VALUES ({', '.join(placeholder_list)})
                    '''
                    if operation == "UPSERT":
                        pass 
                        # Not tested
                        # update_columns = [f"{col} = EXCLUDED.{col}" for col in columns]
                        # insert_query += f'ON CONFLICT ({column_name_of_current_record_key}) DO UPDATE SET {", ".join(update_columns)}'

                    with open("insert_query.txt", "w") as f:
                        f.write(f"{insert_query}" )
                    with open("insert_query_values.txt", "w") as f:
                        for log in insert_log_list:
                            f.write(f"{log}\n")
                    print("Executing query:", insert_query)
                    print("With values:", row_values)
                    cur.execute(insert_query, row_values)

                cur.close()

        except Exception as e:
            print("Error: ", e)
            raise

        finally:
            conn.close()
    
    def get_data_from_env(self, environment_from, table_name, schema="metadata", csv_file_path=None):
        conn = self.get_connection()
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(f'SELECT * FROM {schema}."{table_name}"')
                data = cur.fetchall()
                cur.close()
                return data
        except Exception as e:
            print("Error: ", e)
            raise
        finally:
            conn.close()

def load_csvs_to_postgres(self):
    
    #!#  ------>  Global Variables  <------  !#
    #! Investment Account Numbers (Excludes Private Asset Accounts)
    ACCOUNT_LIST = ["218550733086", "705625596201", "937914441711", "134367817996", "538776741796", 
                    "6953450", "999244", "6958039", "1003833", "6962628", "1008422"]

    #! Nasdaq Data Tables: These will be downloaded
    NASDAQ_TABLES = ['TICKERS', 'INDICATORS'] #, 'METRICS', 'ACTIONS', 'SP500', 'EVENTS', 'SF3', 
                                            # 'SF3A', 'SF3B', 'SEP','SF1', 'SFP', 'DAILY']
    # folder names
    source_folder = f"sources"
    archive_folder = f"archive"

    HOME = os.path.expanduser("~") #User's home directory
    DATA = f"{HOME}/code/data" # Working directory for data
    ARCHIVE = f"{DATA}/{archive_folder}" # Archive directory for prior executions
    SOURCE_DATA = f"{DATA}/{source_folder}" # Source data directory (downloaded and created data from current execution)
    LOGS = 'logs' # Directory for logs
    sic_code_file_path = f"{SOURCE_DATA}/sic_industry_codes.json"
    positions_chase_path = f"{SOURCE_DATA}/positions-chase.csv"
    securitymaster_nasdaq_path = f"{SOURCE_DATA}/NASDAQ_TICKERS.csv"
    company_description_path = f"{SOURCE_DATA}/ticker_desc_list.json"
    company_description_dictionary_path = f"{SOURCE_DATA}/ticker_desc_dictionary.json"
    sec_ticker_dictionary_path = f"{SOURCE_DATA}/sec_tickers.json"
    single_stock_price_history_path = f"{SOURCE_DATA}/single_stock_price_history.csv"

    # Data Model Entity Files
    securitymaster_entity_path = f"{SOURCE_DATA}/SecurityMasterEntity.csv"
    position_entity_path = f"{SOURCE_DATA}/PositionEntity.csv"

    # Data File Outputs (to be loaded)
    Security_Master_To_Load = f"{DATA}/SecurityMasterToLoad.csv" 
    Positions_To_Load = f"{DATA}/PositionsToLoad.csv" 
    
    csv = DataLoader("dbname=platform user=postgres password=test host=localhost port=5432")

    HOME = os.path.expanduser("~") #User's home directory
    DATA = f"{HOME}/code/data" # Working directory for data
    Security_Master_To_Load = f"{DATA}/SecurityMasterToLoad.csv" 

    # Load the SecurityMaster and Position CSVs to the database
    # csv.load_data(Security_Master_To_Load, "SecurityMaster")
    csv.load_data(Positions_To_Load, "Position")


load_csvs_to_postgres()