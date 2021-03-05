# Tweet2Graph
*Fast* and **easy** social graphs from tweets

![Logo](./images/logo.png)


## Installation

To install using pip, use

`pip install tweet2graph`

## Usage

* **Import the library**:

``` python
from tweet2graph import Tweets2Graph
```
* **Choose which interaction between users are relevant for you**:
 ``` python
 backend = Tweets2Graph(interactions=["retweet","quote","reply"], #relevant interactions
                           username="screen_name")                #name of the nodes
```

* **Load dataset**
 ``` python
 #load a single .csv/.json file
 backend.from_file("examples/csv/1614874276.csv")
 
 #load a folder 
 backend.from_folder("examples/csv/")
 
 #load from a mongodb collections
 backend.from_mongo(connection_string='<CONNECTION_STRING>',
                     database=db,
                     collection=collections")
 #or simply, from a pandas dataframe
 backend.from_dataframe(dataframe)
 ```
 * **Fit/Transform**
  ``` python
  #organize data
  backend.fit()
  #create graph
  graph = backend.transform()
  
  #or simply
  graph = backend.fit_transform()
   ```
   
  * **Show and save**
  ``` python
  import networkx as nx
  nx.draw(graph,with_labels=False,node_size=5,font_size=5,font_color="red",node_color="black")
  nx.write_adjlist(G=graph)
  ```
 ![graphs](./images/graph.png)
 ## TODO:
 - [ ] Insert mentions in possible interactions
 - [ ] Add speed benchmark
 - [ ] Add from_stream() method
 - [ ] Add Dockerfile

## License

##### MIT
