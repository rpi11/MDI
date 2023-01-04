#######################################
# In-class exercise week 10
#
# Network analysis
#
# We are using the networkx library
# It is already installed with Anaconda
# Documentation:
# https://networkx.readthedocs.io/en/stable/
#
# Also using community library
# Installation directions MAC:
# https://bitbucket.org/taynaud/python-louvain
# pip install python-louvain
# Installation for Windows
# https://pypi.python.org/pypi/louvain/#downloads
#######################################

import networkx as nx
import matplotlib.pyplot as plt
import community
# NOTE:
# some of you may need to do the following for the import
# import community.community_louvain as community

# Get the karate club network
myNetXGraph=nx.karate_club_graph()

####### VISUALIZE NETWORK
# Draw the network using the default settings
nx.draw(myNetXGraph)
plt.show()

# Draw, but change the color to to blue
nx.draw(myNetXGraph, node_color='blue')
plt.show()

####### COMPUTE & PRINT NETWORK STATS
# Prints summary information about the graph
print(nx.info(myNetXGraph))

# Print the degree of each node
print("Node Degree")
for v in myNetXGraph:
    print('%s %s' % (v,myNetXGraph.degree(v)))

# Compute and print other stats    
nbr_nodes = nx.number_of_nodes(myNetXGraph)
nbr_edges = nx.number_of_edges(myNetXGraph)
nbr_components = nx.number_connected_components(myNetXGraph)

print("Number of nodes:", nbr_nodes)
print("Number of edges:", nbr_edges)
print("Number of connected components:", nbr_components)


# Compute betweeness and then store the value with each node in the networkx graph
betweenList = nx.betweenness_centrality(myNetXGraph)
print();
print("Betweeness of each node")
print(betweenList)

#####################
# Clustering
#####################
# Conduct modularity clustering
partition = community.best_partition(myNetXGraph)

# Print clusters (You will get a list of each node with the cluster you are in)
print();
print("Clusters")
print(partition)

# Get the values for the clusters and select the node color based on the cluster value
values = [partition.get(node) for node in myNetXGraph.nodes()]
nx.draw_spring(myNetXGraph, cmap = plt.get_cmap('jet'), node_color = values, node_size=100, with_labels=False)
plt.show()

# Determine the final modularity value of the network
modValue = community.modularity(partition,myNetXGraph)
print("modularity:", modValue)

