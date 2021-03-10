from Tweets2Graph import Tweets2Graph
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
import os
import time
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    from examples import generate_csv
    #generate_csv.generate(10,10,33)

    backend = Tweets2Graph(interactions=["retweet","quote","reply"],
                           username="screen_name")
    backend.from_stream(hashtags=["#covid"],skip_error=False)

    time.sleep(10^100)
    print("Loading data",datetime.now())
    #backend.from_folder("examples/csv/")
    backend.from_user(users=["ollo_tv"])
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