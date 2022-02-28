import pandas as pd
import csv
import numpy as np
import os
import matplotlib.pyplot as plt
import re
from wordcloud import WordCloud, STOPWORDS
import sys
import time
from datetime import datetime

class month:
  def __init__(self, name, num, days):
    self.name = name
    self.num = num
    self.days = days

m = []
m.append( month('Mar', 3, 31) )
m.append( month('Apr', 4, 30) )
m.append( month('May', 5, 31) )
m.append( month('Jun', 6, 30) )
m.append( month('Jul', 7, 31) )


def get_date_str(num):
    """
    Standardize the month and day string to 2 characters.
    """
    if num < 10:
        return '0' + str(num)
    else:
        return str(num)

def getTweetsByMon(mon):
  tweets = pd.read_csv("/home/ahana/keyword_based_dataset_no_dup/" + mon.name + "/" + mon.name + " " + "01.csv", encoding='utf-8', parse_dates=["created_at"])
  tweets = pd.DataFrame(tweets)
  
  for d in range(2,mon.days+1):
    d_str = get_date_str(d) 

    dir = "/home/ahana/keyword_based_dataset_no_dup/" + mon.name + "/" + mon.name + " " + d_str + ".csv"
    if os.path.exists(dir):
      df = pd.read_csv(dir, encoding='utf-8', parse_dates=["created_at"])
      df = pd.DataFrame(df)
      tweets = tweets.append([df], ignore_index = True)  
      
    

  return tweets 
   
print('start', time.ctime())

tweets = getTweetsByMon(m[0])   

for i in range(1,5):
  t = getTweetsByMon(m[i])
  tweets = tweets.append(t,ignore_index = True)

tweets['text_new'] = ''

import re

for i in range(len(tweets['full_text'])):
    m = re.search('(?<=:)(.*)', tweets['full_text'][i])
    try:
        tweets['text_new'][i]=m.group(0)
    except AttributeError:
        tweets['text_new'][i]=tweets['full_text'][i]

def wordcloud(tweets,name):
    stopwords = set(STOPWORDS)
    stopwords.add("https")
    stopwords.add("ONE")
    stopwords.add("NAN")
    stopwords.add("NOW")
    stopwords.add("EVEN")
    stopwords.add("CO")
    stopwords.add("AMP")
    stopwords.add("VIRU")
    stopwords.add("CCP")
    stopwords.add("SAID")
    stopwords.add("SAY")
    stopwords.add("CHINA")
    stopwords.add("COVID")
    stopwords.add("COVID19")
    stopwords.add("COUNTRIE")
    stopwords.add("CORONAVIRU")
    stopwords.add("CORONAVIRUS")
    stopwords.add("CORONA")
    stopwords.add("VIRUS")
    stopwords.add("T5NLGOUUSW")
    stopwords.add("HW3AJEFJSV")
    stopwords.add("T")
    stopwords.add("U")
    stopwords.add("S")
    stopwords.add("WORLD")
    wordcloud = WordCloud(width=700, height=400, background_color="white",stopwords=stopwords,random_state = 2016).generate(" ".join([i for i in tweets['text_new'].astype(str).str.upper()]))
    plt.figure( figsize=(20,10)) 
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig(name + ".png")
    

wordcloud(tweets,"ADAU5") # All days all users
wordcloud(tweets[tweets['score']>3],"ADHU5") # All days hate users

tweets['created_at'] = pd.to_datetime(tweets['created_at'], errors='coerce', utc=True)
tweets['created_at'].dt

days = [[12, 13, 14, 17, 18, 19, 23, 26, 27, 29, 30, 31],[1,2,9,10,11,12,15,16,27],[1,2,3,4,5,7,10,11,12,13,20,21,25,29],[6,7,8,9,10,11,16,17,18,19,20,22,30],[6,7,10,11,21,22,23,24,30,31]]
tweet = pd.DataFrame()
for i in range(5): 
  for j in range(len(days[i])):
    date_string = '2020-' + get_date_str(i+3) + '-' + get_date_str(days[i][j])
    d = datetime.strptime(date_string, '%Y-%m-%d').date()
    df = tweets.loc[tweets['created_at'].dt.date==d]
    tweet = tweet.append(df)

wordcloud(tweet,"HDAU5") # Hate days all users
wordcloud(tweet[tweet['score']>3],"HDHU5") # Hate days hate users

print(time.ctime())  
