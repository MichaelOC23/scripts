import os
import sys
import pandas as pd
import streamlit as st
from _class_streamlit import streamlit_mytech 
import json
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import uuid
import re

import chardet
from decimal import Decimal
import psycopg2


stm = streamlit_mytech()
stm.set_up_page(page_title_text="DataGen: US Prospects",
                session_state_variables=[{"TransStatus": False}]) 

st.session_state['show_table_pages'] = False
nav_dict={}

class create_new_grid():
    def __init__(self, 
                 col_val_list=None,
                 # Column Options
                 minWidth=100,
                 maxWidth=400, 
                 editable=True, 
                 filter=True, 
                 resizable=True, 
                 sortable=True, 
                 enableRowGroup=True, 
                 enablePivot=True,  # Ensure enablePivot is set to True
                 currency_symbol='$',

                 # Grid Options
                 rowSelection="multiple", 
                 use_checkbox=True,
                 rowMultiSelectWithClick=False, 
                 suppressRowDeselection=False, 
                 suppressRowClickSelection=False, 
                 groupSelectsChildren=True, 
                 groupSelectsFiltered=True, 
                 preSelectAllRows=False,
                 enable_pagination=True,

                 # Sidebar Options
                 show_SideBar=True,
                 show_filters=False,
                 show_columns=True,
                 show_defaultToolPanel=True,
                 hide_by_default=False
                 ):
        
        # if dataframe is None:
        #     print ('ERROR: No dataframe provided')
        #     return
        
        self.show_SideBar = show_SideBar
        self.show_filters = show_filters
        self.defaultToolPanel = show_defaultToolPanel
        self.show_columns = show_columns
        self.minWidth = minWidth
        self.maxwidth = maxWidth
        
        # self.dataframe = dataframe
        self.col_val_list = col_val_list
        
        self.editable = editable
        self.filter = filter
        self.resizable = resizable
        self.sortable = sortable
        self.enableRowGroup = enableRowGroup
        self.enablePivot = enablePivot
        self.rowSelection = rowSelection
        self.use_checkbox = use_checkbox
        self.enable_pagination = enable_pagination
        self.rowMultiSelectWithClick = rowMultiSelectWithClick
        self.suppressRowDeselection = suppressRowDeselection
        self.suppressRowClickSelection = suppressRowClickSelection
        self.groupSelectsChildren = groupSelectsChildren
        self.groupSelectsFiltered = groupSelectsFiltered
        self.preSelectAllRows = preSelectAllRows
        self.currency_symbol = currency_symbol
        self.hide_by_default = hide_by_default
    
    def is_date_or_empty(self, val):
        if pd.isnull(val):
            return True
        val_str = str(val).strip()
        if val_str == '':
            return True
        try:
            pd.to_datetime(val_str)
            return True
        except (ValueError, TypeError):
            return False
    
    def create_default_grid(self, dataframe):
          
        if self.is_none_or_empty(dataframe):
            print ('ERROR: No dataframe provided')
            return
        # Apply formatting and right alignment to numeric columns in Ag-Grid
        
        builder = GridOptionsBuilder.from_dataframe(dataframe)
        
        builder.configure_selection(self.rowSelection  , self.use_checkbox)
        builder.configure_pagination(self.enable_pagination)
        builder.configure_side_bar(self.show_filters, self.show_columns, self.defaultToolPanel)  # Enable the sidebar with default options

        # for col in dataframe.select_dtypes(include=[float, int]).columns:
        #     builder.configure_column(col, type=["numericColumn", "customNumericFormat"], precision=2, valueFormatter="x.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })", cellStyle={'text-align': 'right'})
        
        # Add enablePivot option to column definitions
        gridoptions = builder.build()
        gridoptions['enableCharts'] = True  
        gridoptions['enableRangeSelection'] = True
        
        


        new_col_defs = []
        for col_list_item in gridoptions['columnDefs']:
            # !FIXME: Figure out Col Name Override
            # col_list_item['headerName']= col['headerName']            
            col_list_item['field'] =  col_list_item['headerName']
            col_list_item['filter'] = filter
            col_list_item['resizable'] = self.resizable
            col_list_item['sortable'] = self.sortable
            col_list_item['minWidth'] = self.minWidth # Minimum width in pixels; other values are integers
            col_list_item['editable'] = self.editable # Minimum width in pixels; other values are integers
            col_list_item['maxWidth'] = self.maxwidth  # Maximum width in pixels; other values are integers
            col_list_item['flex'] = 1  # Flex sizing; other values are integers
            
            # Check if 'type' key exists in col
            col_list_item['type'] = [] # 
            # print(f"dtype of {col_list_item['headerName']}: {dataframe[col_list_item['headerName']].dtype}")
            if 'targetmin' in col_list_item['headerName']:
                pass
            if pd.api.types.is_numeric_dtype(dataframe[col_list_item['headerName']]):
                col_list_item['valueFormatter'] = "function(params) { return '$' + params.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }"
                col_list_item['cellStyle'] = {'textAlign': 'right'}

            # Editing
            col_list_item['editable'] = True  # False
            col_list_item['cellEditor'] = 'agTextCellEditor'  # 'agSelectCellEditor', 'agRichSelectCellEditor', 'agLargeTextCellEditor', custom editors

            # Sorting & Filtering
            col_list_item['sortable'] = True  # False
            col_list_item['sort'] = 'asc'  # 'desc', None
            col_list_item['filter'] = True  # False, or a specific filter type like 'agNumberColumnFilter', 'agTextColumnFilter'
            # col_list_item['filterParams'] = {}  # Parameters for the filter, depends on the filter type

            # Grouping & Aggregation
            col_list_item['groupable'] = True  # False
            col_list_item['enableRowGroup'] = True  # False
            col_list_item['rowGroup'] = False  # True, enables row grouping
            col_list_item['rowGroupIndex'] = None  # Index for row grouping; other values are integers
            col_list_item['enablePivot'] = True  # False
            col_list_item['pivot'] = False  # True, enables pivoting
            col_list_item['pivotIndex'] = None  # Index for pivoting; other values are integers
            
            if pd.api.types.is_numeric_dtype(dataframe[col_list_item['headerName']]):
                    col_list_item['aggFunc'] = 'sum' # Set aggregation function to sum for numeric columns
            else:
                col_list_item['aggFunc'] = 'max'  # 'min', 'max', 'avg', 'count', custom aggregation functions
            
            # Column Behavior
            col_list_item['checkboxSelection'] = False  # True, allows the column to have a checkbox for selection
            col_list_item['rowDrag'] = False  # True, enables row dragging
            col_list_item['lockPosition'] = False  # True, locks the column position
            col_list_item['lockVisible'] = False  # True, locks the column visibility
            col_list_item['lockPinned'] = False  # True, locks the column pinning (left or right)

            # Pinning
            col_list_item['pinned'] = None  # 'left', 'right', None for not pinned

            # Tooltip
            col_list_item['tooltipField'] = None  # Field name for a tooltip; other values are strings
            col_list_item['tooltipValueGetter'] = None  # A JavaScript function or string expression to get the tooltip value

            # Column Visibility
            col_list_item['hide'] = self.hide_by_default  # True to hide the column

            
            col_list_item['headerTooltip'] = None  # Tooltip for the column header; other values are strings
            col_list_item['headerCheckboxSelection'] = False  # True, allows a checkbox in the header for selecting all rows
            col_list_item['headerCheckboxSelectionFilteredOnly'] = False  # True, only selects filtered rows
            col_list_item['floatingFilter'] = False  # True, enables floating filters under the header
            col_list_item['menuTabs'] = ['filterMenuTab', 'generalMenuTab', 'columnsMenuTab']  # Tabs to show in the column menu
            col_list_item['sortableTooltip'] = False  # True to show a tooltip when the column is sorted
            col_list_item['columnGroupShow'] = None  # 'open', 'closed', None; controls when the column is shown in a group
            
            # Specifically set MarketValue to sum when pivoted
            if col_list_item['headerName'] == 'MarketValue':
                col_list_item['headerName'] = self.format_col_as_currency(col_list_item)
                # newcol['aggFunc'] = 'sum'

            new_col_defs.append(col_list_item)
        
        

        gridoptions['columnDefs'] = new_col_defs
        gridoptions['domLayout'] = 'normal'
        gridoptions['paginationAutoPageSize']=False
        gridoptions['paginationPageSize'] =500
        
        
        return gridoptions
    
    def format_col_as_currency(self, col):
        col["type"]= ["numericColumn","numberColumnFilter", "customNumericFormat"]
        col["custom_currency_symbol"]= self.currency_symbol
        col['hide'] = False  # True to hide the column
        col['precision'] = 2  # True to hide the column
        return col
    
    def is_none_or_empty(self, df):
            resp = False
            try:
                return df is None or df.empty
            except:
                return resp   
            
    def display_grid(self, dataframe=None, 
             grid_options=None, 
             height=1500, 
             row_selection=True, 
             on_row_selected=None, 
             fit_columns_on_grid_load=False, 
             update_mode=GridUpdateMode.SELECTION_CHANGED, 
             data_return_mode="as_input", 
             conversion_errors='coerce', 
             theme='balham', 
             custom_css=None):
    
        if self.is_none_or_empty(dataframe):
            print ('ERROR: No dataframe provided')
            return

        # print(f"Type of dataframe before processing: {type(dataframe)}")

        if grid_options is None:
            grid_options = self.create_default_grid(dataframe=dataframe)
        
        # print(f"Type of dataframe after creating default grid: {type(dataframe)}")
     
        grid_return = AgGrid(dataframe, 
                        grid_options, 
                        height=height, 
                        row_selection=row_selection,
                        on_row_selected=on_row_selected,
                        fit_columns_on_grid_load=fit_columns_on_grid_load, 
                        update_mode=update_mode, 
                        data_return_mode=data_return_mode, 
                        conversion_errors=conversion_errors,
                        enable_enterprise_modules=True,
                        theme=theme, 
                        custom_css=custom_css, key=str(uuid.uuid4()))

        # print(f"Type of dataframe before processing: {type(dataframe)}")
        
        return grid_return



