
#standard modules   
import os, sys, json, requests, re, datetime, time, random
from time import thread_time

#data processing
import pandas as pd
import numpy as np
import sqlite3
import psycopg2
import nltk
# import spacy

#Streamlit UI
import streamlit as st
from st_aggrid import AgGrid, JsCode, GridOptionsBuilder, GridUpdateMode, DataReturnMode

#charting
#import plotly.express as px

#my modules



def create_default_grid(
        dataframe = None, col_val_list = None,
        # Column Options
        minWidth=5, 
        editable=True, 
        filter=True, 
        resizable=True, 
        sortable=True, 
        enableRowGroup=True, 

        # Grid Options
        rowSelection="multiple", 
        use_checkbox=True,
        rowMultiSelectWithClick=False, 
        suppressRowDeselection=False, 
        suppressRowClickSelection=False, 
        groupSelectsChildren=True, 
        groupSelectsFiltered=True, 
        preSelectAllRows=False,

        # Sidebar Options
        sideBar=True,
        ):
    
    builder = GridOptionsBuilder.from_dataframe(dataframe)
    builder.configure_selection(selection_mode='multiple', use_checkbox=True)
    builder.configure_pagination(enabled=True)

    gridoptions = builder.build()

    new_columns = []
    for col in gridoptions['columnDefs']:
        newcol = {}
        newcol['headerName']= col['headerName']
        newcol['field'] =  col['headerName']
        newcol['minWidth'] = minWidth
        newcol['editable'] = editable
        # Check if 'type' key exists in col
        if 'type' in col:
            newcol['type'] = col['type']
        else:
            newcol['type'] = [] # 
        newcol['filter'] = filter
        newcol['resizable'] = resizable
        newcol['sortable'] = sortable
        newcol['enableRowGroup'] = enableRowGroup
        new_columns.append(newcol)
    
    grid_options =  {
        "defaultColDef": {
            "minWidth": minWidth,
            "editable": editable,
            "filter": filter,
            "resizable": resizable,
            "sortable": sortable,
            "enableRowGroup": enableRowGroup
        },
        "statusBar": 
            {
            "statusPanels": 
                    [
                        {
                        "statusPanel": 'agAggregationComponent',
                        "statusPanelParams": 
                            {
                            # possible values are: 'count', 'sum', 'min', 'max', 'avg'
                            "aggFuncs": ['min', 'max', 'avg']
                            }
                        }
                    ]
            },
                    
        "sideBar": True,
        "enableAdvancedFilter": True,
        "enableCharts": True,
        "enableRangeSelection": True,
        "columnDefs": new_columns,
        # The columnDefs section is ignored as per your request
        "rowSelection": rowSelection,
        "useCheckbox": use_checkbox,
        "pagination": True,
        "paginationAutoPageSize": True,
        "onSelectionChanged": 'on_row_selected',
        "rowMultiSelectWithClick": rowMultiSelectWithClick,
        "suppressRowDeselection": suppressRowDeselection,
        "suppressRowClickSelection": suppressRowClickSelection,
        "groupSelectsChildren": groupSelectsChildren,
        "groupSelectsFiltered": groupSelectsFiltered,
        "preSelectAllRows": False    
        
    }

    return grid_options

def get_grid(dataframe=None, grid_options=None, height=700, row_selection=True, on_row_selected=None, fit_columns_on_grid_load=True, update_mode=GridUpdateMode.SELECTION_CHANGED, data_return_mode="as_input", conversion_errors='coerce', theme='balham', custom_css=None):

    grid_options = create_default_grid(dataframe)
     
    grid_return = AgGrid(dataframe, #: pandas.core.frame.DataFrame, 
                     grid_options, #: typing.Optional[typing.Dict] = None, 
                     height=height, #: int = 7, 
                     row_selection=row_selection,
                     on_row_selected=on_row_selected,
                     #width=None, #! Deprecated
                     fit_columns_on_grid_load=fit_columns_on_grid_load, #: bool = False, 
                     update_mode=update_mode, #: st_aggrid.shared.GridUpdateMode = GridUpdateMode.None, 
                        # GridUpdateMode.NO_UPDATE
                        # GridUpdateMode.MANUAL
                        # GridUpdateMode.VALUE_CHANGED #!Editing
                        # GridUpdateMode.SELECTION_CHANGED #!Navigation
                        # GridUpdateMode.FILTERING_CHANGED
                        # GridUpdateMode.SORTING_CHANGED
                        # GridUpdateMode.MODEL_CHANGED
                        # !modes can be combined with bitwise OR operator | for instance: GridUpdateMode = VALUE_CHANGED | SELECTION_CHANGED | FILTERING_CHANGED | SORTING_CHANGED
                     data_return_mode=data_return_mode, #: st_aggrid.shared.DataReturnMode = 'as_input', 
                        # DataReturnMode.AS_INPUT -> Returns grid data as inputed. Includes cell editions
                        # DataReturnMode.FILTERED -> Returns filtered grid data, maintains input order
                        # DataReturnMode.FILTERED_AND_SORTED -> Returns grid data filtered and sorted
                        #! Defaults to DataReturnMode.AS_INPUT.
                     #allow_unsafe_jscode: bool = False, 
                     #enable_enterprise_modules: bool = False, 
                     #license_key: typing.Optional[str] = None, 
                     #try_to_convert_back_to_original_types: bool = True, 
                     conversion_errors=conversion_errors, #
                    #  Behaviour when conversion fails. One of:
                    #     ’raise’ -> invalid parsing will raise an exception.
                    #     ’coerce’ -> then invalid parsing will be set as NaT/NaN.
                    #     ’ignore’ -> invalid parsing will return the input.
                     #reload_data: bool = False, 
                     theme=theme, 
                        # 'streamlit' -> follows default streamlit colors
                        # 'alpine' -> follows default streamlit colors
                        # 'balham' -> follows default streamlit colors
                        # 'material' -> follows default streamlit colors
                     #key: typing.Optional[typing.Any] = None, 
                     custom_css=custom_css,
                     # default_column_parameters
                     )
    
    # Activate this line to see the input parameters    
    #st.write(locals())

    # st.write(locals()['height'])    
    # st.write(locals()['fit_columns_on_grid_load'])
    # st.write(locals()['update_mode'])
    # st.write(locals()['data_return_mode'])
    # # st.write(input_parameters['conversion_errors'])
    # # st.write(input_parameters['theme'])
    # # st.write(input_parameters['custom_css'])
    return grid_return






if __name__ == "__main__":
    #st.set_page_config(layout="wide")
    st.header('Executing AG_Grid Tests', divider="red")

    #! Test #1: AG Grid with default data
    st.subheader('Test #1: AG Grid with default data')
    

    # Example of Random Data in AGGrid
    dataframe = pd.DataFrame(
        np.random.randn(1000, 4),
        columns=['Column %s' % i for i in range(4)])
    grid_return = get_grid(dataframe=dataframe)
    st.write(grid_return)

    # Showing selected data
    if 'selected_rows' in grid_return and len(grid_return['selected_rows']) > 0:
        st.write(grid_return['selected_rows']) 
        


    


