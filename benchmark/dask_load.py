import dask.bag as db
import json
from datetime import datetime

def dask_load(path_2_file):
    def flatten(json):
        return {
            "user": json["user"]["screen_name"],
            "retweet":json["retweeted_status"]['user']["screen_name"] if "retweeted_status" in json.keys() else None,
            "quote": json["quoted_status"]['user']["screen_name"] if "quoted_status" in json.keys() else None,
            "reply": json["in_reply_to_screen_name"] if "in_reply_to_screen_name" in json.keys() else None
        }
    x = db.read_text(path_2_file).map(json.loads)
    n = x.map(flatten).to_dataframe()
    n = n.compute().dropna()
    return n
