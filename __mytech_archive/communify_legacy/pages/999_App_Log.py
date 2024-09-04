import sys
from pathlib import Path

# Add the parent directory to sys.path
# parent_dir = str(Path(__file__).resolve().parent.parent)
# sys.path.append(parent_dir)

from flask import g
from numpy import disp
import shared.functions_constants as con
import streamlit as st
import pandas as pd
import shared.functions_db_postgres as db
import sqlite3
from st_aggrid import AgGrid as ag, GridOptionsBuilder
st.set_page_config(layout="wide")





conn = sqlite3.connect(db.DB_FILE_PATH)

sql = db.sql_recent_sql_recent_llm_interactions()
sql2= db.sql_recent_log_entries()
df = pd.read_sql_query(sql, conn)
#ag(df)
#editable=True




filter_panel = {
        "id": "filters",
        "labelDefault": "Filters",
        "labelKey": "filters",
        "iconKey": "filter",
        "toolPanel": "agFiltersToolPanel",
    }

columns_panel = {
    "id": "columns",
    "labelDefault": "Columns",
    "labelKey": "columns",
    "iconKey": "columns",
    "toolPanel": "agColumnsToolPanel",

}
defaultToolPanel: str = "",        
st.sideBar = {"toolPanels": [], "defaultToolPanel": defaultToolPanel}
st.sideBar["toolPanels"].append(filter_panel)
st.sideBar["toolPanels"].append(columns_panel)

        #self.__grid_options["sideBar"] = sideBar
# GridOptionsBuilder allows you to build the grid options
# https://streamlit-aggrid.readthedocs.io/en/docs/GridOptionsBuilder.html
options_builder = GridOptionsBuilder.from_dataframe(df) #Create instance of options builder
options_builder.configure_column('id', editable=True)  #make specific column editable
options_builder.configure_selection('single') #allow only single row 
grid_options = options_builder.build() #return the grid options (json)
grid_return = ag(df, grid_options) #(you ag to create the grid)
selected_rows = grid_return['selected_rows']
st.write(selected_rows)




conn.close()

# https://medium.com/@nikolayryabykh/enhancing-your-streamlit-tables-with-aggrid-advanced-tips-and-tricks-250d4b57903
# import streamlit as st

# from src.agstyler import PINLEFT, PRECISION_TWO, draw_grid

# formatter = {
#     'player_name': ('Player', PINLEFT),
#     'team': ('Team', {'width': 80}),
#     'poss': ('Posessions', {'width': 110}),
#     'mp': ('mp', {'width': 80}),
#     'raptor_total': ('RAPTOR', {**PRECISION_TWO, 'width': 100}),
#     'war_total': ('WAR', {**PRECISION_TWO, 'width': 80}),
#     'pace_impact': ('Pace Impact', {**PRECISION_TWO, 'width': 120})
# }

# row_number = st.number_input('Number of rows', min_value=0, value=20)
# data = draw_grid(
#     df.head(row_number),
#     formatter=formatter,
#     fit_columns=True,
#     selection='multiple',  # or 'single', or None
#     use_checkbox='True',  # or False by default
#     max_height=300
# )