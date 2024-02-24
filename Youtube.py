from googleapiclient.discovery import build #(pip install google-api-python-client) --    
import pymongo                              #(pip install pymongo)                   |
import psycopg2                             #(pip install psycopg2)                  | --> install this library before importing these packages individually
import pandas as pd                         #(pip install pandas)                    |
import streamlit as st                      #(pip install streamlit)                --

#API CONNECTION
def Api_connect():
    Api_Id="AIzaSyDSGINlGmfrRep30gZNzI4zJ0bT56XFLYg" #get this api key from google developer console

    api_service_name = "youtube"
    api_version = "v3"
    youtube = build(api_service_name,api_version,developerKey=Api_Id)
    return youtube

youtube=Api_connect()


#COLLECTING CHANNELS INFORMATION FROM YOUTUBE
def get_channel_info(channel_id):
    
    request = youtube.channels().list(
                part = "snippet,contentDetails,Statistics",
                id = channel_id)
            
    response1=request.execute()

    for i in range(0,len(response1["items"])):
        data = dict(
                    Channel_Name = response1["items"][i]["snippet"]["title"],
                    Channel_Id = response1["items"][i]["id"],
                    Subscription_Count= response1["items"][i]["statistics"]["subscriberCount"],
                    Views = response1["items"][i]["statistics"]["viewCount"],
                    Total_Videos = response1["items"][i]["statistics"]["videoCount"],
                    Channel_Description = response1["items"][i]["snippet"]["description"],
                    Playlist_Id = response1["items"][i]["contentDetails"]["relatedPlaylists"]["uploads"],
                    )
        return data
    
