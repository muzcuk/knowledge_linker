#import pyximport; pyximport.install()
import scipy.sparse as scp
import numpy as np
from heapq import heappush, heappop, heapify


def bottleneck_undir_full(G, retpath=False):
    rows = []
    paths = []
    N = G.shape[0]
    for s in xrange(N):
        row, p = bottleneck_undir(G, s, retpath=retpath)
        rows.append(row)
        paths.append(p)
    return np.asarray(rows), paths

def bottleneck_undir(G, s, targets=None, retpath=False):
    '''
    Return the bottleneck capacity and paths from node s. If no targets are
    specified, will return the capacities for all possible targets in the graph.
    '''
    N = G.shape[0]
    if targets is None:
        targets = xrange(N)
    capacities = []
    paths = []
    for t in targets:
        c, p = bottleneck_undir_st(G, s, t, retpath=retpath)
        paths.append(p)
        capacities.append(c)
    capacities = np.asarray(capacities)
    return capacities, paths

def bottleneck_undir_st(G, s, t, retpath=False):
    """
    Returns the bottleneck capacity and path between source node s and 
    target node t for a given graph G.
    """
    def _neighbors(node, G):
        return G.indices[G.indptr[node]:G.indptr[node+1]]
    Q = []
    path = []
    visited = set([s])
    s_nbrs = _neighbors(s, G)
    if s==t or t in s_nbrs:
        if s==t:
            path = [t]
        else:
            path = [s,t]
        bottleneck = 1.0
    else:
        items = {} # contains 3-tuple: distance, node, predecessor
        # init the heap
        for n in xrange(G.shape[0]):
            if n==s:
                dist = 1.0
            else:
                dist = 0.0
            items[n] = [-dist,n,-1]
            heappush(Q,items[n])
        while t not in visited:
            dist_n,n,_ = heappop(Q)
            nbrs = _neighbors(n, G)
            if len(nbrs)>0:
                for nbr in nbrs:
                    dist_nbr,_,pred = items[nbr]
                    if nbr==t:
                        items[nbr][0] = -max([-dist_nbr,-dist_n])
                        if -dist_n > -dist_nbr:
                            items[nbr][2] = n
                    else:
                        if min([-dist_n, G[n,nbr]]) > -dist_nbr:
                            items[nbr][0] = -min([-dist_n, G[n,nbr]])
                            items[nbr][2] = n
                heapify(Q)
            visited.add(n)
        bottleneck = -items[t][0]
        if retpath:
            # trace the path
            tracenode = t
            path.insert(0,t)
            while True:
                predecessor = items[tracenode][2]
                if predecessor >= 0:
                    path.insert(0, predecessor)
                    tracenode = predecessor
                    if tracenode == s:
                        break
                else:
                    path = []
                    break
    if retpath == True:
        return bottleneck, path 
    else:
        return bottleneck, None
