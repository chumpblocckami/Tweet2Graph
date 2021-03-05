from Tweets2Graph import Tweets2Graph
from dask_load import dask_load
from dask.distributed import Client
import time

print("Tweets2Graph read function")
start_time = time.time()
b = Tweets2Graph(interactions=["retweet"],username="screen_name")
b.from_folder("examples/json/")
print("--- %s seconds ---" % (time.time() - start_time))

print("dask read function")
client = Client(n_workers=4, threads_per_worker=1)
start_time = time.time()
dask_load("examples/json/*.json")
print("--- %s seconds ---" % (time.time() - start_time))

