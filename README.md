# YouTube Data Harvesting and Warehousing using SQL, MongoDB and Streamlit
![image](https://github.com/choprasv/Youtube-Data-Harvesting-and-Warehousing/blob/main/youtube.png)

# Aim of the project

 - This project aims to focus on harvesting data from YouTube channels using the YouTube API, processing the data, and warehousing it. The harvested data is initially stored in a MongoDB Atlas database as documents and is then converted into SQL records for in-depth data analysis. The project's core functionality relies on the Extract, Transform, Load (ETL) process.

     
# Approach 

  - Harvest YouTube channel data using the YouTube API by providing a 'Channel ID'.
    
  - Store channel data in MongoDB Atlas as documents
    
  - Convert MongoDB data into SQL records for data analysis.
    
  - Implement Streamlit to present code and data in a user-friendly UI.
    
  - Execute data analysis using SQL queries.
    

# Getting Started

  - Install/Import the necessary modules: Streamlit, Pandas, PyMongo, Psycopg2 and Googleapiclient.
    
  - Ensure you have access to MongoDB Atlas and set up a PostgresSQL DBMS on your local environment.
    

# Technical Steps to Execute the Project

### Step 1: Install/Import Modules

   - Ensure the required Python modules are installed: Streamlit, Pandas, PyMongo, Psycopg2 and Googleapiclient.

### Step 2: Utilize the methods and dataframes 

   - There are individual methods for channel, videos and comments, each with specific functionality for data extraction and transformation. These methods cover tasks like data retrieval, data storage, and data analysis.

### Step 3: Run the Project with Streamlit

   - Open the command prompt in the directory where "YtAPiproject.py" is located.
   - Execute the command: streamlit run Youtube.py. This will open a web browser, such as Google Chrome/Microsoft Edge, displaying the project's user interface.

### Step 4: Configure Databases

   - Ensure that you are connected to both MongoDB Atlas and your local PostgresSQL DBMS.


# Methods

   - Api_connect(): = Fetches the youtube channels data.
     
   - get_channel_info(channel_id): Provides channel details in JSON format.
     
   - get_channel_videos(channel_id): Returns video IDs for the given channel IDs.
     
   - get_video_info(video_ids): Provides video details for the given video IDs in JSON format.
     
   - get_comment_info(video_ids): Returns comments details for the given video IDd in JSON format.
     
   - channel_details(channel_id): Inserts channel data into MongoDB Atlas as a document.

   - Convert MongoDB Document to Dataframe: Fetches MongoDB documents and converts them into dataframes for SQL data insertion.
     
   - channels_table(): Creates a  channel table ,retrieves the channel details from MongoDB and inserts the data into the table.
     
   - video_tables(): Creates a  video table ,retrieves the video details from MongoDB and inserts the data into the table.

   - comments_table(): Creates a  comment table ,retrieves the comments details from MongoDB and inserts the data into the table.

   - tables(): channel_table(), video_tables(), comments_table() are combined into a single function.

   - show_channel_table(),show_videos_tables(),show_comments_table(): Visualize the output in stramlit application
     

# Tools Expertise 
   - Python (Scripting)
   - Data Collection
   - API Integration
   - Data Management using MongoDB (Atlas) and PostgreSQL
   - IDE: Visual Studio Code


# Result
   - This project focuses on harvesting YouTube data using the YouTube API, storing it in MongoDB, converting to SQL for analysis. Utilizes Streamlit, Python, and various methods. Expertise includes Python, MongoDB, SQL, API integration, and data management tools . This project mainly reduces 80% percentage of manually data processing and data storing work effectively.
