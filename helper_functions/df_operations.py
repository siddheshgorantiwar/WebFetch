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
import re
import json
from io import StringIO
from streamlit_gsheets import GSheetsConnection
from google.oauth2.service_account import Credentials
import gspread
import ast


llm_client = Groq()



def load_excel_file(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df

def clean(data,user_query):
    user_prompt = f'''
                Given the text below, your task is to extract and format {user_query}s into a structured dictionary format. 
                Specifically, parse the text to create a dictionary , where each entry consists of a 
                entity name as the key and the {user_query}.Do it for all entities in the text.\n\n\n
                {data}
            '''
                    
    chat_completion = llm_client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ],
    model="llama3-8b-8192",
    temperature=1, 
    max_tokens=1024  
    )

    chat_completion=llm_client.chat.completions.create(
        messages=[
            {"role": "user", 
             
            "content": user_prompt
            }

            ], 
            
            model="llama3-8b-8192", 
            temperature=1, 
            max_tokens=1024)
    
    response_content = chat_completion.choices[0].message.content
    pattern = r'```(.*?)```'
    matches = re.findall(pattern, response_content, re.DOTALL)

    return matches


def to_md(data, user_query,selected_column):
    # Update the user prompt to request a Markdown table
    user_prompt = f'''
               Your task is to extract and format **all instances** of `{user_query}` from the provided text into a **Markdown table**. The goal is to accurately parse the text and create a Markdown table where:

1. **Column Details**:
   - each column should be named based on elements in **"{user_query}"**.
   - you need to extract data for {user_query} based on the following data chunk: {data}

2. **Output Requirements**:
   - The output must be in **Markdown table format** that is **ready for direct rendering** (e.g., within a Markdown viewer or editor).
   - **Do not include any additional text, commentary, or explanation**—only the Markdown table.

3. **Data Handling**:
   - Extract **all relevant information** from the provided text and ensure no significant data is missed.
   - If no data is found for certain entities or rows, leave the corresponding cell blank.

4. **Input Data**:
   - You will be given a block of text (`{data}`) that contains unstructured information about various entities.

5. **Output Example**:
   If `{user_query}` is ["Price Details","processor info" and `{selected_column}` is "Product Name", and the data contains this information:
   ```plaintext
   Product A has a price of $100. Product B is $150. Product C does not have a listed price.

output should look like this:\n
   | Product Name | Price Details   | processor info |
|--------------|-----------------|----------------
| Product A    | $100            |snapdragon 845
| Product B    | $150            |mediatech
| Product C    |                 |A12 bionic


            '''
                    
    # Create chat completion request
    chat_completion = llm_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
        model="mixtral-8x7b-32768",
        temperature=1, 
        max_tokens=2000  
    )

    # Get the response content
    response_content = chat_completion.choices[0].message.content.strip()
    start_index = response_content.find('|')
    end_index = response_content.rfind('|')
    if start_index != -1 and end_index != -1:
        markdown_table = response_content[start_index:end_index + 1]
    else:
        markdown_table = ""  # Handle case where no table is found

    return markdown_table

def markdown_to_dataframe(markdown_table):
    
    table_io = StringIO(markdown_table)

    df = pd.read_csv(table_io, sep='|', skipinitialspace=True)

    df.columns = df.columns.str.strip()  # Remove leading/trailing whitespace from column names
    df = df.dropna(axis=1, how='all')     # Drop empty columns
    df = df.iloc[1:]                      # Drop the header row (Markdown header)

    return df

@st.cache_data
def convert_df(df):
    # Convert DataFrame to CSV and encode it
    return df.to_csv(index=False).encode('utf-8')

def merge_df(df_original,df_changed):
    user_prompt = f'''
                original df : \n {df_original} \n
                changed df : \n {df_changed} \n
                your task is to combine the contents of  the two dataframes into one.
                add all the extra things of changed df into original df by preserving the contents of
                original dataframe.\n
                *Remove any duplicate rows or columns.*\n

                return ONLY a markedown table containing only table data and NO additional text.
            '''
                    
    # Create chat completion request
    chat_completion = llm_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
        model="mixtral-8x7b-32768",
        temperature=0, 
        max_tokens=2000  
    )

    # Get the response content
    response_content = chat_completion.choices[0].message.content.strip()
    start_index = response_content.find('|')
    end_index = response_content.rfind('|')
    if start_index != -1 and end_index != -1:
        markdown_table = response_content[start_index:end_index + 1]
    else:
        markdown_table = ""  # Handle case where no table is found

    return markdown_table


def parse_query(user_query):
    # Construct the user prompt
    user_prompt = f'''
        User query: {user_query} 
        
        Your task is to intelligently split the user query into meaningful terms based on context and semantics.
        Each term should represent a specific aspect of the query.

        Example:
        User query: "processor info and price in India"
        Output: ['processor info', 'price in India']

        Note:
        - The terms should be meaningful, and phrases like "and" or "or" should not appear as standalone terms.
        - Preserve context for multi-word terms such as "price in India" or "processor info".
        - Return the result as a Python list of strings in the format: ['term1', 'term2', ...]
        to know the exact term to put, check if adding a name after it makes sense.
        example: ['price', 'in India'], iphone price makes sense but in India price doesn't make sense
        example query : Price in India
        correct: ['price in India'] 
        Incorrect: ['price', 'in', 'India'] or ['price','in India'].
    '''

    # Create chat completion request
    chat_completion = llm_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant who understands context and semantics."
            },
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
        model="llama3-8b-8192",
        temperature=0, 
        max_tokens=1024  
    )

    # Get the response content
    response_content = chat_completion.choices[0].message.content.strip()


    # Extract the list from the response content
    start_index = response_content.find('[')
    end_index = response_content.rfind(']')
    if start_index != -1 and end_index != -1:
        response_list = response_content[start_index:end_index + 1]
        # Convert the extracted string to a Python list
        parsed_list = ast.literal_eval(response_list)
        return parsed_list

    else:
        return [user_query]

