import pymongo
import glob
import os
import time
import sys
import datetime
import calendar
from twarc import Twarc
import pandas as pd
from multiprocessing import Pool
import pandas
import threading
import re

# get the available api keys
with open('api_keys_hyd.txt') as f:
    df = pd.read_csv(f, sep=",")
api_keys = df.values.tolist()


num_to_month = {1: 'jan', 2: 'feb', 3: 'mar', 4: 'apr', 5: 'may', 6: 'jun', 7: 'jul'}

def get_and_save_data(id_col, t, mycol, count, path):
    """
    Use configured Twarc t to get full tweets given tweet ids id_col
    and save tweets in database.
    """
    for tweet in t.hydrate(id_col):
        x = None
        try:
            x = mycol.insert_one(tweet)
            count += 1
            print(count)
        except:
            print(sys.exc_info()[1])
            print(path)
        print(x)
        print(path)
        if count >= 166668: 
            break
    return count

def get_date_str(num):
    """
    Standardize the month and day string to 2 characters.
    """
    if num < 10:
        return '0' + str(num)
    else:
        return str(num)

def hydrate_ids(args):
    """
    Process the first 2 datasets of tweet ids and download the
    corresponding full tweets into database.

    Parameter:
        args - an array of [api_keys, month, start_day, end_day]
    """
    # connect to db
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myclient['covid-stigma21']
    mycol = mydb[num_to_month[args[1]]]
    print("Connected to db")

    # configure Twarc
    t = Twarc(args[0][0], args[0][1], args[0][2], args[0][3],
        app_auth=True, tweet_mode="extended")


    for day in range(args[2], args[3] + 1):
        c = 0
        mon_str = get_date_str(args[1])
        day_str = get_date_str(day)
        # process dataset 1
        base_dir_A = "/home/ahana/COVID-19-TweetIDs/"
        path = base_dir_A + \
            "2021-%s/coronavirus-tweet-id-2021-%s-%s-*.txt" \
             % (mon_str, mon_str, day_str)
        for file in glob.glob(path):
            try:
                with open(file) as f:
                    c = get_and_save_data(f, t, mycol, c, file)
                    
            except:
                print(path + '\n' + sys.exc_info()[1])

        
        # process dataset 2
        if args[1] > 2:
            base_dir_B = "/home/ahana/covid19_twitter/"
            path = base_dir_B + \
            "dailies/2021-%s-%s/2021-%s-%s-dataset.tsv.gz" \
             % (mon_str, day_str, mon_str, day_str)
            if os.path.exists(path):
                #log_file.write('[start] [%s] %s\n' % (time.ctime(), path))
                df = pd.read_csv(path, sep='\t')
                try:
                    c = get_and_save_data(df['tweet_id'].tolist(), t,
                                    mycol, c, path)

                except:
                    print(path + '\n' + sys.exc_info()[1])
          
  


def main(month):
    """
    Hydrate ids in dataset 1 and 2 for month
    """
    args = []
    last_day = calendar.monthrange(2021, month)[1]

    for j in range(39 - last_day):
        args.append([api_keys[j], month, 2 * j + 1, 2 * j + 2])
    for j in range(13 - (39 - last_day)):
        args.append([api_keys[j+8], month, 79 - 2 * last_day + 3 * j,
                        81 - 2 * last_day + 3 * j])
    threads = []
    for k in range(13):
        thread = threading.Thread(target=hydrate_ids, args=(args[k],))
        threads.append(thread)
        thread.start()
    for m in range(13):
        threads[m].join()


if __name__ == '__main__':
    print('start', time.ctime())
    main(3) # 3 for March, change acc for other months
    print(time.ctime())
