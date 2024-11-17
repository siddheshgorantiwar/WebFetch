# CSV Data Extraction Workflow

This project is a **Streamlit-based application** that allows users to extract and update information in a CSV file using **prompt-driven web-based data retrieval**. It leverages APIs and tools like LangChain, Tavily, and Google Sheets for seamless and intelligent data processing.

## Project Summary

The application enables users to:
- Upload a CSV file or load data directly from **Google Sheets**.
- Use custom prompts to retrieve relevant web-based information via the **Tavily API**.
- Update the Google Sheet with the newly extracted data.
- Download the updated data in both **CSV** and **Google Sheet** formats.
- Perform operations like cleaning, merging, and converting DataFrames.

## Features

### Web Search Integration
- **Tavily API**: Retrieves real-time web-based information by querying various web tools.
- **DuckDuckGo Search Tool**: Acts as a backup tool if the Tavily API fails to fetch results.
  
### Google Sheets Integration
- **Load Google Sheets**: Directly load data from Google Sheets using a URL input.
- **Update Google Sheets**: After processing the data, users can update their Google Sheets with the newly fetched data.

### File Management
- **CSV Upload**: Users can upload a CSV file directly into the application.
- **Downloadable Outputs**: After processing, users can download the updated data in both **CSV** and **Google Sheets** formats.
- **Data Merging**: Merges the original DataFrame with the newly fetched data, while removing any duplicates and maintaining original data integrity.

### Custom Data Extraction
- **Dynamic Prompts**: The application allows users to input custom search queries to retrieve specific information related to a product or topic.
- **Structured Data Output**: Extracted information is formatted into structured data, such as markdown tables or cleaned dictionaries, ready for use in the DataFrame.

### Session Management
- **Column Selection**: Users can select which column in the CSV file to process using a drop-down menu.
- **User Query Input**: Allows users to input specific search queries that will be processed across multiple columns in the dataset.

### Data Cleaning and Processing
- **Data Transformation**: The tool cleans and formats raw web data into a usable structure, removing unnecessary details and creating a clean table.
- **Markdown to DataFrame Conversion**: Converts markdown tables generated from responses into DataFrames for further processing.

### Progress and Status Updates
- **Progress Bars**: A visual progress bar shows the status of data extraction across multiple columns and queries.
- **Error Handling**: Handles errors gracefully, providing feedback to the user if something goes wrong during data loading or processing.

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/siddheshgorantiwar/WebFetch
   cd WebFetch
2. pip install -r requirements.txt
3. Create a .env File and Add the Following Credentials:
   TAVILY_API_KEY=<Your_Tavily_API_Key>
   GOOGLE_CREDENTIALS_JSON=<Path_to_Google_Service_Account_JSON_File>
4. run the application: streamlit run app_final.py
