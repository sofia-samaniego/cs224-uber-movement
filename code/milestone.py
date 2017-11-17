
################################################################################
# CS 224W (Fall 2017) - Project
# Uber Movement
# Authors:
# jvrsgsty@stanford.edu
# pearson3@stanford.edu
# sofiasf@stanford.edu
# Last Updated: Nov 2, 2017
################################################################################

import snap
import matplotlib.pyplot as plt
import numpy as np
import random
import scipy.stats
import time
import collections
import networkx as nx

path_adjacency = '../data/washington/washington_DC_censustracts.csv'
path_weights = '../data/washington/washington-2016-1_1.csv'
path_longlat = '../data/washington/washington_DC_censustracts_centroid.csv'

def loadPNEANGraph(path):
    """
    :param - path: path to edge list file

    return type: snap.PNEANGraph
    return: Graph loaded from edge list at @path

    """
    ############################################################################

    Graph = snap.LoadEdgeList(snap.PNEANet, path, 0, 1, ",")

    print('Number of nodes: %d' %Graph.GetNodes())
    print('Number of edges: %d' %snap.CntUniqUndirEdges(Graph))

    return Graph


def loadNGraph(path):
    """
    :param - path: path to edge list file

    return type: snap.PNGraph
    return: Graph loaded from edge list at @path

    """
    ############################################################################

    Graph = snap.LoadEdgeList(snap.PNGraph, path, 0, 1, ",")

    print('Number of nodes: %d' %Graph.GetNodes())
    print('Number of edges: %d' %snap.CntUniqUndirEdges(Graph))

    return Graph


def loadWeights(path):
    """
    :param - path: path to edge list file

    return type: dictionary (key = node pair (a,b), value = sign)
    return: Return sign associated with node pairs. Both pairs, (a,b) and (b,a)
    are stored as keys. Self-edges are NOT included.
    """
    means = collections.defaultdict(float)
    sds = collections.defaultdict(float)
    g_means = collections.defaultdict(float)
    g_sds = collections.defaultdict(float)
    with open(path, 'r') as ipfile:
        for line in ipfile:
            if line[0] != '#':
                line_arr = line.split(',')
                if line_arr[0] == line_arr[1]:
                    continue
                node1 = int(line_arr[0])
                node2 = int(line_arr[1])
                mean = float(line_arr[3])
                sd = float(line_arr[4])
                g_mean = float(line_arr[5])
                g_sd = float(line_arr[6])
                means[(node1, node2)] = mean
                sds[(node1, node2)] = sd
                g_means[(node1, node2)] = g_mean
                g_sds[(node1, node2)] = g_sd
    return means, sds, g_means, g_sds

def add_weights(graph, weights, Attr):
    """
    :param - graph: graph of type snap.PNEANGraph
    :param - weights: defaultdict mapping pairs of nodes to weight
    :param - attr: string equal to the type of weights being added
             For example:  "mean_time"

    return type: snap.PNEANGraph
    return: graph with edges weighted using param: weights
    """
    for EdgeI in graph.Edges():
        N1 = EdgeI.GetSrcNId()
        N2 = EdgeI.GetDstNId()
        graph.AddFltAttrDatE(EdgeI, means[(N1, N2)], Attr)

    return graph

def computePageRank(graph, Attr):
    """
    :param - graph: weighted graph of type snap.PNEANGraph
    :param - attr: string equal to the type of weights used to
    compute the pageRank. For example: "mean_time"

    return type: snap.TIntFltH()
    return: a dictionary mapping node id to page rank
    """
    PRankH = snap.TIntFltH()
    snap.GetWeightedPageRank(graph, PRankH, Attr, 0.85, 1e-4, 100)
    return PRankH

def computeWeightedBetweennessCentr(graph, Attr):
    """
    :param - graph: weighted graph of type snap.PNEANGraph
    :param - attr: string equal to the type of weights used to
    compute the betweenessCentr. For example: "mean_time"

    return type: snap.TIntFltH()
    return: a dictionary mapping node id to betweeness centrality measure
    """
    NIdBtwH = snap.TIntFltH()
    EdgeBtwH = snap.TIntPrFltH()

    attr = snap.TFltV()
    for edge in graph.Edges():
        attr.Add(graph.GetFltAttrDatE(edge, Attr))

    snap.GetWeightedBetweennessCentr(graph, NIdBtwH, EdgeBtwH, attr, 1.0, True)

    return NIdBtwH

def graphViz(graph, nodeWeight, Attr):
    """
    :param - graph: weighted graph of type snap.PNEANGraph
    :param - nodeWeight: dictionary with key: node id, value: weight
    :param - attr: string equal to the type of weights used to
    compute the betweenessCentr. For example: "mean_time"

    return: saves a plot
    """
    G=nx.Graph()
    latlong = np.genfromtxt(path_longlat, delimiter=',')

    for NodeI in graph.Nodes():
        nodeID = NodeI.GetId()
        G.add_node(nodeID, nodeWeight = nodeWeight[NodeI.GetId()], pos = (latlong[nodeID-1][0], latlong[nodeID-1][1]))
    for EdgeI in graph.Edges():
        N1 = EdgeI.GetSrcNId()
        N2 = EdgeI.GetDstNId()
        G.add_edge(N1, N2, edgeWeight = graph.GetFltAttrDatE(EdgeI, Attr))

    nodes, nodeWeight = zip(*nx.get_node_attributes(G,'nodeWeight').items())
    edges, edgeWeight = zip(*nx.get_edge_attributes(G,'edgeWeight').items())

    pos = nx.spring_layout(G,k=0.5,iterations=20)
    nx.draw(G, nx.get_node_attributes(G, 'pos'), arrows = True, node_shape = '.', with_labels = False, nodelist=nodes, node_color=nodeWeight, \
        edge_list=edges, edge_color=[np.log(y+1) for y in edgeWeight], width=.5, node_cmap=plt.cm.Blues, edge_cmap=plt.cm.Blues)
    plt.savefig("nodes1.pdf")

if __name__ == "__main__":
    geoGraph = loadPNEANGraph(path_adjacency)
    means, sds, g_means, g_sds = loadWeights(path_weights)
    weightedGeoGraph = add_weights(geoGraph, means, "mean_time")
    pageRank = computePageRank(weightedGeoGraph, "mean_time")
    betweenCentr = computeWeightedBetweennessCentr(weightedGeoGraph, "mean_time")

    graphViz(weightedGeoGraph, betweenCentr, "mean_time")