#COLLECTING THE VIDEO IDS FROM THE CHANNELS
def get_channel_videos(channel_id):
    video_ids = []

    res = youtube.channels().list(id=channel_id, 
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None
    
    while True:
        res = youtube.playlistItems().list( 
                                           part = 'snippet',
                                           playlistId = playlist_id, 
                                           maxResults = 50,
                                           pageToken = next_page_token).execute()
        
        for i in range(len(res['items'])):
            video_ids.append(res['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None:
            break
    return video_ids

#COLLECTING THE VIDEO'S INFORMATION FROM THE CHANNELS
def get_video_info(video_ids):

    video_data = []

    for video_id in video_ids:
        request = youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id= video_id)
        response = request.execute()

        for item in response["items"]:
            data = dict(Channel_Name = item['snippet']['channelTitle'],
                        Channel_Id = item['snippet']['channelId'],
                        Video_Id = item['id'],
                        Title = item['snippet']['title'],
                        Tags = item['snippet'].get('tags'),
                        Thumbnail = item['snippet']['thumbnails']['default']['url'],
                        Description = item['snippet']['description'],
                        Published_Date = item['snippet']['publishedAt'],
                        Duration = item['contentDetails']['duration'],
                        Views = item['statistics']['viewCount'],
                        Likes = item['statistics'].get('likeCount'),
                        Comments = item['statistics'].get('commentCount'),
                        Favorite_Count = item['statistics']['favoriteCount'],
                        Definition = item['contentDetails']['definition'],
                        Caption_Status = item['contentDetails']['caption']
                        )
            video_data.append(data)
    return video_data

#COLLECTING THE COMMENT'S INFORMATION FROM THE CHANNEL'S VIDEOS
def get_comment_info(video_ids):
        Comment_Information = []
        try:
                for video_id in video_ids:

                        request = youtube.commentThreads().list(
                                part = "snippet",
                                videoId = video_id,
                                maxResults = 50
                                )
                        response5 = request.execute()
                        
                        for item in response5["items"]:
                                comment_information = dict(
                                        Comment_Id = item["snippet"]["topLevelComment"]["id"],
                                        Video_Id = item["snippet"]["videoId"],
                                        Comment_Text = item["snippet"]["topLevelComment"]["snippet"]["textOriginal"],
                                        Comment_Author = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                                        Comment_Published = item["snippet"]["topLevelComment"]["snippet"]["publishedAt"])

                                Comment_Information.append(comment_information)
        except:
                pass
                
        return Comment_Information


#CONNECTION WITH MONGODB 
client = pymongo.MongoClient("mongodb+srv://chopravalarmathi:S3PTb5maInNiAtwz@cluster0.senieqc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["Youtube_data"]

#UPLOADING THE COLLECTED DATA TO MONGODB
def channel_details(channel_id):
    ch_details = get_channel_info(channel_id)
    vi_ids = get_channel_videos(channel_id)
    vi_details = get_video_info(vi_ids)
    com_details = get_comment_info(vi_ids)

    coll1 = db["channel_details"]
    coll1.insert_one({"channel_information":ch_details,"video_information":vi_details,
                     "comment_information":com_details})
    
    return "upload completed successfully"

#CREATION OF TABLE FOR CHANNELS
def channels_table():
    mydb = psycopg2.connect(host="localhost",
                user="postgres",
                password="12345",
                database= "youtube_data",
                port = "5432"
                )
    cursor = mydb.cursor()

    drop_query = "drop table if exists channels"
    cursor.execute(drop_query)
    mydb.commit()

    try:
        create_query = '''create table if not exists channels(Channel_Name varchar(100),
                            Channel_Id varchar(80) primary key, 
                            Subscription_Count bigint, 
                            Views bigint,
                            Total_Videos int,
                            Channel_Description text,
                            Playlist_Id varchar(50))'''
        cursor.execute(create_query)
        mydb.commit()
    except:
         st.write("Channels Table alredy created")  

#FETCHING THE CHANNEL DATA'S FROM MONGODB
    ch_list = []
    db = client["Youtube_data"]
    coll1 = db["channel_details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])
    df = pd.DataFrame(ch_list)

#INSERTING THE FETCHED CHANNEL DATA'S INTO SQL TABLE
    for index,row in df.iterrows():
            insert_query = '''INSERT into channels(Channel_Name,
                                                        Channel_Id,
                                                        Subscription_Count,
                                                        Views,
                                                        Total_Videos,
                                                        Channel_Description,
                                                        Playlist_Id)
                                            VALUES(%s,%s,%s,%s,%s,%s,%s)'''
                

            values =(
                    row['Channel_Name'],
                    row['Channel_Id'],
                    row['Subscription_Count'],
                    row['Views'],
                    row['Total_Videos'],
                    row['Channel_Description'],
                    row['Playlist_Id'])
            try:                     
                cursor.execute(insert_query,values)
                mydb.commit()    
            except:
                st.write("channel values already inserted")


#CREATION OF TABLE FOR VIDEOS
def video_tables():
    mydb = psycopg2.connect(host="localhost",
                user="postgres",
                password="12345",
                database= "youtube_data",
                port = "5432"
                )
    cursor = mydb.cursor()

    drop_query = "drop table if exists videos"
    cursor.execute(drop_query)
    mydb.commit()

    try:
         create_query = '''create table if not exists videos(
                        Channel_Name varchar(150),
                        Channel_Id varchar(100),
                        Video_Id varchar(50) primary key, 
                        Title varchar(150), 
                        Tags text,
                        Thumbnail varchar(225),
                        Description text, 
                        Published_Date timestamp,
                        Duration interval, 
                        Views bigint, 
                        Likes bigint,
                        Comments int,
                        Favorite_Count int, 
                        Definition varchar(10), 
                        Caption_Status varchar(50))''' 
         cursor.execute(create_query)
         mydb.commit()

    except:
         st.write("videos table already created")

#FETCHING THE VIDEO DATA'S FROM MONGODB
    vi_list = []
    db = client["Youtube_data"]
    coll1 = db["channel_details"]
    for vi_data in coll1.find({},{"_id":0,"video_information":1}):
        for i in range(len(vi_data["video_information"])):
            vi_list.append(vi_data["video_information"][i])
    df2 = pd.DataFrame(vi_list)

#INSERTING THE FETCHED VIDEO DATA'S INTO SQL TABLE
    for index, row in df2.iterrows():
            insert_query = '''INSERT INTO videos(Channel_Name,
                            Channel_Id,
                            Video_Id, 
                            Title, 
                            Tags,
                            Thumbnail,
                            Description, 
                            Published_Date,
                            Duration, 
                            Views, 
                            Likes,
                            Comments,
                            Favorite_Count, 
                            Definition, 
                            Caption_Status 
                            )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

                    '''
            values = (
                        row['Channel_Name'],
                        row['Channel_Id'],
                        row['Video_Id'],
                        row['Title'],
                        row['Tags'],
                        row['Thumbnail'],
                        row['Description'],
                        row['Published_Date'],
                        row['Duration'],
                        row['Views'],
                        row['Likes'],
                        row['Comments'],
                        row['Favorite_Count'],
                        row['Definition'],
                        row['Caption_Status'])
            try:
                 cursor.execute(insert_query,values)
                 mydb.commit()
            except:
                 st.write("videos values are already inserted")


#CREATION OF TABLE FOR COMMENTS
def comments_table():
    mydb = psycopg2.connect(host="localhost",
                    user="postgres",
                    password="12345",
                    database= "youtube_data",
                    port = "5432"
                    )
    cursor = mydb.cursor()

    drop_query = "drop table if exists comments"
    cursor.execute(drop_query)
    mydb.commit()

    try:
         create_query = '''CREATE TABLE if not exists comments(Comment_Id varchar(200) primary key,
                                                            Video_Id varchar(80),
                                                            Comment_Text text, 
                                                            Comment_Author varchar(150),
                                                            Comment_Published timestamp)'''
         cursor.execute(create_query)
         mydb.commit()
    except:
         st.write("Comments table is already created")


#FETCHING THE COMMENT DATA'S FROM MONGODB
    com_list = []
    db = client["Youtube_data"]
    coll1 = db["channel_details"]
    for com_data in coll1.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data["comment_information"])):
            com_list.append(com_data["comment_information"][i])
            
    df3 = pd.DataFrame(com_list)

#INSERTING THE FETCHED COMMENT DATA'S INTO SQL TABLE
    for index, row in df3.iterrows():
                insert_query = '''
                    INSERT INTO comments (Comment_Id,
                                        Video_Id ,
                                        Comment_Text,
                                        Comment_Author,
                                        Comment_Published)
                    VALUES (%s, %s, %s, %s, %s)

                '''
                values = (
                    row['Comment_Id'],
                    row['Video_Id'],
                    row['Comment_Text'],
                    row['Comment_Author'],
                    row['Comment_Published'])
                try:
                     cursor.execute(insert_query,values)
                     mydb.commit()
                except:
                     st.write("comments values are already inserted")


#TRANSFERRING DATA'S FROM MONGODB TO SQL 
def tables():
    channels_table()
    video_tables()
    comments_table()

    return "Tables Created successfully"


#TO VIEW CHANNEL'S INFORMATION OUTPUT IN STREAMLIT
def show_channel_table():
        ch_list = []
        db = client["Youtube_data"]
        coll1 = db["channel_details"]
        for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
                ch_list.append(ch_data["channel_information"])
        df = st.dataframe(ch_list)

        return df

#TO VIEW VIDEO'S INFORMATION OUTPUT IN STREAMLIT
def show_videos_tables():
    vi_list = []
    db = client["Youtube_data"]
    coll1 = db["channel_details"]
    for vi_data in coll1.find({},{"_id":0,"video_information":1}):
        for i in range(len(vi_data["video_information"])):
            vi_list.append(vi_data["video_information"][i])
    df2 = st.dataframe(vi_list)

    return df2

#TO VIEW COMMENT'S INFORMATION OUTPUT IN STREAMLIT
def show_comments_table():
    com_list = []
    db = client["Youtube_data"]
    coll1 = db["channel_details"]
    for com_data in coll1.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data["comment_information"])):
            com_list.append(com_data["comment_information"][i])
    df3 = st.dataframe(com_list)

    return df3


