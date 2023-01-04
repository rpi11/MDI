import csv
import json
import tweepy
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import community
import os

## GLOBALS
source=[]
target=[]
jsonObj = {}
CSET = "Twitter/altmetrics_climate_17_22_social.jsonl"
##

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

    def collect_retweets_by_id(self, tweet_id):
        try:
            status = self.api.get_retweets(tweet_id, tweet_mode="extended")
        except Exception as e:
            status = {
                "id_str": str(tweet_id),
                "error": str(e)
            }
        if len(status)>0:
            output=[]
            for elem in status:
                output.append(vars(elem)["_json"])
            return output
        else:
            return []
        
        # Returns list of dictionaries where each list element is the full tweet info of a retweet


def getTweetInfo(tweet):
    info={}
    if "created_at" in tweet:
        info["created_at"]=tweet["created_at"]
    if "full_text" in tweet:
        info["full_text"]=tweet["full_text"]
    if "retweet_count" in tweet:
        info["retweet_count"]=tweet["retweet_count"]
    if "user" in tweet:
        if "id" in tweet["user"]:
            info["user_id"]=tweet["user"]["id"]
        if "location" in tweet["user"]:
            info["user_id"]=tweet["user"]["id"]
        if "followers_count" in tweet["user"]:
            info["followers_count"]=tweet["user"]["followers_count"]
    return info

def getTweets(doi):

    global jsonObj
    if len(jsonObj)==0:
        jsonObj=pd.read_json(path_or_buf=CSET, lines=True)


    api_key_filepath = "Twitter/credKey.json"
    collector = TweetCollector(api_key_filepath)

    source.clear()
    target.clear()

    with open("results/tweetInfo_"+doi[:7]+"-"+doi[8:]+".json","w+") as out:
        tweets={
            "tweet_counts":{},
            "follower_counts":{}
        }

        for i in range(0,len(jsonObj)):
            print("# document count: "+str(i+1)+"/"+str(len(jsonObj)))
            postDict=jsonObj.iloc[i,6]
            citeDict=jsonObj.iloc[i,3]

            # Check if keys are in altmetrics data
            if not pd.isnull(postDict) and "twitter" in postDict \
                and not pd.isnull(citeDict) and "doi" in citeDict:
                #Check if this line is for a paper with a relevant doi
                if citeDict["doi"] == doi:
                    
                    print("++ number of tweets: "+str(len(postDict["twitter"])))
                    tweets[citeDict["doi"]]={}
                    tweets["tweet_counts"]["article -> tweet"]=len(postDict["twitter"])

                    j=1
                    for twt in postDict["twitter"]:
                        print("### tweet count: "+str(j)+"/"+str(len(postDict["twitter"])))
                        j=j+1

                        id=twt["tweet_id"]
                        
                        
                        tweet = collector.collect_tweets_by_id(id)
                        
                        if "retweeted_status" not in tweet: #only get original posts about article
                            addEdge(1, id)
                            tweets[citeDict["doi"]][id]=getTweetInfo(tweet)

                            if "followers_count" in tweets[citeDict["doi"]][id]:
                                if "article -> tweet" in tweets["follower_counts"]:
                                    tweets["follower_counts"]["article -> tweet"] += tweets[citeDict["doi"]][id]["followers_count"]
                                else:
                                    tweets["follower_counts"]["article -> tweet"] = tweets[citeDict["doi"]][id]["followers_count"]

                            '''
                            # GETS POST THAT TWEET IS RETWEETED FROM

                            if "retweeted_status" in tweet:
                                rt_from_id=tweet["retweeted_status"]["id"]
                                rt_from=collector.collect_tweets_by_id(rt_from_id)
                                tweets[citeDict["doi"]][id]["retweeted_FROM"]={}
                                tweets[citeDict["doi"]][id]["retweeted_FROM"][rt_from_id]=getTweetInfo(rt_from)
                                addEdge(rt_from_id, id)
                            '''

                            if "retweet_count" in tweet and tweet["retweet_count"]>0 :
                                retweetList=collector.collect_retweets_by_id(id)
                                tweets[citeDict["doi"]][id]["retweeted_TO"]={}

                                if len(retweetList)>0:
                                    
                                    if "tweet -> retweet" in tweets["tweet_counts"]:
                                        tweets["tweet_counts"]["tweet -> retweet"] += len(retweetList)
                                    else:
                                        tweets["tweet_counts"]["tweet -> retweet"] = len(retweetList)

                                    print("++++  number of tweet retweets: "+str(len(retweetList)))
                                    k=1
                                    for rt in retweetList:
                                        print("#####  tweet retweet count: "+str(k)+"/"+str(len(retweetList)))
                                        k=k+1

                                        rt_to_id=rt["id"]
                                        rt_to=collector.collect_tweets_by_id(rt_to_id)
                                        tweets[citeDict["doi"]][id]["retweeted_TO"][rt_to_id]=getTweetInfo(rt_to)

                                        addEdge(id, rt_to_id)

                                        if "followers_count" in tweets[citeDict["doi"]][id]["retweeted_TO"][rt_to_id]:
                                            if "tweet -> retweet" in tweets["follower_counts"]:
                                                tweets["follower_counts"]["tweet -> retweet"]+=\
                                                    tweets[citeDict["doi"]][id]["retweeted_TO"][rt_to_id]["followers_count"]
                                            else:
                                                tweets["follower_counts"]["tweet -> retweet"]=\
                                                    tweets[citeDict["doi"]][id]["retweeted_TO"][rt_to_id]["followers_count"]

                                        '''
                                        if rt_to["retweet_count"]>0:
                                            re_retweetList=collector.collect_retweets_by_id(rt_to_id)
                                            tweets[citeDict["doi"]][id]["retweeted_TO"][rt_to_id]["re_retweeted_TO"]={}

                                            if len(re_retweetList)>0:
                                                print("++++++  number of tweet re_retweets: "+str(len(re_retweetList)))
                                                l=1
                                                for r_rt in re_retweetList:
                                                    print("#######  tweet re_retweet count: "+str(l)+"/"+str(len(re_retweetList)))
                                                    l=l+1

                                                    r_rt_to_id=r_rt["id"]
                                                    r_rt_to=collector.collect_tweets_by_id(r_rt_to_id)
                                                    tweets[citeDict["doi"]][id]["retweeted_TO"][rt_to_id]["re_retweeted_TO"][r_rt_to_id]=\
                                                        getTweetInfo(r_rt_to)
                                                    
                                                    addEdge(rt_to_id,r_rt_to_id)
                                        '''

                    break

        json.dump(tweets,out,indent=4)
        writeEdges(doi)

