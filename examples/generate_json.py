import tweepy
import json
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        try:
            if len(os.listdir("examples/json/"))>100:
                print("Capped.")
                return

            print(status._json["user"]["screen_name"])
            with open("examples/json/"+str(round(datetime.timestamp(datetime.now())))+".json","w") as file:
                json.dump(status._json,file)
        except Exception as e:
            print(e)
            pass

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
myStream.filter(track=['#sanremo2021','#sanremo'], is_async=True)