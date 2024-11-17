# CSV Data Extraction Workflow

This project is a **Streamlit-based application** that allows users to extract and update information in a CSV file using **prompt-driven web-based data retrieval**. It leverages APIs and tools like LangChain, Tavily, and Google Sheets for seamless and intelligent data processing.

## Project Summary

The application enables users to:
- Upload a CSV file from local or load data directly from **Google Sheets**.
- Use custom prompts to retrieve relevant web-based information via the **Tavily API**.
- get back updated CSV/google sheets link.

  
## Features

### Web Search Integration
- **Tavily API**: Retrieves real-time web-based information by querying various web tools.
- **DuckDuckGo Search Tool**: Acts as a backup tool if the Tavily API fails to fetch results.
  
### Google Sheets Integration
- **Load Google Sheets**: Directly load data from Google Sheets using a URL input.
- **Update Google Sheets**: After processing the data, users can update their Google Sheets with the newly fetched data.

### Multiple Fields in a single prompt
- Users can request for multiple details in a single prompt.
  eg: customer care email-id and contact phone number for {company}
  
### File Management
- **CSV Upload**: Users can upload a CSV file directly into the application.
- **Downloadable Outputs**: After processing, users can download the updated data in **CSV** OR update the original google sheet.

### Custom Data Extraction
- **Dynamic Prompts**: The application allows users to input custom search queries to retrieve specific information related to a product or topic.
- **Structured Data Output**: Extracted information is formatted into markdown tables ready for use in the DataFrame.

### Session Management
- **Column Selection**: Users can select which column in the CSV file to process using a drop-down menu.
- **User Query Input**: Allows users to input specific search queries that will be processed across multiple columns in the dataset.

### Data Cleaning and Processing
- **Data Transformation**: The tool cleans and formats raw web data into a usable structure, removing unnecessary details and creating a clean table.
- **Markdown to DataFrame Conversion**: Converts markdown tables generated from responses into DataFrames for further processing.

### Progress and Status Updates
- **Progress Bars**: A visual progress bar shows the status of data extraction across multiple columns and queries.

### Error Handling

1. **File Upload & Google Sheets Errors**: Invalid file types or empty files trigger prompts to upload valid CSVs. Incorrect Google Sheets URLs or authentication failures notify users to verify details.
2. **Web Data Retrieval & Processing Errors**: If Tavily API fails, the DuckDuckGo fallback is triggered. No results or parsing issues prompt user notifications, with automatic duplicate handling.
3. **CSV/Sheet Update & Session Errors**: Failed updates due to permissions or network issues halt operations. Session timeouts and interruptions notify users to restart or save progress periodically.
4. **General Notifications & Alerts**: Catch-all exceptions log errors and display user-friendly messages, with progress updates keeping users informed during delays.


## Project Demo
  **Loom video link ** : https://www.loom.com/share/abb6883c6871479282fc96a569c77979?sid=ce5cb83c-e754-4bd1-ad45-5dd58a2d61e9

  
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