class CSVToPostgres:
    def __init__(self, start_folder_path=None, schema='datagen', likely_key_names = [], table_prefix='', column_prefix='c'):
        
        self.connection_str = os.environ.get('POSTGRES_AWS_PRODUCT_DB_CONN_STRING')
        if not start_folder_path:
            start_folder_path = sys.argv[1] if len(sys.argv) > 1 else "/Users/michasmi/Downloads/Goldmine/UsefulPart01" #os.getcwd()
            self.folder_path = start_folder_path
        self.dataframe_list = []
        self.force_repickling = True
        self.schema = schema
        self.likely_key_names = likely_key_names
        self.table_prefix = table_prefix
        self.column_prefix = column_prefix
        self.dataframe_analysis = None
        
    def connect(self):
        conn = psycopg2.connect(self.connection_str)
        return conn
    
    def create_schema_safely(self,  schema):
        self._create_schema(schema)
    
    def _create_schema(self, schema):
        with self.connect() as conn:
            try:
                # conn.cursor()o create the schema
                conn.cursor().execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")
                conn.commit()
            except Exception as e:
                # Log the error for debugging purposes (or handle it differently)
                print(f"Error creating schema {schema}: {e}")

    def clean_column_names(self, columns):
        # Clean column names to comply with PostgreSQL conventions
        return [re.sub(r'\W+', '_', col.lower()) for col in columns]

    def generate_create_table_query(self, df, table_name, schema=None ):
        
        self._create_schema( schema)
        
        if not schema:
            schema = self.schema
        # Clean up the dataframe column names
        cleaned_columns = self.clean_column_names(df.columns)
        df.columns = cleaned_columns

        # Start building the create table query
        create_query = f'CREATE TABLE IF NOT EXISTS {schema}.{table_name} ('
        
        # Add the GUID primary key
        # create_query += 'id serial4 NOT NULL, '
        create_query += ''

        # Add columns based on DataFrame dtypes
        for col in df.columns:
            dtype = df[col].dtype
            if dtype == 'O':
                create_query += f'{col} TEXT, '
            elif dtype == 'float64' or dtype == 'int64' or isinstance(df[col].iloc[0], Decimal):
                create_query += f'{col} DECIMAL, '
            elif dtype == 'datetime64[ns]':
                create_query += f'{col} TEXT, '  # Treat dates as strings

        # Remove trailing comma and space
        create_query = create_query.rstrip(', ') + ');'

        return create_query

    def load_folder_of_csvs_to_postgres(self, max_concurrent_tasks=1):

        # Collecting CSV paths and preparing load tasks
        loaded_tables = self.execute_select_query (f"""SELECT table_name FROM information_schema.tables c
        where c.table_schema = 'datagen'""")
        
        results = []
        all_tables = []
        for table_str in loaded_tables['table_name']:
            all_tables.append(table_str.upper())
        
        for file in os.listdir(self.folder_path):
            if file.endswith('.csv'):
                try: 
                    table_name= self.create_table_name_from_csv_file_name(file)  
                    if table_name.upper() not in all_tables:
                        csv_path = os.path.join(self.folder_path, file)
                        result = self.load_csv_to_postgres(csv_file_path=csv_path)
                        results.append(result)
                    else:
                        print('Table already exists in Postgres: ', table_name)
                        continue
                except:
                    print('Error loading CSV file: ', file)
                    pass
        

        

        # Returning all results
        return results
    
    def create_table_name_from_csv_file_name(self, csv_path):
        table_name = os.path.basename(csv_path).split('.')[0]
        table_name = table_name.replace(' ', '')   # Replace spaces with blanks
        table_name = table_name.replace('-', '')   # Replace dashes with blanks
        table_name = table_name.replace('_', '')   # Replace unerscores with blanks
        
        return table_name
    
    def load_csv_to_postgres(self, csv_file_path):

        csv_folder_path = os.path.dirname(csv_file_path)
        csv_file_name = os.path.basename(csv_file_path)
        clean_csv_export_path = os.path.join(csv_folder_path, 'clean', csv_file_name)
        table_name =  self.create_table_name_from_csv_file_name(csv_file_name)

        encoding =  self.detect_encoding(csv_file_path)
        df =  self.type_df(csv_file_path, encoding)
        
        df.to_csv(
                clean_csv_export_path,
                sep=',',                 # CSV separator
                index=False,             # No index in the CSV
                header=True,             # Include headers (column names)
                na_rep='',               # Empty string for NaN values
                float_format='%.2f',     # Format floats with 2 decimal places (for SQL compatibility)
                mode='w',                # Write mode (overwrite)
                encoding='utf-8'         # UTF-8 encoding
            )

        if df is None or df.empty:
            print(f'The DataFrame for {table_name} is empty or not properly loaded.')
            print (f"Clean CSV export does not exist at {clean_csv_export_path} or file is empty.")
            return [False, csv_file_name]
        
        create_table_query =  self.generate_create_table_query(df, table_name, schema=self.schema)
        with self.connect() as conn:
            conn.cursor().execute(f'DROP TABLE IF EXISTS {self.schema}.{table_name};')
            conn.commit()
            
            conn.cursor().execute(create_table_query)
            conn.commit()

        # Bulk insert using psycopg2 and COPY
        with psycopg2.connect(dsn=self.connection_str) as pg_conn:
            cursor = pg_conn.cursor()
            with open(clean_csv_export_path, 'r') as f:
                cursor.copy_expert(f'COPY {self.schema}.{table_name} FROM STDIN WITH CSV HEADER', f)
            cursor.close()
            pg_conn.commit()
        
        primary_key_sql = f"ALTER TABLE {self.schema}.{table_name} ADD COLUMN id SERIAL4;"
        for key in self.likely_key_names:
            try:
                if df[key].is_unique:
                    print(f"{table_name} is unique. Assigning it as primary key instead of creating an id field.")
                    primary_key_sql = f"ALTER TABLE {self.schema}.{table_name} ADD PRIMARY KEY ({key});"
                    break
                print(f'{table_name} loaded and assign pk of {key}')
            except KeyError:
                pass
        with self.connect() as conn:
            print(f"\n{primary_key_sql}")
            conn.cursor().execute(primary_key_sql)
            conn.commit()
        
        return {table_name: True}

    def clean_str(self, str_text, prefix=None):
        if prefix is None:
            prefix = self.column_prefix
        clean_col = re.sub(r'\W+', '', str_text.lower())
        clean_col = f"{prefix}{clean_col.replace('"', '')}"
        return clean_col

    def type_df(self, file_path, encoding, max_rows=1000):
        def check_convertible_to_datetime(column):
            def is_convertible(value):
                if pd.isnull(value) or value == '':
                    return True
                try:
                    pd.to_datetime(value)
                    return True
                except (ValueError, TypeError):
                    return False
            return column.apply(is_convertible).all()

        def is_numeric_or_empty(s):
            s_float = pd.to_numeric(s, errors='coerce')
            return s_float.notna() | s.isna()
        
        def sanitize_col_names(df):
            # Create a dictionary to safely rename the fields
            rename_dict = {}
            df.columns = df.columns.str.strip()
            for col in df.columns:
                clean_col_name = self.clean_str(col, "c")
                rename_dict[col] = clean_col_name.strip()
            df = df.rename(columns=rename_dict)
            return df

        # Reading the CSV file
        print(f"About to read csv {os.path.basename(file_path)} with encoding: {encoding}")
        df = pd.read_csv(file_path, on_bad_lines='warn', encoding=encoding)
        
        # Process each column
        for col in df.columns:
            sample = df[col].iloc[:max_rows]
            
            if is_numeric_or_empty(sample).all():
                # Set its type to number
                df[col] = df[col].replace(r'^\s*$', '0', regex=True).fillna('0')
                try:
                    df[col] = df[col].astype(float).fillna(0)
                except ValueError:
                    continue
                
            elif check_convertible_to_datetime(sample):
                try:
                    # Set its type to datetime
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except ValueError:
                    continue
            else:
                df[col] = df[col].astype(str).replace({pd.NA: None, 'nan': None, 'NaT': None, None: None, '<NA>': None})

            
            # Set all string and date columns to None (to be more consistent in replacement)
            df[col] = df[col].replace({pd.NA: None, 'nan': None, 'NaT': None, None: None, '<NA>': None})

        # Sanitize column names
        df = sanitize_col_names(df)
        
        # Clean Up Tasks
        # 1. Remove empty rows and columns
        df = df.replace('', pd.NA).dropna(how='all')  # Replace empty strings with pd.NA and drop completely empty rows
        
        # 2. Ensure no whitespace in column names
        df.columns = df.columns.str.strip()
        
        # 3. Remove newline characters from all fields in the DataFrame
        def sanitize_cell(x):
            if isinstance(x, str):
                return x.replace('\n', ' ').replace('\r', ' ')
            else:
                return x

        # Apply the sanitize_cell function to each element in the DataFrame
        df = df.apply(lambda column: column.map(sanitize_cell))

        
        # 4. Drop rows where all elements are NaN (if it's not redundant with step 1)
        df = df.dropna(how='all')
        
        # 5. Handle NaNs for specific types
        for col in df.columns:
            if pd.api.types.is_integer_dtype(df[col]):
                df[col] = df[col].fillna(0).astype(pd.Int64Dtype())  # Handle integer columns with NaNs
            elif pd.api.types.is_float_dtype(df[col]):
                df[col] = df[col].fillna(0.0)  # Handle float columns with NaNs
            elif pd.api.types.is_string_dtype(df[col]):
                df[col] = df[col].fillna('')  # Handle string columns with NaNs
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].fillna(pd.Timestamp('1970-01-01'))  # Handle datetime columns with NaNs
        
        # 6. Reset the index after dropping rows
        df = df.reset_index(drop=True)
        
        return df
    
    def detect_encoding(self, file_path):
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            return result['encoding']

    def fetch_all_rows(self, table_name, filters=None):
        filters = filters or {}
        where_clause = ""
        
        # Generate where clause if filters exist
        if filters:
            conditions = [f"{key} = ${i+1}" for i, key in enumerate(filters.keys())]
            where_clause = f"WHERE {' AND '.join(conditions)}"

        # Query to fetch all rows
        query = f"SELECT * FROM {table_name} {where_clause};"

    
        with self.connect() as conn:
            cursor = conn.cursor()
            
            if filters:
                cursor.execute(query, *filters.values())
                rows = cursor.fetchall()
                cursor.close()
            else:
                cursor.execute(query)
                rows = cursor.fetchall()
                cursor.close()

    
        # Convert fetched rows to a list of dictionaries
        row_dicts = [dict(row) for row in rows]
        
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(row_dicts)
        
        return df
          
    def execute_select_query(self, sql):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                cursor.close()
                
                if not rows:
                    return pd.DataFrame()  # Return an empty DataFrame if no rows were fetched
                
                # Retrieve column names
                colnames = [desc[0] for desc in cursor.description]
                
                # Convert fetched rows to a DataFrame
                df = pd.DataFrame(rows, columns=colnames)
                
                return df

        except Exception as e:
            print(f"Error during SQL query execution: {e}")
            return pd.DataFrame()  # Return an empty DataFrame in case of error


