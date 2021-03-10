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
                     database='<DB_NAME>',
                     collection='<COLLECTION_NAME>')
                     
 #or from a pandas dataframe
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
- [x] add connected component
- [x] `.from_user('<USER_NAME>')` method
- [ ] Add metadata to tweet
- [ ] Insert mentions in possible interactions
- [ ] Add custom error and better explanation
- [ ] Add speed benchmark and figures
- [x] Add `.from_stream(id="<hashtag>")` method
- [ ] Update `.from_stream(id="<hashtag>")` with two distinct processes
- [ ] Dockerfile

## License

##### MIT
