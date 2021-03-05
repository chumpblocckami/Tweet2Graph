from gephistreamer import graph
from gephistreamer import streamer
#https://github.com/totetmatt/GephiStreamer
#DA FARE
stream = streamer.Streamer(streamer.GephiWS(hostname="localhost", port=8080, workspace="workspace0"),)
node_a = graph.Node("A",custom_property=1)
node_b = graph.Node("B",custom_property=2)
node_c = graph.Node("C",custom_property=3)
node_d = graph.Node("D",custom_property=4)

stream.add_node(node_a,node_b)
edge_ab = graph.Edge(node_a,node_b,custom_property="hello")
stream.add_edge(edge_ab)
