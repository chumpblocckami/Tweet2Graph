import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import debug_errors
import glob
import pandas as pd
import dask.dataframe as dd
from dask.diagnostics import ProgressBar
import networkx as nx
import json
import os
import pymongo
from tqdm import tqdm
import tweepy
import time
import numpy
class Tweets2Graph():
    def __init__(self,interactions,username,npartitions=2):
        self.data = pd.DataFrame(columns=["user","retweet","quote","reply"])
        self.ddf = dd.from_pandas(pd.DataFrame(), npartitions=npartitions)
        self.graph = None
        self.interactions = interactions
        self.username = username
        self.mapping = self.get_mapping()

    def get_mapping(self):
        """
            From friendly naming of the activity on Twitter,
            map the related fields in json format.
        :return:
        """
        return {
            "retweet" : "retweeted_status",
            "quote" : "quoted_status",
            "reply" : "in_reply_to_screen_name",
            "mentions" : "mentions"
        }

    def from_file(self, path_2_file):
        """
        From a .csv or a nested .json, load data
        :param path_2_file:
        :return:
        """
        #load csv
        if path_2_file.endswith(".csv"):
            self.data = pd.read_csv(path_2_file)
            self.log.info("CSV loaded correctly")
        #load json
        elif path_2_file.endswith(".json"):
            with open(path_2_file+".json","r") as file:
                tmp = json.loads(file)
                for key in tqdm(tmp,desc="Loading from file"):
                    tmp_data = {"user": tmp[key]["user"][self.username]}
                    for activity in self.interactions:
                        if (self.mapping[activity] in tmp[key].keys()):
                            if activity == "reply":
                                source_user = tmp[key][self.mapping[activity]]
                            if activity == "retweet" or activity == "quote":
                                source_user = tmp[key][self.mapping[activity]]['user'][self.username]
                        else:
                            source_user = None
                        tmp_data[activity] = source_user
                    self.data = self.data.append(pd.Series(tmp_data), ignore_index=True, sort=True)
                del tmp, key
        else:
            raise debug_errors.UnsupportedFormat(format(path_2_file[:-3]))

    def from_folder(self,path_2_files, limit = 100):
        if os.listdir(path_2_files)[0].endswith("json"):
            pattern = glob.glob(path_2_files+'/*.json', recursive=True)
            for json_path in tqdm(pattern,desc="Loading from folder"):
                json_file = json.load(open(json_path))
                tmp_data = {"user": json_file["user"][self.username]}
                for activity in self.interactions:
                    if (self.mapping[activity] in json_file.keys()):
                        if activity == "reply":
                            source_user = json_file[self.mapping[activity]]
                        if activity == "retweet" or activity == "quote":
                            source_user = json_file[self.mapping[activity]]['user'][self.username]
                    else:
                        source_user = None
                    tmp_data[activity] = source_user
                self.data = self.data.append(pd.Series(tmp_data),ignore_index=True,sort=True)
            self.log.info("JSONs loaded correctly")

        elif os.listdir(path_2_files)[0].endswith("csv"):
            pattern = glob.glob(path_2_files + '/*.csv', recursive=True)[:limit]
            for csv_path in tqdm(pattern,desc="Loading from folder"):
                csv_file = pd.read_csv(csv_path)
                csv_file = csv_file[["user"]+self.interactions]
                self.data = self.data.append(csv_file,sort=True)
        else:
            raise debug_errors.UnsupportedFormat(format(path_2_files[:-3]))

    def from_dataframe(self, dataframe):
        self.data = dataframe[[self.interactions]]

    def from_mongo(self,connection_string,database,collection, query={}):
        cluster = pymongo.MongoClient(connection_string)
        db = cluster[database][collection]
        cursor = db.find(query)
        for document in tqdm(cursor, desc="Loading from mongoDB"):
            tmp_data = {"user": document["user"][self.username]}
            for activity in self.interactions:
                if (self.mapping[activity] in document.keys()):
                    if activity == "reply":
                        source_user = document[self.mapping[activity]]
                    if activity == "retweet" or activity == "quote":
                        source_user = document[self.mapping[activity]]['user'][self.username]
                else:
                    source_user = None
                tmp_data[activity] = source_user
                self.data = self.data.append(pd.Series(tmp_data), ignore_index=True, sort=True)

    def from_user(self, consumer_key, consumer_secret, access_token, access_token_secret, users=[]):
        '''
        Retrieve followers based on users. Requires valid Twitter API. It might take a while.
        :param username:
        :return:
        '''
        self.interactions = ["follow"]
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
        target_users = pd.DataFrame(columns=["user","follow"])
        for user in tqdm(users,desc="Getting user"):
            c = tweepy.Cursor(api.followers, user)
            for follower in c.items():
                target_users = target_users.append(pd.DataFrame([(user,follower.screen_name)],columns=["user","follow"]))
                time.sleep(numpy.random.uniform(0,1))
        self.data = target_users
        del target_users


    def fit(self,):
        for activity in self.interactions:
            rt = self.data.loc[pd.isna(self.data[activity]) == False][["user", activity]]
            rt.columns = ["source_user", "target_user"]
            self.ddf = self.ddf.append(dd.from_pandas(rt, npartitions=2, sort=True))

    def transform(self,connected_component = False):
        df_topic = self.ddf.groupby(["source_user", "target_user"]).size().reset_index()
        with ProgressBar():
            df_topic = df_topic.compute()
        df_topic.columns = ["source_user", "target_user", "weight"]

        topic_graph = nx.from_pandas_edgelist(df=df_topic,
                                              source="source_user",
                                              target="target_user",
                                              edge_attr="weight",
                                              create_using=nx.Graph)
        if connected_component:
            return nx.subgraph(topic_graph, max(nx.connected_components(topic_graph), key=len))
        return topic_graph

    def fit_transform(self):
        self.fit()
        graph = self.transform()
        self.log.info("Graph loaded and created correctly")
        return graph