if __name__ == '__main__':

    def main():
        
        #? ##########
        #? NAVIGATION
        #? ##########
                
        csvpg = CSVToPostgres(schema='datagen', likely_key_names=['cfilingid', 'creferenceid', 'ccik'], table_prefix='t', column_prefix='c',)
        # csv_file_list = csvpg.load_folder_of_csvs_to_postgres()
        # print (csv_file_list)

        
        merge_fields =  []  

        Base_A_Fields = [ #"FormVersion","DateSubmitted",
                        "1A", "1F1-Street 1","1F1-Street 2","1F1-City","1F1-State","1F1-Country","1F1-Postal","1F1-Private", "1J-Email","1J2-Name", 
                        "Reg Contact-Name","Reg Contact-Title","Reg Contact-Phone","Reg Contact-Email",
                        "1L","1M","1N","1N-CIK","1O","1OAmount","1P",
                        "5A","5B1","5B2","5B3","5B4","5B5","5B6","5C1","5C2","5D1a","5D1b","5D1c","5D1d","5D1e","5D1f","5D1g","5D1h","5D1i","5D1j","5D1k","5D1l",
                        "5D1m","5D1n","5D1n Other","5D2a","5D2b","5D2c","5D2g","5D2h","5D2i","5D2j","5D2k","5D2l","5D2m","5D2n","5D3a","5D3b","5D3c","5D3d","5D3e","5D3f","5D3g","5D3h",
                        "5D3i","5D3j","5D3k","5D3l","5D3m","5D3n","5E1","5E2","5E3","5E4","5E5","5E6","5E7","5E7-Other","5F1","5F2a","5F2b","5F2c","5F2d","5F2e","5F2f","5F3","5G1","5G2",
                        "5G3","5G4","5G5","5G6","5G7","5G8","5G9","5G10","5G11","5G12","5G12-Other","5H","5H-Other","5I1","5I2a","5I2b","5I2c","5J1","5J2","5K1","5K2","5K3","5K4",
                        "6A1","6A2","6A3","6A6","6A5","6A7","6A8","6A9","6A10","6A11","6A14","6A14-Other","6B1","6B2","6B3",
                        #  "7A1","7A2","7A3","7A4","7A5","7A6","7A7","7A8","7A9","7A10","7A11","7A12","7A13","7A14","7A15","7A16","7B",
                        # "8A1","8A2","8A3","8B1","8B2","8B3","8C1","8C2","8C3","8C4","8D","8E","8F","8G1","8G2","8H1","8H2","8I",
                        "9A1a","9A1b","9A2a","9A2b","9D1","9D2","9E", #"9B1a","9B1b","9B2a","9B2b","9C1","9C2","9C3","9C4", "9F",    "10A",
                        #  "11","11A1","11A2","11B1","11B2","11C1","11C2","11C3","11C4","11C5","11D1","11D2","11D3","11D4","11D5","11E1","11E2","11E3","11E4","11F","11G","11H1a","11H1b","11H1c","11H2",
                        "12A","12B1","12B2","12C1","12C2","Signatory","Title"]
        Base_B_Fields = ["2A1","2A2","2A3","2A4","2A5","2A6","2A7","2A8","2A9","2A10","2A11","2A12","2A13",]
                        # "2-AL","2-AK","2-AZ","2-AR","2-CA","2-CO","2-CT","2-DE","2-DC","2-FL","2-GA","2-HI","2-ID","2-IL","2-IN","2-IA","2-KS","2-KY","2-LA","2-ME","2-MD","2-MA","2-MI","2-MN","2-MS","2-MO","2-MT","2-NE","2-NV","2-NH","2-NJ","2-NM","2-NY","2-NC","2-ND","2-OH","2-OK","2-OR","2-PA","2-PR","2-RI","2-SC","2-SD","2-TN","2-TX","2-UT","2-VT","2-VA","2-WA","2-WV","2-WI","2-GU","2-VI",
                        # "3A","3A-Other","3B","3C","3C-State","3C-Country"
        D_10B_Fields =  ["Full Legal Name","CIK Number"]
        FiveK1_Fields = ["5K(1)(a)(i)MID","5K(1)(a)(i)EOY","5K(1)(a)(ii)MID","5K(1)(a)(ii)EOY","5K(1)(a)(iii)MID","5K(1)(a)(iii)EOY","5K(1)(a)(iv)MID","5K(1)(a)(iv)EOY","5K(1)(a)(v)MID","5K(1)(a)(v)EOY","5K(1)(a)vi)MID","5K(1)(a)vi)EOY","5K(1)(a)(vii)MID","5K(1)(a)(vii)EOY","5K(1)(a)(viii)MID","5K(1)(a)(viii)EOY","5K(1)(a)(ix)MID","5K(1)(a)(ix)EOY","5K(1)(a)(x)MID","5K(1)(a)(x)EOY","5K(1)(a)(xi)MID","5K(1)(a)(xi)EOY","5K(1)(a)(xii)MID","5K(1)(a)(xii)EOY","5K(1)(a)(xii) Description","5K(1)(b)(i)","5K(1)(b)(ii)","5K(1)(b)(iii)","5K(1)(b)(iv)","5K(1)(b)(v)","5K(1)(b)(vi)","5K(1)(b)(vii)","5K(1)(b)(viii)","5K(1)(b)(ix)","5K(1)(b)(x)","5K(1)(b)(xi)","5K(1)(b)(xii)","5K(1)(b)(xii) Description"]
        FiveK2_Fields = [] #"5K(2)(a)(i)(1)10","5K(2)(a)(i)(2)10","5K(2)(a)(i)(3)(a)10","5K(2)(a)(i)(3)(b)10","5K(2)(a)(i)(3)(c)10","5K(2)(a)(i)(3)(d)10","5K(2)(a)(i)(3)(e)10","5K(2)(a)(i)(3)(f)10","5K(2)(a)(i)(1)10-149","5K(2)(a)(i)(2)10-149","5K(2)(a)(i)(3)(a)10-149","5K(2)(a)(i)(3)(b)10-149","5K(2)(a)(i)(3)(c)10-149","5K(2)(a)(i)(3)(d)10-149","5K(2)(a)(i)(3)(e)10-149","5K(2)(a)(i)(3)(f)10-149","5K(2)(a)(i)(1)150","5K(2)(a)(i)(2)150","5K(2)(a)(i)(3)(a)150","5K(2)(a)(i)(3)(b)150","5K(2)(a)(i)(3)(c)150","5K(2)(a)(i)(3)(d)150","5K(2)(a)(i)(3)(e)150","5K(2)(a)(i)(3)(f)150","5K(2)(a)(i)Desc","5K(2)(a)(ii)(1)10","5K(2)(a)(ii)(2)10","5K(2)(a)(ii)(3)(a)10","5K(2)(a)(ii)(3)(b)10","5K(2)(a)(ii)(3)(c)10","5K(2)(a)(ii)(3)(d)10","5K(2)(a)(ii)(3)(e)10","5K(2)(a)(ii)(3)(f)10","5K(2)(a)(ii)(1)10-149","5K(2)(a)(ii)(2)10-149","5K(2)(a)(ii)(3)(a)10-149","5K(2)(a)(ii)(3)(b)10-149","5K(2)(a)(ii)(3)(c)10-149","5K(2)(a)(ii)(3)(d)10-149","5K(2)(a)(ii)(3)(e)10-149","5K(2)a)(ii)(3)(f)10-149","5K(2)(a)(ii)(1)150","5K(2)(a)(ii)(2)150","5K(2)(a)(ii)(3)(a)150","5K(2)(a)(ii)(3)(b)150","5K(2)(a)(ii)(3)(c)150","5K(2)(a)(ii)(3)(d)150","5K(2)(a)(ii)(3)(e)150","5K(2)(a)(ii)(3)(f)150","5K(2)(a)(ii)Desc","5K(2)(b)(1)10","5K(2)(b)(2)10","5K(2)(b)(1)10-149","5K(2)(b)(2)10-149","5K(2)(b)(1)150","5K(2)(b)(2)150","5K(2)(b)Desc"]
        FiveK3_Fields = [] #"5K(3)(a)","5K(3)(b)","5K(3)(c) City","5K(3)(c) State","5K(3)(c) Country","5K(3)(d)","5K(3)(e)","5K(3)(f)","5K(3)(g)"]
        SixB2_Fields =  ["Primary Business","Business Name"]
        SixB3_Fields =  ["Other Products and Services"] #,"Business Name"]
        Sch_D_7A =      ["FilingID","ReferenceID","SEC Number or Other","CRD Number","Type"]
        other_files = []


        merge_fields = Base_A_Fields + Base_B_Fields + D_10B_Fields +FiveK1_Fields + FiveK2_Fields + FiveK3_Fields + SixB2_Fields + SixB3_Fields + Sch_D_7A
        merge_fields = [x.replace(" ", "").lower() for x in merge_fields]
        merge_fields = list(set(merge_fields))
        
        
        meta1_t  = "File Tables"
        meta2_t  = "Field Definitions"
        meta3_t  = "Unique cFilingID"
        meta4_t  = "Unique cReferenceID"
        meta5_t  = "All Table Keys"
        
        table_name_dict = {
            "iaschrotherbusinessnames1c2024010120240331": "ADV. 1C Other Bus. Names",
            "iaschrcik1h2024010120240331": "Sched.R Relying Advisor CIK",
            "iaschr4d2024010120240331": "Sched.R4D Disc. Hist.",
            "iascheduler4c2024010120240331": "Sched.R4C",
            "iascheduledforeignregulatoryauthority2024010120240331": "Sched.D For. Reg. Auth.",
            "iascheduled9c2024010120240331": "Sched.D9C Private Funds",
            "iascheduled7b22024010120240331": "Sched.D7B2",
            "iascheduled7b1a7f2024010120240331": "Sched.D7B1A7F Affiliations",
            "iascheduled7b1a7d22024010120240331": "Sched.D7B1A7D2 RIA of BD",
            "iascheduled7b1a7d12024010120240331": "Sched.D7B1A7D1 BD Affiliation",
            "iascheduled7b1a6b2024010120240331": "Sched.D7B1A6B Insurance Advisor",
            "iascheduled7b1a52024010120240331": "Sched.D7B1A5",
            "iascheduled7b1a3b2024010120240331": "Sched.D7B1A3B",
            "iascheduled7b1a3a2024010120240331": "Sched.D7B1A3A",
            "iascheduled7b1a28websites2024010120240331": "Sched.D7B1A28 Websites",
            "iascheduled7b1a282024010120240331": "**Sched.D7B1A28",
            "iascheduled7b1a262024010120240331": "Sched.D7B1A26",
            "iascheduled7b1a222024010120240331": "Sched.D7B1A22",
            "iascheduled7b1a18b2024010120240331": "Sched.D7B1A18B",
            "iascheduled7b1a17b2024010120240331": "Sched.D7B1A17B",
            "iascheduled7b12024010120240331": "Sched.D7B1",
            "iascheduled7acik2024010120240331": "Sched.D7A CIK",
            "iascheduled7a2024010120240331": "Sched.D7A",
            "iascheduled7a10b2024010120240331": "Sched.D7A10B",
            "iascheduled6b32024010120240331": "Sched.D6B3",
            "iascheduled6b22024010120240331": "**Sched.D6B2",
            "iascheduled6a2024010120240331": "Sched.D6A",
            "iascheduled5k32024010120240331": "Sched.D5K3",
            "iascheduled5i22024010120240331": "Sched.D5I2",
            "iascheduled5g32024010120240331": "Sched.D5G3",
            "iascheduled42024010120240331": "Sched.D4",
            "iascheduled2arelated2024010120240331": "Sched.D2A Related",
            "iascheduled2aexemptiveorder2024010120240331": "Sched.D2A Exemptive Order",
            "iascheduled2a2024010120240331": "Sched.D2A",
            "iascheduled2a120day2024010120240331": "Sched.D2A 1120 Day",
            "iascheduled1b2024010120240331": "?Sched.D1B",
            "iascheduled10b2024010120240331": "?Sched.D10B",
            "iascheduled10a2024010120240331": "?Sched.D10A",
            "iascheduleab2024010120240331": "**Sched.AB",
            "iaadvbasea2024010120240331": "**ADV Base A",
            "ia1e2additionalcrd2024010120240331": "ADV.1E2 Additional CRD",
            "ia1d3cik2024010120240331": "ADV.1D3 CIK",
            "advfilingtypes2024010120240331": "ADV Filing Types"         }
        
        def meta1():
            st.subheader(meta1_t)
            sql = """select * from information_schema.tables t where t.table_schema ='datagen' order by table_name;"""
            df =csvpg.execute_select_query(sql)
            pg_table_grid = create_new_grid(enablePivot=True)
            pg_table_grid.display_grid( df)
        def meta2():
            st.subheader(meta2_t)
            sql = """select * from information_schema.columns where table_schema ='datagen' order by table_name;"""
            df = csvpg.execute_select_query(sql)
            pg_table_grid = create_new_grid(enablePivot=False)
            pg_table_grid.display_grid( df)        
        def meta3():
            st.subheader(meta3_t)
            unique = []
            nonunique = []
                
            sql = """SELECT table_name
                    FROM information_schema.columns c 
                    WHERE c.column_name = 'cfilingid'
                    AND c.table_schema = 'datagen';"""
            
            def create_table_sql(table_name):
                table_sql = f"""SELECT COUNT(*)
                                FROM (
                                    SELECT t.cfilingid
                                    FROM datagen.{table_name} t
                                    GROUP BY t.cfilingid
                                    HAVING COUNT(*) > 1
                                ) AS subquery;"""
                return table_sql
            df = csvpg.execute_select_query(sql)
            if 'unique' not in st.session_state:
                for table_name in df['table_name']:
                    table_sql = create_table_sql(table_name)
                    df = csvpg.execute_select_query(table_sql)
                    for i in df['count']:
                        if i > 0:
                            nonunique.append(table_name)
                        else:
                            unique.append(table_name)
                st.session_state['unique'] = unique
                st.session_state['nonunique'] = nonunique
            uni, nonuni = st.columns([1,1])
            uni.subheader("Unique", divider=True)
            uni.write(st.session_state['unique'])
            nonuni.subheader("Non-Unique", divider=True)
        def meta5():
            st.subheader(meta5_t)
            if st.button("Recompute Keys"):
                table_keys = {}
                    
                sql = """SELECT table_name
                        FROM information_schema.tables c 
                        WHERE c.table_schema = 'datagen';"""
                df = csvpg.execute_select_query(sql)
                
                for table in df['table_name']:
                    table_keys[table]={}
                    table_keys[table]['unique'] = []
                    table_keys[table]['nonunique'] = []
                
                sql = """SELECT table_name, column_name
                        FROM information_schema.columns c 
                        WHERE c.table_schema = 'datagen'
                        and (c.column_name like '%id%'
                        or c.column_name like '%crd%' or
                        c.column_name like  '%cik%' );"""
                
                df = csvpg.execute_select_query(sql)
                count = 0
                for table in table_keys.keys():
                    df_row_count = csvpg.execute_select_query(f"""SELECT COUNT(*) FROM datagen.{table};""")
                    row_count = int(df_row_count[f'count'][0])
                    table_keys[table]['row_count'] = row_count
                
                for index, row in df.iterrows():
                    table = row['table_name']
                    column = row['column_name']
                    count +=1
                    print (f"Field #{count} of {len(df.index)}: {table}")
                    if not 'id' in column.lower() and not 'cik' in column.lower():
                        continue
                    sql  = f"""SELECT DISTINCT c.{column} FROM datagen.{table} c"""
                    df1 = csvpg.execute_select_query(sql)
                    if len(df1.index)==table_keys[table]['row_count']:
                        table_keys[table]['unique'].append(f"{column} {len(df1.index)}")
                    else:
                        table_keys[table]['nonunique'].append(f"{column} {len(df1.index)}")
                st.session_state['tablekeys'] = table_keys
                st.write(table_keys)
        
        column_name_dict = {

            #c Firm
            "c1A": "Legal Name",
            "cBusiness Name": "Business Name",
            "cPrimary Business": "Business Description",
            "cOther Products and Services": "Other Offerings",



            #cAUM Breakdown
            "c5F1": "Manage Portfolios",
            "c5F2a": "Discretionary AUM",
            "c5F2b": "Non-Discretionary AUM",
            "c5F2c": "Total AUM",
            "c5F3": "Foreign Part of AUM",

            #c Filing Contacts
            "cSignatory": "Exec1 Name - CCO",
            "cTitle": "Exec1 Title",
            "cReg Contact-Name": "Exec2 Name",
            "cReg Contact-Title": "Exec2 Title",
            "cReg Contact-Phone": "Exec2 Phone",
            "cReg Contact-Email": "Exec2 Email",
            "c1J2-Name": "CCO Name",
            "c1J-Email": "CCO Email",

            #c Main Office Location
            "c1F1-Street 1": "Address 1",
            "c1F1-Street 2": "Address 2",
            "c1F1-City": "City",
            "c1F1-State": "State",
            "c1F1-Country": "Country",
            "c1F1-Postal": "Postal Code",

                #c Client Segmentation
            "c5C1": "AdviceOnly Clients",
            "c5C2": "Foreign Client Percentage",
            "c5D1a": "NonHNW Clients",
            "c5D1b": "HNW Clients",
            "c5D1c": "Bank Clients",
            "c5D1d": "Invest. Co. Clients",
            "c5D1e": "Bus Dev Co",
            "c5D1f": "Pooled Vehicles",
            "c5D1g": "Pension Sponsor Clients",
            "c5D1h": "Charity Clients",
            "c5D1i": "Gov Clients",
            "c5D1j": "Other Inv. Advisor Clients",
            "c5D1k": "Insurance Co. Clients",
            "c5D1l": "Sovereign Wealth Clients",
            "c5D1m": "Corporate Clients",
            "c5D1n": "Other Clients",
            "c5D1n Other": "Other Description",
            "c5D2a": "Under 5 Non-HNW Clients",
            "c5D2b": "Under 5 HNW Clients",
            "c5D2c": "Under 5 Bank Clients",
            "c5D2g": "Under 5 Pension Sponsor Clients",
            "c5D2h": "Under 5 Charity Clients",
            "c5D2i": "Under 5 Gov. Clients",
            "c5D2j": "Under 5 Other Inv. Advisor Clients",
            "c5D2k": "Under 5 Insurance Co. Clients",
            "c5D2l": "Under 5 Sovereign Wealth Clients",
            "c5D2m": "Under 5 Corporate Clients",
            "c5D2n": "Under 5 Other Clients",
            "c5D3a": "Non-HNW AUM",
            "c5D3b": "HNW AUM",
            "c5D3c": "Bank AUM",
            "c5D3d": "Invest. Co. AUM",
            "c5D3e": "Bus. Dev. Co. AUM",
            "c5D3f": "Pooled Vehicle AUM",
            "c5D3g": "Pension Sponsor AUM",
            "c5D3h": "Charity AUM",
            "c5D3i": "Gov. AUM",
            "c5D3j": "Other Inv. Advisor AUM",
            "c5D3k": "Insurance Co. AUM",
            "c5D3l": "Sovereign Wealth AUM",
            "c5D3m": "Corporate AUM",
            "c5D3n": "Other AUM",
            "c5F1": "Manage Portfolios",
            "c5F2a": "Discretionary AUM",
            "c5F2b": "Non-Discretionary AUM",
            "c5F2c": "Total AUM",

            #c Firm Size
            "c5A": "Total Employees",
            "c5B1": "Advisory Employees",
            "c5B2": "Registerd Reps",
            "c5B3": "Registered Advisors",
            "c5B4": "Affiliated Advisors",
            "c5B5": "Insurance Advisors",
            "c5B6": "3rdParty Solicitors",
            "c1O": "Greater than 1B Ent. Val.",
            "c1M": "Intl Registered",
            "c1L": "Maintain Book of Record",
            "c1N": "Public Reporting Company",
            "c1F1-Private": "Is a Residential Address",

            #c Firm Structure
            "c6A1": "Broker Dealer",
            "c6A2": "Registered BD Rep",
            "c6A5": "Real Estate Brokerage",
            "c6A6": "Insurance Brokerage",
            "c6A7": "Bank",
            "c6A8": "Trust Company",
            "c6A9": "Municipal Advisor",
            "c9A1a": "Custody Client Cash",
            "c9A1b": "Custody Client Securities",
            "c9A2a": "Custody AUC",
            "c9A2b": "Custody Accounts",
            "c12A": "Greater than 5m AUM",
            "c12B1": "Ownership of Advisory Firm",
            "c12C1": "Control of Indiv. Advisor",
            "c12C1": "Share Oversigh Co.",
            "c12C2": "Share Oversight Person",
            "c2A1": "Large Advisory Firm",
            "c2A2": "Mid Advisory Firm",
            "c2A4": "US Based",
            "c2A5": "Subadvisor",
            "c2A6": "Advisor of BDC",
            "c2A7": "Pension Consultant",
            "c2A8": "Related Advisor",
            "c2A9": "Expect Reg. Elig.",
            "c2A10": "Multi-Staet Advisor",
            "c2A11": "Internet Advisor",
            "c2A13": "Uneligible for Reg.",

            #c Accounts
            "c5F2d": "Discretionary Accts",
            "c5F2e": "Non-Discretionary Accts",
            "c5F2f": "Total Accts",

            #c Revenue
            "c5E1": "Comp-AUM Fee",
            "c5E2": "Comp-Hourly Fee",
            "c5E3": "Comp-Subscription",
            "c5E4": "Comp-Fixed Fee",
            "c5E5": "Comp-Commission",
            "c5E6": "Comp-Performance Fee",
            "c5E7": "Other Fee",
            "c5E7-Other": "Other Fee Description",

            #c Services Offered
            "c5G1": "Financial Planning",
            "c5G2": "Portfolio Management for Indiv.",
            "c5G3": "Portfolio Management for Invest. Co.",
            "c5G4": "Portfolio Management for Pooled Vehic.",
            "c5G5": "Portfolio Management for Businesses",
            "c5G6": "Penson Consulting",
            "c5G7": "Adviser Selection",
            "c5G8": "Media Publication",
            "c5G9": "Ratings and Pricing",
            "c5G10": "Market Timing",
            "c5G11": "Education",
            "c5G12": "Other",
            "c5G12-Other": "Other Activity",
            "c5H": "Fin Plan Clients",
            "c5H-Other": "Fin Plan Clients Large",
            "c5I1": "Use SMA Program",
            "c5I2a": "SMA Program Sponsor AUM",
            "c5I2b": "SMA Product Mgt AUM",
            "c5I2c": "Sponsor to Other Manager",
            "c5J1": "Product Advice Limited",

            #c Identifiers
            "c1P": "Legal Entity Id",
            "cCIK Number": "CIK", 
            "cFilingID" :"Filing Id", 
            "cReferenceID": "Reference ID",
            }

        
        def firmList():
            if st.button("Show me the $$$"):
                csvpg = CSVToPostgres()
                # iascheduled7a2024010120240331
                df_merged = csvpg.execute_select_query("""SELECT * from datagen.iaadvbasea2024010120240331""")
                # # df_0 = csvpg.execute_select_query("""SELECT * from datagen.iaadvbasea2024010120240331""")
                # # df_merged = pd.merge(df_0, df_base, on='cfilingid', how='left')
                
                # # Get all dem data frames
                # df1 = csvpg.execute_select_query("""SELECT i.cfilingid, i.cfulllegalname || '; ' || i.ctitleorstatus as pers FROM datagen.iascheduleab2024010120240331 i WHERE i.cdefei = 'I';""")
                # df1 = df1.groupby('cfilingid')['pers'].agg(', '.join).reset_index()
                # df_merged = pd.merge(df_base, df1, on='cfilingid', how='left')
          
  
                
                # return
                # df2 = csvpg.execute_select_query("""SELECT * from datagen.iascheduled1i2024010120240331""")
                # df3 = csvpg.execute_select_query("""SELECT * from datagen.iascheduled7b1a28websites2024010120240331""")
                
                # #df1
                # df_merged = pd.merge(df_base, df_0, on='cfilingid', how='left')
                
                
                
                
                
                # df_merged = pd.merge(df_merged, df2, on='cfilingid', how='left')
                # df_merged = pd.merge(df_merged, df3, on='cfilingid', how='left')

                
                
                
                
                r_dict = {}
                for k in column_name_dict.keys():
                    r_dict[k.lower()]=column_name_dict[k]

                df_merged.drop_duplicates()
                df_merged = df_merged.rename(columns=r_dict)
                df_merged.to_csv('merged.csv', index=False)
                
                pg_table_grid = create_new_grid(enablePivot=False)
                pg_table_grid.display_grid(df_merged)
                print('done')

        nav_dict= {
            "Awesome US Target Lists": [
            st.Page(page=firmList, title="Why did you click here?", url_path='home'),    
            st.Page(page=firmList, title="US List", url_path='for_noelle_and_sarah_and_uhhhh_maybe_barb'),    
            ],
            "Filings": [],
            "Metadata": [
            st.Page(page=meta1, title=meta1_t),
            st.Page(page=meta2, title=meta2_t),
            st.Page(page=meta3, title=meta3_t),
            st.Page(page=meta5, title=meta5_t),
            ]
            }
        
        
        
        def define_function_from_string(table_name='', title=''):
            func_code = (
                f"def func{table_name}():\n"
                f"    csvpg = CSVToPostgres(schema='datagen', likely_key_names=['cfilingid', 'creferenceid', 'ccik'], table_prefix='', column_prefix='c',)\n"
                f"    pg_table_grid = create_new_grid(enablePivot=False)\n"
                f"    st.subheader(f'Table / Filing: {title}')\n"
                f"    st.divider()\n"
                f"    if '{table_name}' in st.session_state:\n"
                f"        df = st.session_state['{table_name}']\n"
                f"        pg_table_grid.display_grid(df)\n"
                f"    elif st.button('Show me the data: {title}'):\n"
                f"        sql = f\"Select * from datagen.{table_name}\"\n"
                f"        st.write(sql)\n"
                f"        df = csvpg.execute_select_query(sql)\n"
                f"        pg_table_grid.display_grid(df)\n"
                f"        st.session_state['{table_name}'] = df\n"
                f"\n"
                f"nav_dict['Filings'].append(st.Page(page=func{table_name}, title='{title}', url_path='{table_name}'))\n"
            )
            
            
            # Explicitly pass nav_dict as part of the local context
            local_context = {'nav_dict': nav_dict, 'csvpg':csvpg}
            exec(func_code, globals(), local_context)
        
        for key in table_name_dict.keys():
            title_str=table_name_dict.get(key, key)
            define_function_from_string(key, title=title_str)
            
        pg = st.navigation(nav_dict)
           
        pg.run()
        
    
    main()
    st.stop()
    
    
    

    
    
    
    