def addEdge(s,t):
    source.append(s)
    target.append(t)

def writeEdges(doiOfInterest):
    with open("results/graphEdges_"+doiOfInterest[:7]+"-"+doiOfInterest[8:]+".csv", "w+") as f:
        writer=csv.writer(f)
        for i in range(0,len(source)):
            writer.writerow([source[i], target[i]])

def makeGraph(doiOfInterest):
    G = nx.DiGraph()
    with open("results/graphEdges_"+doiOfInterest[:7]+"-"+doiOfInterest[8:]+".csv", "r") as f:
        reader=csv.reader(f)

        article=["1"]
        tweets=[]
        retweets=[]

        for line in reader:
            source = line[0]
            target = line[1]

            if source == "1":
                if str(target) not in tweets:
                    tweets.append(str(target))
                if str(target) in retweets:
                    print("asdfasdf: "+target)
                    retweets.remove(str(target))
            else:
                if str(source) not in tweets:
                    tweets.append(str(source))
                if str(target) not in tweets:
                    if str(target) not in retweets:
                        retweets.append(str(target))
            
            G.add_edge(source, target)

       # print(tweets)
        colors=[]
        for node in G:
            if node in article:
                colors.append('yellow')
            elif node in tweets:
                colors.append('green')
            else:
                colors.append('red')

        
    
    #nx.draw(G)
    #plt.show()
    #nx.draw(G, node_color=colors, node_size=15, alpha=.75, arrowsize=3, with_labels=False)
    #plt.show()

    undirected_SG = G.to_undirected()
    unweighted_SG = nx.Graph()
    for u, v in undirected_SG.edges():
        unweighted_SG.add_edge(u, v)
    partition = community.best_partition(unweighted_SG) 
    
    colors_2=[]
    for node in unweighted_SG:
        if node in article:
            colors_2.append('yellow')
        elif node in tweets:
            colors_2.append('red')
        else:
            colors_2.append('blue')

    nx.draw_spring(unweighted_SG, node_color = colors_2, node_size=10, with_labels=False,\
        width=.1, edge_color="blue", )
    plt.show()


if __name__ == "__main__":

    '''
    for file in os.listdir("results"):
        if "graphEdges" in file:
            doi=file[11:18]+"/"+file[19:-4]
            print(doi+"\n")
            makeGraph(doi)
    '''

    doiOfInterest="10.1126/science.aan4399"
    #getTweets(doiOfInterest)
    makeGraph(doiOfInterest)

    '''
    doiOfInterest=[
        "10.1111/acv.12439",
        "10.1080/17524032.2019.1687537",
        "10.1038/s41467-019-12138-0",
        "10.1021/acs.est.9b04657",
        "10.1016/j.landusepol.2017.11.032",
        "10.1016/j.jhydrol.2017.07.027"
    ]
    '''
    '''
    with open("Twitter/foundMisinfo.json","r") as f:
        reader=json.load(f)
        for line in reader:
            print(line)
            getTweets(line)
    '''



    
    