#STREAMLIT PART
with st.sidebar:
    st.title(":red[YOUTUBE DATA HARVESTING AND WAREHOUSING]")
    st.header("SKILLS TAKE AWAY")
    st.caption('Python scripting Language')
    st.caption("MongoDB")
    st.caption("SQL")
    st.header("APPLICATIONS/DATABASE USED")
    st.caption("Mongo DataBase")
    st.caption("SQL")
    st.caption("Streamlit")

channel_id = st.text_input("Enter the Channel_ID")

if st.button("Collect and Store Data in MongoDB"):
    ch_ids=[]
    db=client["Youtube_data"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_ids.append(ch_data["channel_information"]["Channel_Id"])

    if channel_id in ch_ids:
        st.success("Channel Information for the given channel id already exists")

    else:
        insert=channel_details(channel_id)
        st.success(insert)

if st.button("Migrate to SQL"):
    Table=tables()
    st.success(Table)

show_table=st.radio("CHOOSE A OPTION BELOW TO  HAVE A TABLE VIEW ",("CHANNELS","VIDEOS","COMMENTS"))

if show_table=="CHANNELS":
    show_channel_table()

elif show_table=="VIDEOS":
    show_videos_tables()

elif show_table=="COMMENTS":
    show_comments_table()


#SQL QUERIES FOR THE GIVEN QUESTIONS
mydb = psycopg2.connect(host="localhost",
            user="postgres",
            password="12345",
            database= "youtube_data",
            port = "5432"
            )
cursor = mydb.cursor()

question=st.selectbox("Select your question from the below options available",("1.Name of all the videos and their channels",
                                                                                "2.Number of videos for the channels that has larrge number of videos",
                                                                                "3.Top 10 most viewed videos and their respective channels",
                                                                                "4.Number of comments on each video with their corresponding video names",
                                                                                "5.Channel name for the videos with highest number of likes",
                                                                                "6.Total number of likes and dislikes for each video with their corresponding video names",
                                                                                "7.Total number of views for each channel with their corresponding channel names",
                                                                                "8.Name of all the channels that has published videos in the year 2022",
                                                                                "9.Average duration of all videos in each channel with their corresponding channel names",
                                                                                "10.videos have the highest number of comments with their corresponding channel names"))

if question=="1.Name of all the videos and their channels":
    query1='''select title as videos,channel_name as channelname from videos'''
    cursor.execute(query1)
    mydb.commit()
    t1=cursor.fetchall()
    df=pd.DataFrame(t1,columns=["video title","channel name"])
    st.write(df)

elif question=="2.Number of videos for the channels that has larrge number of videos":
    query2='''select channel_name as channelname,total_videos as no_of_videos from channels 
                order by total_videos desc'''
    cursor.execute(query2)
    mydb.commit()
    t2=cursor.fetchall()
    df2=pd.DataFrame(t2,columns=["channel name","No of videos"])
    st.write(df2)

elif question=="3.Top 10 most viewed videos and their respective channels":
    query3='''select views as views,channel_name as channelname,title as videotitle from videos 
                where views is not null order by views desc limit 10'''
    cursor.execute(query3)
    mydb.commit()
    t3=cursor.fetchall()
    df3=pd.DataFrame(t3,columns=["views","channel name","videotitle"])
    st.write(df3)

elif question=="4.Number of comments on each video with their corresponding video names":
    query4='''select comments as no_of_comments,title as videotitle from videos where comments is not null'''
    cursor.execute(query4)
    mydb.commit()
    t4=cursor.fetchall()
    df4=pd.DataFrame(t4,columns=["no of comments","videotitle"])
    st.write(df4)

elif question=="5.Channel name for the videos with highest number of likes":
    query5='''select title as videotitle,channel_name as channelname,likes as likecount 
                from videos where likes is not null order by likes desc'''
    cursor.execute(query5)
    mydb.commit()
    t5=cursor.fetchall()
    df5=pd.DataFrame(t5,columns=["videotitle","channelname","likecount"])
    st.write(df5)

elif question=="6.Total number of likes and dislikes for each video with their corresponding video names":
    query6='''select likes as likecount,title as videotitle from videos'''
    cursor.execute(query6)
    mydb.commit()
    t6=cursor.fetchall()
    df6=pd.DataFrame(t6,columns=["likecount","videotitle"])
    st.write(df6)

elif question=="7.Total number of views for each channel with their corresponding channel names":
    query7='''select channel_name as channelname,views as totalviews from channels'''
    cursor.execute(query7)
    mydb.commit()
    t7=cursor.fetchall()
    df7=pd.DataFrame(t7,columns=["channelname","totalviews"])
    st.write(df7)

elif question=="8.Name of all the channels that has published videos in the year 2022":
    query8='''select title as video_title,published_date as videorelease,channel_name as channelname from videos
                where extract(year from published_date)=2022'''
    cursor.execute(query8)
    mydb.commit()
    t8=cursor.fetchall()
    df8=pd.DataFrame(t8,columns=["video_title","videorelease","channelname"])
    st.write(df8)

elif question=="9.Average duration of all videos in each channel with their corresponding channel names":
    query9='''select channel_name as channelname,AVG(duration) as averageduration 
                from videos group by channel_name'''
    cursor.execute(query9)
    mydb.commit()
    t9=cursor.fetchall()
    df9=pd.DataFrame(t9,columns=["channelname","averageduration"])
    st.write(df9)

elif question=="10.videos have the highest number of comments with their corresponding channel names":
    query10='''select title as videotitle,channel_name as channelname,
            comments as comments from videos where comments is not null order by comments desc'''
    cursor.execute(query10)
    mydb.commit()
    t10=cursor.fetchall()
    df10=pd.DataFrame(t10,columns=["videotitle","channelname","comments"])
    st.write(df10)
