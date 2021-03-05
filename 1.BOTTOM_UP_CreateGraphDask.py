import dask.dataframe as dd
import glob
import pandas as pd
import networkx as nx
from dask.diagnostics import ProgressBar
from tqdm import tqdm
import pickle
import os
import igraph
import sys
from datetime import datetime 
from cleantext import clean
import re
import logging
import sys
sys.path.append("./utils/")
import sanitize

def loadhd(topic):
    print(str(datetime.now()),"START load graph")
    if "ddf_depression.pkl" in os.listdir("./../data/database/"):
        with open("./../data/database/ddf_depression.pkl","rb") as file:
            ddf = pickle.load(file)
        file.close()
    else:
        path_2_database = "./../data/database/depression/"
        count = 0
        csvs = [path_2_database+x for x in os.listdir(path_2_database)]
        print(topic, "elementi caricati",len(csvs))

        ddf  = dd.from_pandas(pd.DataFrame(), npartitions=2)
        for csv in tqdm(csvs):
            try:
               tmp = pd.read_hdf(csv)[["user_name","RT_user_name","in_reply_to_user_name","QT_user_name"]]
            except Exception as e:
                print("\n",csv,e)
                continue

            if tmp.shape[0] == 0:
                print("No data for "+csv)
                continue

            rt = tmp.loc[pd.isna(tmp["RT_user_name"])==False][["user_name","RT_user_name"]]
            rt.columns = ["source_user","target_user"]
            ddf = ddf.append(dd.from_pandas(rt,npartitions=2))

            rp = tmp.loc[pd.isna(tmp["in_reply_to_user_name"])==False][["user_name","in_reply_to_user_name"]]
            rp.columns = ["source_user","target_user"]
            ddf = ddf.append(dd.from_pandas(rp,npartitions=2))

            qt = tmp.loc[pd.isna(tmp["QT_user_name"])==False][["user_name","QT_user_name"]]
            qt.columns = ["source_user","target_user"]
            ddf = ddf.append(dd.from_pandas(qt,npartitions=2))

            count = count + tmp.shape[0]
            del qt, rp, rt

        print("TOTAL TWEETS:",count)
        with open("./../data/database/ddf_depression.pkl", "wb") as file:
            pickle.dump(ddf, file)
        file.close()
    print(str(datetime.now()),"END load graph")
    return ddf

def get_atlas(graph):
    from fa2 import ForceAtlas2
    forceatlas2 = ForceAtlas2(
            # Behavior alternatives
            outboundAttractionDistribution=True,  # Dissuade hubs
            linLogMode=False,  # NOT IMPLEMENTED
            adjustSizes=False,  # Prevent overlap (NOT IMPLEMENTED)
            edgeWeightInfluence=1.0,

            # Performance
            jitterTolerance=1.0,  # Tolerance
            barnesHutOptimize=True,
            barnesHutTheta=1.2,
            multiThreaded=False,  # NOT IMPLEMENTED

            # Tuning
            scalingRatio=2.0,
            strongGravityMode=False,
            gravity=1.0,

            # Log
            verbose=True)
    G = igraph.Graph.TupleList(ccn_graph.edges(), directed=False)
    layout = forceatlas2.forceatlas2_igraph_layout(G, pos=None, iterations=1000)
    return layout
        # igraph.plot(G, "graph.png", layout=layout).show()

def polarity_graph(ddf):
    print("creating graph")
    df_topic_positive = ddf.groupby(["source_user", "target_user"])["POSITIVE"].sum().reset_index()
    print("Compute positive values")
    with ProgressBar():
            df_topic_positive = df_topic_positive.compute()

    df_topic_negative = ddf.groupby(["source_user", "target_user"])["NEGATIVE"].sum().reset_index()
    print("Compute negative values")
    with ProgressBar():
        df_topic_negative = df_topic_negative.compute()

    df_topic_value = pd.merge(df_topic_positive, df_topic_negative, on=["source_user", "target_user"])
    df_topic_value["WEIGHT"] = df_topic_value["POSITIVE"] - df_topic_value["NEGATIVE"]
    print("Numero utenti unici:", len(set(df_topic_value["source_user"].unique().tolist() + df_topic_value["target_user"].unique().tolist())))
    del df_topic_positive, df_topic_negative
    
    topic_graph = nx.from_pandas_edgelist(df=df_topic_value,
                                          source="source_user",
                                          target="target_user",
                                          edge_attr=["WEIGHT"],
                                          create_using=nx.Graph)
    return topic_graph

