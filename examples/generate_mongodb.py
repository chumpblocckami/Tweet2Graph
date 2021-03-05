import tweepy
import json
import pymongo

with open("./psswd.json", "r") as file:
    credentials = json.load(file)

consumer_key = credentials["consumer_key"]
consumer_secret = credentials["consumer_secret"]
access_token = credentials["access_token"]
access_token_secret = credentials["access_token_secret"]
cluster = pymongo.MongoClient(credentials["cluster"])
collections_name = "sanremo"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        try:
            print(status._json["user"]["screen_name"])
            collection = cluster.TWEETS["sanremo"]
            collection.insert_one(status._json)
        except Exception as e:
            print(e)
            pass

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
myStream.filter(track=['#sanremo2021','#sanremo'], is_async=True)