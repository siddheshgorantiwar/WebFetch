import streamlit as st
import pandas as pd
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent,initialize_agent, Tool
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type, List
from langchain_core.prompts import PromptTemplate
from groq import Groq
from langchain.output_parsers import PandasDataFrameOutputParser
from streamlit_gsheets import GSheetsConnection
from google.oauth2.service_account import Credentials
import gspread
import ast

from helper_functions.sheet_functions import update_google_sheet,load_google_sheet
from helper_functions.df_operations import load_excel_file, clean,to_md,markdown_to_dataframe,merge_df,convert_df,parse_query


load_dotenv()
conn = st.connection("gsheets", type=GSheetsConnection)


##### DEFINING TOOLS #####

class TavilySearchInput(BaseModel):
    query: str = Field(description="should be a search query")

class TavilySearchTool(BaseTool):
    name: str = "tavily_search"
    description: str = '''Primary web search tool to get details '''

    args_schema: Type[BaseModel] = TavilySearchInput

    def _run(self, query: str) -> str:
        from tavily import TavilyClient
        api_key = os.getenv("TAVILY_API_KEY")
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query,max_results=3)
        combined_content = "\n".join(result['content'] for result in response['results'] if result['content'])
        return f"Search results for: {query}\n\n\n{combined_content}\n"
    
class DuckDuckGoSearchInput(BaseModel):
    query: str = Field(description="should be a search query")

class DuckDuckGoSearchTool(BaseTool):
    name: str = "duckduckgo_search"
    description: str = '''backup web search tool to get details if tavily doesn't work'''
    args_schema: Type[BaseModel] = DuckDuckGoSearchInput

    def _run(self, query: str) -> str:
        from langchain_community.tools import DuckDuckGoSearchRun
        search = DuckDuckGoSearchRun()  # Adjust max_results as needed
        results=search.invoke(query)
        return f"search results are {results}"




##### Mainframe code ######
def run_main(df):
    global google_sheet_used
    st.text("CSV data loaded successfully!")
    st.dataframe(df)
    
    # Initialize session state only once
    if 'selected_column' not in st.session_state:
        st.session_state.selected_column = df.columns[0]  # Default to first column
    st.write("Current selected column:", st.session_state.selected_column)
    # Create selectbox with session state
    column = st.selectbox("Column", df.columns, index=df.columns.get_loc(st.session_state.selected_column))
    
    # Update session state with selected column
    st.session_state.selected_column = column

    columns = df[column].to_list()

    user_query = st.text_input("Enter the search term")
    data = ""
    if st.button("Search"):
        if user_query:
            with st.spinner('Searching...'):
                tools = [TavilySearchTool(), DuckDuckGoSearchTool()]
                llm = ChatGroq(model="llama3-groq-70b-8192-tool-use-preview", temperature=0.4)
                prompt = hub.pull("hwchase17/openai-tools-agent")
                agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
                agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
                  
                response_dict = {}
                query_list=parse_query(user_query)
                st.write(f"list of queries :{query_list}")
                total_iterations = len(columns) * len(query_list)
                progress_bar = st.progress(0)
                for i,value in enumerate(columns):
                    for j,query_element in enumerate(query_list):
                        response = agent_executor.invoke({"input":
                                                    f"""
                                                        Use your tools to answer the following query: \n
                                                            {query_element}\n for \n {value}\n\n
                                                        {query_element}: 20 to 50  words response to {value} in form of
                                                        key value pair, where key is query element and value is corresponding 
                                                        info extracted from tool.                                                
                                                        example: contact email for adobe: xyz@adobe.in\n
                                                        if no relevant results are found using one tool, 
                                                        use another tool. If still no results are 
                                                        found return "no results found".  
                                                        """ 
                                                         }) 
                        data += response["output"] + "\n"
                        total_iterations = len(columns) * len(query_list)  # Total number of iterations
                        current_iteration = i * len(query_list) + j + 1     # Current iteration count
                        progress_percentage = current_iteration / total_iterations  # Normalize to [0, 1]
                        progress_bar.progress(progress_percentage)          
                print(data)
                st.write(f"Data extraction complete!")
            
            with st.spinner("converting to csv"):

                response_content = to_md(data, str(query_list),column)

                df_result = markdown_to_dataframe(response_content)
                st.dataframe(df_result)
                df_result_csv=convert_df(df_result)

                df_merged_md=merge_df(df,df_result)
                df_merged_pd=markdown_to_dataframe(df_merged_md)
                st.dataframe(df_merged_pd)
                df_merged_csv=convert_df(df_merged_pd)
                
                st.download_button(
                    label="Download only results file as CSV",
                    data=df_result_csv,
                    file_name='Results_changes.csv',
                    mime='text/csv'
                )
                st.download_button(
                    label="Download updated file as CSV",
                    data=df_merged_csv,
                    file_name='Results_new.csv',
                    mime='text/csv'
                )

                if google_sheet_used:
                    st.button("Click to update the google sheet",on_click=update_google_sheet(sheet_url, df_merged_pd))

                


st.title("Web Search for CSV Data!")

option = st.selectbox("Choose an option:", ["Paste Google Sheet Link", "Upload Excel File"])
google_sheet_used=False
if option=="Upload Excel File":
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    if uploaded_file is not None:
        try:
            
            df = pd.read_csv(uploaded_file)
            run_main(df)
        except Exception as e:
            st.error(f"Error loading CSV file: {e}")  

if option == "Paste Google Sheet Link":
    google_sheet_used=True
    google_sheet_url = st.secrets["connections"].get("google_sheet_url", None)
    sheet_url = st.text_input("Enter your Google Sheet URL:", value=google_sheet_url)
    if st.button("Load Data"):
        if sheet_url:
            try:
                st.session_state.df = load_google_sheet(sheet_url)
                st.session_state.df_loaded = True
                st.write("Data loaded successfully!")
            except Exception as e:
                st.error(f"Error loading data from Google Sheet: {e}")
                st.session_state.df_loaded = False
        else:
            st.warning("Please enter a valid Google Sheet URL.")
    
    # Check if data is loaded and pass it to `run_main`
    if st.session_state.get("df_loaded", False):
        run_main(st.session_state.df)

       



