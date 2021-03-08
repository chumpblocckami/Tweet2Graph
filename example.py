from Tweets2Graph import Tweets2Graph
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    from examples import generate_csv
    #generate_csv.generate(10,10,33)

    backend = Tweets2Graph(interactions=["retweet","quote","reply"],
                           username="screen_name")
    print("Loading data",datetime.now())
    #backend.from_folder("examples/csv/")
    backend.from_user(users=["ollo_tv"],
                      consumer_key=os.environ.get("CONSUMER_KEY"),
                      access_token=os.environ.get("ACCESS_TOKEN"),
                      access_token_secret=os.environ.get("ACCESS_TOKEN_SECRET"),
                      consumer_secret=os.environ.get("CONSUMER_SECRET"))
    print("Number of tweets", backend.data.shape)
    print("Fit",datetime.now())
    backend.fit()
    print("Transform", datetime.now())
    graph = backend.transform()
    print("show",datetime.now())
    nx.draw(graph,with_labels=False,node_size=5,font_size=2,font_color="red",node_color="black")
    plt.show()
    print("Transform",datetime.now())
    graph = backend.transform()
    print("END",datetime.now())
    nx.draw(graph,with_labels=True,node_size=5,font_size=15,font_color="red",node_color="black")
    plt.show()
    print("something else?")