import pandas as pd
import csv
import numpy as np
import os
import pymongo
import glob
import time
import sys
import datetime
import calendar
import tweepy
from multiprocessing import Pool
import threading
import re
import json
import pickle
from csv import DictWriter
from csv import writer

def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)


def append_dict_as_row(file_name, dict_of_elem, field_names):
    with open(file_name, 'a+', newline='') as write_obj:
        dict_writer = DictWriter(write_obj, fieldnames=field_names)
        dict_writer.writerow(dict_of_elem)


# get the available api keys
with open('api_keys_hyd.txt') as f:
    df = pd.read_csv(f, sep=",")
api_keys = df.values.tolist()

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

D = {} # Key is user screen name and value is hate score

class month:
  def __init__(self, name, num, days):
    self.name = name
    self.num = num
    self.days = days

m = []
m.append( month('Mar', 3, 31) ) 

def get_date_str(num):
    """
    Standardize the month and day string to 2 characters.
    """
    if num < 10:
        return '0' + str(num)
    else:
        return str(num)

def getNameByMon(mon):
  global D
  for d in range(16,27):
    d_str = get_date_str(d) 

    dir = "keyword_based_dataset_no_dup/" + mon.name + "/" + mon.name + " " + d_str + ".csv"
    if os.path.exists(dir):
      df = pd.read_csv(dir, encoding='utf-8', parse_dates=["created_at"])
      for i in range(len(df['user_sn'])):

         if df['user_sn'][i] in D:
          
           if df['score'][i]>3:
             D[df['user_sn'][i]][0] = 1 + D[df['user_sn'][i]][0]
      
         else:
           if df['score'][i]>3:  
             D[df['user_sn'][i]]= []
             D[df['user_sn'][i]].append(1)


    else:
      print(dir + '\n' + sys.exc_info()[1]) 


getNameByMon(m[0])
with open("Users_Mar_16-26.json", "w") as f:
    json.dump(D, f, cls=NpEncoder)   


num_to_month = {3: 'mar', 4: 'apr', 5: 'may', 6: 'jun', 7: 'jul'}

def follower_ids(args):
    """
    Parameter:
        args - an array of [api_keys, month, start_day, end_day]
    """
    
    f = open('Users_Mar_16-26.json',) # List of Hate users during Mar 16-26 2020
    D2 = json.load(f)

    consumer_key = args[0][0]
    consumer_secret = args[0][1]
    access_token = args[0][2]
    access_token_secret = args[0][3]

    # authorization of consumer key and consumer secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  
    # set access to user's access key and access secret 
    auth.set_access_token(access_token, access_token_secret)
  
    # calling the api 
    api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=False)

    field_names = ['Name','Fol']
    for day in range(args[2], args[3] + 1): 
      d_str = get_date_str(day-1)

      if day==31:
        for i in range(38*(day-1),1183):
          name = list(D2)[i]
          D = {}
          D['Name'] = name
          D['Fol'] = []
          
          try:

            for follower in tweepy.Cursor(api.friends, screen_name=name).items():
              D['Fol'].append(follower.screen_name)
              # print(follower.screen_name)
              
          except:
            D['Fol'].append('Nan') 
          append_dict_as_row('/home/ahana/Fol_list/List2_Mar_16-26.csv', D, field_names)
          append_list_as_row('/home/ahana/Fol_list/Count2_Mar_16-26.csv', [i])
          print(i) 
            

      else:
        for i in range (38*(day-1),38*(day)):
          name = list(D2)[i]
          D = {}
          D['Name'] = name
          D['Fol'] = []
          try:

            for follower in tweepy.Cursor(api.friends, screen_name=name).items():
              D['Fol'].append(follower.screen_name)
              # print(follower.screen_name)
              
          except:
            D['Fol'].append('Nan')
          append_dict_as_row('/home/ahana/Fol_list/List2_Mar_16-26.csv', D, field_names)
          append_list_as_row('/home/ahana/Fol_list/Count2_Mar_16-26.csv', [i])
          print(i) 
 
      
      print(day)
      
       

def main(month):

    args = []
    last_day = calendar.monthrange(2020, month)[1]

    for j in range(39 - last_day):
        args.append([api_keys[j], month, 2 * j + 1, 2 * j + 2])
    for j in range(13 - (39 - last_day)):
        args.append([api_keys[j+8], month, 79 - 2 * last_day + 3 * j,
                        81 - 2 * last_day + 3 * j])
    threads = []
    for k in range(13):
        thread = threading.Thread(target=follower_ids, args=(args[k],))
        threads.append(thread)
        thread.start()
    for m in range(13):
        threads[m].join()


      

if __name__ == '__main__': 

    print('start', time.ctime())

    main(3)
    
    print(time.ctime())      
