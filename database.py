import sqlite3
from datasets import load_dataset
import pandas as pd

# USERS(FIRST_NAME, LAST_NAME)
# RESPONSES(FIRST_NAME, LAST_NAME, TWEET_ID, EMOTION)
# EMOTIONS(EMOTION_ID, EMOTION_STR)
# TWEETS(TWEET, TWEET_ID)

connect = sqlite3.connect('database.db')
connect.execute('''
    CREATE TABLE IF NOT EXISTS USERS (
    FIRST_NAME TEXT,
    LAST_NAME TEXT,
    PRIMARY KEY (FIRST_NAME, LAST_NAME)
    )
    ;'''
)

connect.execute('''
    CREATE TABLE IF NOT EXISTS EMOTIONS (
    EMOTION_ID int PRIMARY KEY,
    EMOTION TEXT NOT NULL
    );
    '''             
)

connect.execute('''
    CREATE TABLE IF NOT EXISTS RESPONSES (
        FIRST_NAME TEXT,
        LAST_NAME TEXT,
        TWEET_ID int,
        EMOTION_ID int,
        
    CONSTRAINT USER_FK 
        FOREIGN KEY (FIRST_NAME, LAST_NAME)
        REFERENCES USERS (FIRST_NAME, LAST_NAME)
    
    CONSTRAINT EMOTION_FK
        FOREIGN KEY (EMOTION_ID)
        REFERENCES EMOTIONS(EMOTION_ID)
    )
    '''
)

ds = load_dataset("dair-ai/emotion", split = "train")
ds = ds.with_format("pandas")
ds = ds.add_column("TWEET_ID", range(0, len(ds)))
ds.to_sql('TWEETS', con=connect, if_exists='append', index=False)

emotions = ds.features["label"]._str2int
emotions = [(emotions[name], name) for name in emotions]
connect.executemany('''INSERT INTO EMOTIONS VALUES (?, ?)''', emotions)
connect.execute('''ALTER TABLE TWEETS RENAME COLUMN text TO TWEET''')
connect.execute('''ALTER TABLE TWEETS DROP COLUMN label''')

connect.commit()