from sqlalchemy import create_engine

import pandas as pd
import numpy as np

from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer

import json

        
def extractStars(row):
    """Lambda function to extract number of stars left in rating"""
    return float(row.split(' ')[0]) 

def extractHelpful(row):
    """Lambda function to extract number of upvotes on Amazon"""
    rev = row.split(' ')[0]
    
    if(rev.isnumeric()):
        return int(rev)
    elif(rev=="one"):
        return 1
    else:
        return 0
    
def extractDate(row):
    """Lambda function to convert string into datetime object"""
    date = pd.to_datetime(row[33:])
    return date

def convertTime(rev):
    """Lambda function to abstract datetime object per month for groupby"""
    corr_date = rev-pd.offsets.MonthBegin(1) 
    return corr_date

def countWords(rev):
    """Lambda function to count all words in a particular review"""
    return len(word_tokenize(rev))



# define function to read data from PostgreSQL server
def readData(table="eucerin_intensive_lotion", 
         engine=create_engine("postgresql://postgres:postgres@localhost/CPG")):
    
    # connect engine
    conn = engine.connect()
    
    # try making query asked for
    try:
        query = f"SELECT * FROM {table}"
        # attempt to read table queried
        data = pd.read_sql(query,conn)
    except:
        # output default data
        query = "SELECT * FROM eucerin_intensive_lotion"
        data = pd.read_sql(query,conn)
    
    return data


# perform data loading and transforming in one function
def read_transform(table="eucerin_intensive_lotion",
                   engine=create_engine("postgresql://postgres:postgres@localhost/CPG")):
    """Docstring: makes query to PostgreSQL database using the table defined.
    Performs all transformations, including cleaning prior to returning dataframe"""
    
    # read in raw data from PostgreSQL
    data = readData(table,engine)
    


    # transformations
    data["stars"] = data.apply(lambda x: extractStars(x["stars"]),axis=1)
    data["helpful"] = data.apply(lambda x: extractHelpful(x["helpful"]),axis=1)
    data["review_date"] = data.apply(lambda x: extractDate(x["review_date"]),axis=1)
    data["corr_date"] = data.apply(lambda x: convertTime(x["review_date"]),axis=1)
    data["word_count"] = data.apply(lambda x: countWords(x["review"]),axis=1)
    
    # perform groupby on month to get aggregate data
    gb = data.groupby('corr_date')["stars"].mean()
    
    # find review with maximum upvoted comments
    idx = data["helpful"].argmax()
    max_upvoted_review = data["review"][idx]

    # populate dictionary containing all data to pass back to route
    ratings_dict = {}
    ratings_dict["review_date"] = list(data["review_date"])
    ratings_dict["gb_date"] = gb.index.astype(str).tolist()
    ratings_dict["avg_monthly_rating"] = list(gb)
    ratings_dict["histogram_rating_values"] = np.histogram(data["stars"], bins=[1,2,3,4,5,6])[0].tolist()
    ratings_dict["histogram_rating_bins"] = np.histogram(data["stars"], bins=[1,2,3,4,5,6])[1].tolist()
    ratings_dict["max_upvoted_review"] = max_upvoted_review
    
    return data, ratings_dict