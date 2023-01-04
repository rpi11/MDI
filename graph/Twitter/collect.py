#!/usr/bin/env python
# coding: utf-8

'''
@title: Utilities for working on Twitter data
@authors: Kornraphop Kawintiranon (Ken)
@institution: Georgetown University
@project: Tweet Collector
@date: April 2022
@updated: April 2022
@description: Utilities for working on Twitter data
'''


import json
import tweepy


class TweetCollector():
    """ A class to collect tweets. """

    def __init__(self, api_key_filepath):
        # Read credential file
        with open(api_key_filepath, "r") as f:
            data = json.load(f)
        consumer_key = data["app_key"]
        consumer_secret = data["app_secret"]
        access_token = data["oauth_token"]
        access_token_secret = data["oauth_token_secret"]

        # Init API client
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

    def collect_tweets_by_id(self, tweet_id):
        try:
            status = self.api.get_status(tweet_id, tweet_mode="extended")
        except Exception as e:
            status = {
                "id_str": str(tweet_id),
                "error": str(e)
            }
        return status if isinstance(status, dict) else status._json

if __name__ == "__main__":
    '''
    testOut="test_collected_tweet.json"
    import pandas as pd
    obj=pd.read_json(path_or_buf=testOut, lines=True)
    print(obj.full_text)
    exit()
    '''

    file_path = "altmetrics_climate_17_22_social.jsonl"
    import pandas as pd
    import csv
    jsonObj = pd.read_json(path_or_buf=file_path, lines=True)
    
    citeIdx=3
    postIdx=6
    
    with open("test_collected_tweet.json", "w") as f:

        api_key_filepath = "credKey.json"
        collector = TweetCollector(api_key_filepath)
        tweetInfo={}
        j=0
        for i in range(0,len(jsonObj)):
            if not pd.isnull(jsonObj.iloc[i,postIdx]) and "twitter" in jsonObj.iloc[i,postIdx] \
                and not pd.isnull(jsonObj.iloc[i,citeIdx]) and "doi" in jsonObj.iloc[i,citeIdx]:
                doi=jsonObj.iloc[i,citeIdx]["doi"]
                for twt in jsonObj.iloc[i,postIdx]["twitter"]:
                    id=twt["tweet_id"]
                    tweet = collector.collect_tweets_by_id(id)
                    if "full_text" in tweet:
                        j+=1
                        tweetInfo[doi]={
                            "tweet_id":id,\
                            "full_text":tweet["full_text"].replace('\n',""), \
                            "retweeted":tweet["retweeted"]
                            }
            print("Total: "+str(i))
            print("Collected: "+str(j))
            print("\n")
        json.dump(tweetInfo,f,indent=4)