def topology_graph(ddf):
    print("START creating graph", str(datetime.now()))
    df_topic = ddf.groupby(["source_user", "target_user"]).size().reset_index()
    with ProgressBar():
        df_topic = df_topic.compute()
    df_topic.columns = ["source_user", "target_user", "weight"]

    topic_graph = nx.from_pandas_edgelist(df=df_topic,
                                          source="source_user",
                                          target="target_user",
                                          edge_attr="weight",
                                          create_using=nx.Graph)

    print("END creating graph", str(datetime.now()))
    df_topic["weight"].value_counts().sort_index()
    print("GRAFO NON PREPROCESSATO")

    print("\n", nx.info(topic_graph))
    df_topic = df_topic.loc[df_topic["weight"] > 1]
    topic_graph = nx.from_pandas_edgelist(df=df_topic,
                                          source="source_user",
                                          target="target_user",
                                          edge_attr="weight",
                                          create_using=nx.Graph)
    print("GRAFO PREPROCESSATO")
    print("\n", nx.info(topic_graph))
    #print("SAVING EDGELIST")
    #df_topic.to_csv("./../data/TOP_DOWN/"+topic+"/"+topic+"_edgelist.csv",index=False)
    del df_topic
    return topic_graph

if __name__ == "__main__":

    try:
        topic = sys.argv[1]
        print("SIAMO IN CMD")
    except:
        topic = "depression"
    
    print("TOPIC SELECTED:",topic)
    path_2_database = "./../data/database/depression/"
    ddf = loadhd(topic = topic)
    #topic_graph = polarity_graph(ddf)
    topic_graph = topology_graph(ddf)

    print("---" * 10)
    print(str(datetime.now()), "GRAFO TOTALE")
    print(nx.info(topic_graph))
    print("Grafo diretto?",nx.is_directed(topic_graph))
    print("Grafo pesato?", nx.is_weighted(topic_graph))
    print("Grafo connesso?", nx.is_connected(topic_graph))

    print("---" * 10)
    print(str(datetime.now()),": computing connected component")
    largest_cc = max(nx.connected_components(topic_graph), key=len)
    ccn_graph = topic_graph.subgraph(largest_cc)
    del topic_graph
    del largest_cc
    print("\nCC", "\n", nx.info(ccn_graph))
    print("Grafo diretto?",nx.is_directed(ccn_graph))
    print("Grafo pesato?", nx.is_weighted(ccn_graph))
    print("Grafo connesso?", nx.is_connected(ccn_graph))

    print("---"*10)
    print(str(datetime.now()), ": computing connected component normalized")
    copied_graph = ccn_graph.copy()
    copied_graph.remove_nodes_from([node for node, degree in dict(ccn_graph.degree()).items() if degree < 2])
    del ccn_graph

    print("\nCCN", "\n", nx.info(copied_graph))
    print("Grafo diretto?",nx.is_directed(copied_graph))
    print("Grafo pesato?", nx.is_weighted(copied_graph))
    print("Grafo connesso?", nx.is_connected(copied_graph))

    with open("./../data/BOTTOM_UP/GRAPH/depression_ccn.pkl", "wb") as file:
        pickle.dump(copied_graph, file)
    file.close()

    pd.DataFrame(copied_graph.nodes).to_csv("./../data/BOTTOM_UP/GRAPH/depression_nodes.csv", index=False)
    nx.write_gexf(copied_graph, "./../data/BOTTOM_UP/GRAPH/depression_graph.gexf")
    nx.to_pandas_edgelist(copied_graph,source="source",target="target").to_csv("./../data/BOTTOM_UP/GRAPH/depression_edgelist.csv",index=False)

    input("Continuare provando a calcolare la modularity?")

    #print("START",str(datetime.now()))
    #print("COMMUNITY USING MODULARITY")
    #from networkx.algorithms.community import greedy_modularity_communities
    #communities = list(greedy_modularity_communities(copied_graph.to_undirected()))
    #print("FINISH",str(datetime.now()))
    #print("Lunghezza community",sorted([len(x) for x in communities])[-4:])

    #with open("./../data/TOP_DOWN"+topic+"/"+topic+"_community.pkl","wb") as file:
    #    pickle.dump(communities,file)

    #largest_comms = sorted(communities,key=len)[-4:]