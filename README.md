# CSV Data Extraction Workflow

This project is a **Streamlit-based application** that allows users to extract and update information in a CSV file using **prompt-driven web-based data retrieval**. It leverages APIs and tools like LangChain, Tavily, and Google Sheets for seamless and intelligent data processing.

## Project Summary

The application enables users to:
- Upload a CSV file or load data directly from **Google Sheets**.
- Use custom prompts to retrieve relevant web-based information via the **Tavily API**.
- Update the Google Sheet with the newly extracted data.
- Download the updated data in both **CSV** and **Google Sheet** formats.
- Perform operations like cleaning, merging, and converting DataFrames.

Key features include:
- **Web Search Integration**: Tools like Tavily are used for real-time web data retrieval.
- **Google Sheets Integration**: Load and update data directly in Google Sheets.
- **File Management**: Options to upload a CSV file, update Google Sheets, and download updated files.

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone [<repository_url>](https://github.com/siddheshgorantiwar/WebFetch)
   cd WebFetch
2. pip install -r requirements.txt
3. create a .env file and add the below credentials:
   TAVILY_API_KEY=<Your_Tavily_API_Key>
   GOOGLE_CREDENTIALS_JSON=<Path_to_Google_Service_Account_JSON_File>
4. streamlit run app_final.py
