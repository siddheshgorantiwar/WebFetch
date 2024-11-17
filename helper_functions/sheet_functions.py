from streamlit_gsheets import GSheetsConnection
import streamlit as st
import pandas as pd

@st.cache_data
def load_google_sheet(sheet_url):
    global conn
    data = conn.read(spreadsheet=sheet_url)  # Assuming this returns a dictionary or list of lists
    df = pd.DataFrame(data)
    df = df.convert_dtypes()
    return df


def update_google_sheet(sheet_url, df):
    global conn
    conn=st.connection("gsheets", type=GSheetsConnection)

    # Convert DataFrame to a list of lists for updating
    values = df.values.tolist()
    
    # Define the range where you want to update the data (e.g., starting from A1)
    range_name = 'Sheet1!A1'  # Adjust as necessary
    
    # Update Google Sheets using the correct method
    conn.update(worksheet="Sheet1", data=values) 