#######################################
# Homework 5
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
#
# The data set can be found here:
# https://snap.stanford.edu/data/soc-sign-bitcoin-otc.html
#
#######################################

import networkx as nx
import matplotlib.pyplot as plt
import community
# NOTE:
# some of you may need to do the following for the import
# import community.community_louvain as community

# Build the graph
G = nx.DiGraph()
with open('soc-sign-bitcoinotc.csv', 'r') as f:
    for line in f:
        data = line.strip().split(',')
        source = int(data[0])
        target = int(data[1])
        weight = int(data[2])
        G.add_edge(source, target, weight=weight)

####### VISUALIZE NETWORK
# Draw the network using the default settings
# We are using a small subgraph so we can draw it quickly.
small_G = G.subgraph([i for i in range(0,100)])  # this gets the subgraph of G for nodes 0-99
nx.draw(small_G)
plt.show()

# Draw, but change some drawing properties
nx.draw(small_G, node_color='blue', node_size=15, alpha=0.5, arrowsize=5)
plt.show()

####### COMPUTE & PRINT NETWORK STATS
# Prints summary information about the graph
print(nx.info(G))

# Print the degree of each node
print("Node, Degree")
for v in list(small_G.nodes())[:10]:
    print('{}, {}'.format(v, small_G.degree[v]))

# Compute and print other stats
nbr_nodes = len(small_G.nodes())
nbr_edges = len(small_G.edges())

print("Number of nodes:", nbr_nodes)
print("Number of edges:", nbr_edges)

# Change G to an undirected graph and find the number of CCs
undirected_SG = small_G.to_undirected()
nbr_components = nx.number_connected_components(undirected_SG)
print("Number of connected components:", nbr_components)


# Compute betweeness centralities and then store the value with each node in the networkx graph
centralities = nx.betweenness_centrality(small_G)
print()
print("Betweeness of each node")
for node in list(small_G.nodes())[:10]:
    print(centralities[node])

#####################
# Clustering
#####################
# Conduct modularity clustering
# Create an unweighted version of G because modularity works only on graphs with non-negative edge weights
unweighted_SG = nx.Graph()
for u, v in undirected_SG.edges():
    unweighted_SG.add_edge(u, v)
partition = community.best_partition(unweighted_SG)

# Print clusters (You will get a list of each node with the cluster you are in)
print()
print("Clusters")
print(partition)

# Get the values for the clusters and select the node color based on the cluster value
values = [partition.get(node) for node in unweighted_SG.nodes()]
nx.draw_spring(unweighted_SG, cmap = plt.get_cmap('jet'), node_color = values, node_size=10, with_labels=False)
plt.show()

# Determine the final modularity value of the network
modValue = community.modularity(partition, unweighted_SG)
print("modularity: {}".format(modValue))

