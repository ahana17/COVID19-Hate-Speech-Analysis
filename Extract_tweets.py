import pymongo
import time
import re
import csv 
import sys
import pandas as pd
import spacy
from nltk.corpus import wordnet
import html
#import nltk

# set up spacy
nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
# nltk.download('wordnet')
def include_keyword(full_text, keywords):
    ########### Inclusion Criteria ###########
    # eat + animal
    # bio + weapon
    # wet + market
    ##########################################
    animals = ['bat', 'animal', 'snake', 'dog', 'rat', 'soup', 'cat', 
                'critter', 'swine', 'pig', 'meat']
    score = 0
    # clean the text and split cleaned text into tokens and get their lemma
    temp = re.sub(r"[\n\t\r]{1,}", " ", full_text)
    temp = html.unescape(temp)
    temp = re.sub(r"(http|www)\S+", "", temp)
    temp = re.sub(r"[,.;@#?!&$]+\ *", " ", temp)
    temp = re.sub(r"\s{2,}", " ", temp)
    tokens = nlp(temp)

    eat_animal = [0, 0]
    bio_weapon = [0, 0]
    wet_market = [0, 0]
    for token in tokens:
        lemma = token.lemma_
        if lemma[0] == '-' and token.text[0] != '-':
            lemma = token.text
        lemma = lemma.lower()
        if lemma in keywords:
            if lemma not in ['eat', 'bio', 'weapon', 'wet', 'market']:
                if lemma in keywords:
                    score += 1
            if lemma == 'eat':
                eat_animal[0] = 1
            if lemma in animals:
                eat_animal[1] = 1
            if lemma == 'wet':
                wet_market[0] = 1
            if lemma == 'market':
                wet_market[1] = 1
            if lemma == 'bio':
                bio_weapon[0] = 1
            if lemma == 'weapon':
                bio_weapon[1] = 1
    if sum(eat_animal) == 2:
        score += 1
    if sum(wet_market) == 2:
        score += 1
    if sum(bio_weapon) == 2:
        score += 1
    return score

    

def parse_hashtags(hashtags):
    result = []
    for item in hashtags:
        result.append(item['text'])
    return ' '.join(result)

def parse_urls(urls):
    result = []
    for item in urls:
        result.append(item['expanded_url'])
    return ' '.join(result)

def get_keywords():
    df = pd.read_csv('/home/ahana/keywords.txt', header=None, names=['keywords'])
    df = df.drop_duplicates()
    keywords = df['keywords'].to_list()

    # replace keywords with their corresponding lemma
    lemmas = []
    for word in keywords:
        parsed_word = nlp(word)
        lemma = parsed_word[0].lemma_
        if lemma[0] == '-' and parsed_word[0].text != '-':
            lemma = parsed_word[0].text
        lemma = lemma.lower()
        if lemma not in lemmas:
            lemmas.append(lemma)
    return lemmas

def main():
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myclient['covid-stigma']
    mycol1 = mydb['may']
    mycol2 = mydb['jun']
    mycol3 = mydb['jul']
    mycol4 = mydb['tweets']
    mycols = [mycol1,mycol2,mycol3,mycol4]

    

    lemmas = get_keywords()

    for mycol in mycols:
        # look for syntax on mongodb 
        tweets = mycol.find({'lang': 'en'},
            {
                'id': 1,
                'full_text': 1,
                'created_at': 1,
                'user.screen_name': 1,
                'user.followers_count': 1,
                'favorite_count': 1,
                'retweet_count': 1,
                'user.location': 1,
                'place': 1
            }
             # twitter object API 
        )



        print('got the cursor:', time.ctime())

        for tweet in tweets:
            full_text = tweet['full_text']
            # omit RT
            if full_text[0:2] == 'RT':
                continue
            
            if re.search('chinese|china|asian|ccp', full_text, re.I) is None:
                continue
            
            score = include_keyword(full_text, lemmas)

            if score > 3: # Hate tweets->tweets having score above 3
                longitude = None
                latitude = None
                location = None
                user_loc = None
                if 'place' in tweet and tweet['place'] != None:
                    try:
                        if longitude == None:
                            if  tweet['place']['bounding_box'] != None and tweet['place']['bounding_box']['coordinates'] != None:
                                temp1 = 0
                                temp2 = 0
                                for j in tweet['place']['bounding_box']['coordinates'][0]:
                                    temp1 += j[0]
                                    temp2 += j[1]
                                longitude = temp1 / len(tweet['place']['bounding_box']['coordinates'][0])
                                latitude = temp2 / len(tweet['place']['bounding_box']['coordinates'][0])        
                            location = str(tweet['place']['full_name']) + ', ' + str(tweet['place']['country'])
                    except:
                        print(sys.exc_info()[1])
                if 'location' in tweet['user'] and tweet['user']['location'] not in [None, ""] :
                    user_loc = tweet['user']['location']

                newrow = [str(tweet['id']), 
                        score,
                        tweet['full_text'], 
                        tweet['created_at'], 
                        tweet['user']['screen_name'],

                        tweet['user']['followers_count'], 
                        tweet['retweet_count'],
                        tweet['favorite_count'],
                        
                        longitude,
                        latitude,
                        location,
                        user_loc]
        
                tweets_file = open('/home/ahana/data2/keyword-based/%s/%s.csv' % (tweet['created_at'][4:7], tweet['created_at'][4:10]), 'a', newline='')
                writer = csv.writer(tweets_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(newrow)
                tweets_file.flush()
                tweets_file.close()
                

        print('complete')       
    

if __name__ == '__main__':

    print(time.ctime())
    main()
    print(time.ctime())