import streamlit as st
import shared.functions_common as oc2c
import os
import json
import pandas as pd
import shared.functions_sql as psql
import shared.functions_model_generation as model_gen
oc2c.configure_streamlit_page("Meeting Notes")

PE_IO_DIRECTORY = os.environ.get('PERSONAL_EXPENSES_IO_FOLDER_PATH')
models_path = os.path.join(PE_IO_DIRECTORY, "models.json")


if __name__ == "__main__":

    @st.cache_data
    def get_transactions_data_as_df():
        df = psql.execute_sql("SELECT * FROM transaction")
        return df

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        st.header("Personal Expenses")
        st.subheader("Transaction Data")

        db_conn = psql.get_connection_to_db()

        def read_data_from_db(db_conn, table_name):
            """Reads data from a PostgreSQL table and returns a pandas DataFrame"""
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql(query, db_conn)
            return df

    st.cache = True

    def display_data_editor(df):
        """Displays the data in a Streamlit data editor and returns the modified DataFrame"""

        with open(models_path, "r") as f:
            models_text = f.read()
            models_dict = json.load(models_text)
            auto_col_config = {}
            for column in df.columns:
                if column.lower() in models_dict['models']['entities']['transaction']['attributes']:
                    col_props = models_dict['models']['entities']['transaction']['attributes'][column.lower(
                    )]
                    # # get the first 3 letters of the column name
                    # field_type = column[:3]
                    # col_type_props = models_dict[
                    #     'databasedefinitions']['postgresql']['AttributeDefaultProperties']

        return st.data_editor(df, height=700, use_container_width=True, hide_index=True, num_rows="dynamic", key="data_editor", column_config={})

    table_name = "transaction"

    # Fetch initial data
    original_data = read_data_from_db(db_conn, table_name)

    # Display in data editor
    modified_data = display_data_editor(original_data.copy())  # Work on a copy

    # Handle changes if the data editor returns a modified DataFrame
    if modified_data is not None:
        psql.handle_edits(original_data, modified_data, db_conn, table_name)

    with col4:
        if st.button("Reaload Standardized Data"):
            # Load all the standardized transactions
            psql.DELETE_ALL_TABLES()
            print("Deleted all tables")
            print(models_path)
            create_table_statements = model_gen.generate_model_for_database(
                models_path, 'outercircles', 'postgresql')
            for statement in create_table_statements:
                psql.execute_sql(statement)
            # << This is the output file that will be created. All of the transactions will be in MY standard model format
            transactionFilePath = os.path.join(
                PE_IO_DIRECTORY, "Output", 'standardized.csv')
            print(transactionFilePath)
            psql.loadTableDataFromCSV('transaction', transactionFilePath)

if __name__ == "__main__":
    print("This is the main function")

    # column_config={

    #         #Defult
    #         label="Streamlit Widgets", #The label shown at the top of the column. If None (default), the column name is used.
    #         help="Streamlit **widget** commands", #An optional tooltip that gets displayed when hovering over the column label.
    #         width="medium", # "small", "medium", "large", or "None" (which is to set it do data width)
    #         required=True, # An optional tooltip that gets displayed when hovering over the column label.
    #         disabled=False, #Whether editing should be disabled for this column. Defaults to False.
    #         default="String Value", # Data that aligns with column type or None. Specifies the default value in this column when a new row is added by the user.

    #         #Text
    #         max_chars=50, #(int or None) # The maximum number of characters that can be entered. If None (default), there will be no maximum.
    #         validate=None, # (str or None) A regular expression (JS flavor, e.g. "^[a-z]+$") that edited values are validated against. If the input is invalid, it will not be submitted.

    #         #For Number Datetime, Date, and Time
    #         Format=None, # (str or None) A printf-style format string controlling how numbers are displayed. This does not impact the return value. Valid formatters: %d %e %f %g %i %u. You can also add prefixes and suffixes, e.g. "$ %.2f" to show a dollar prefix.
    #         min_value=None, # (int, float, or None) The minimum value that can be entered. If None (default), there will be no minimum.
    #         max_value=None, # (int, float, or None) The maximum value that can be entered. If None (default), there will be no maximum.
    #         step=None (int, float, or None) The stepping interval. Specifies the precision of numbers that can be entered. If None (default), uses 1 for integers and unrestricted precision for floats.

    #         # Others are: Checkbox, Selectbox, List, Link, Image, Line chart, Bar chart, Progress

    # }
