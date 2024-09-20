import os
import sys
import pandas as pd
import streamlit as st

import json
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import uuid
import re

import chardet
from decimal import Decimal
import psycopg2

from _class_streamlit import streamlit_mytech 
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