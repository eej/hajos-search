#!/usr/bin/env python


"""

Hajos utilities.

"""


from util import *


# Hajos Sum
def hajosSum(G1, G2, x1, y1, x2, y2):
    G = []
    for i in range(len(G1)):
        G.append(G1[i][:])
        G[i].extend([0 for x in range(len(G2)-1)])

    for i in range(len(G2)-1):
        G.append([0 for x in range(len(G1) + len(G2) - 1)])

    indexMap = []
    for i in range(len(G2)):
        if i < x2:
            indexMap.append(len(G1)+i)
        elif i == x2:
            indexMap.append(x1)
        elif i > x2:
            indexMap.append(len(G1)+i-1)
            
            
    for i in range(len(G2)):
        for j in range(len(G2)):
            if i != j:
                if G2[i][j] == 1:
                    G[indexMap[i]][indexMap[j]] = 1
                    G[indexMap[j]][indexMap[i]] = 1

    G[x1][y1] = 0
    G[y1][x1] = 0
    G[indexMap[x2]][indexMap[y2]] = 0
    G[indexMap[y2]][indexMap[x2]] = 0
    G[y1][indexMap[y2]] = 1
    G[indexMap[y2]][y1] = 1
                    
    return G

# identify vertex
def identify(G, pair):
    newG = []
    for col in G:
        newG.append(col[:])

    for i in range(len(G)):
        if i != pair[0]:
            if G[i][pair[1]] == 1:
                #print pair, i
                newG[i][pair[0]] = 1
                newG[pair[0]][i] = 1
        newG[pair[1]][i] = -1
        newG[i][pair[1]] = -1
   
    #print "---------------------"
    #print pair
    #printGraph(G)
    #print ""
    #printGraph(newG)
    #print "---------------------"

    newG = newG[:pair[1]] + newG[pair[1]+1:]
    for i in range(len(newG)):
        newG[i] = newG[i][:pair[1]] + newG[i][pair[1]+1:]
    #if not isSymetric(newG):
    #    print "screwed up while trying to merge", pair
    #    print "\n".join(map(str,G))
    #    print "###############################################"
    #    print "\n".join(map(str,newG))
    return newG


def mergeSubgraphs(t, sub1, sub2):
    # uhhhmmm hajos sum on lists?  Or something like that.

    #print t
    #print sub1
    #print sub2

    new1 = set()
    for e in sub1:
        new1.add(sortPair(e))
    if sortPair((t[0],t[2])) in new1:
        new1.remove(sortPair((t[0],t[2])))

    new2 = set()
    for e in sub2:
        new2.add(sortPair(e))
    if sortPair((t[1],t[2])) in new2:
        new2.remove(sortPair((t[1],t[2])))

    ret = new1.union(new2)
    ret.add(sortPair((t[0], t[1])))

    #print "ret:", ret

    return ret


def takeSubgraph(G, edges):
    # given a graph and edge list, return the subgraph consisting of the listed edges,
    # and a mapping between the vextex indicies.

    vertexSet = set()
    for e in edges:
        vertexSet.add(e[0])
        vertexSet.add(e[1])

    vertexList = sorted(list(vertexSet))
    #m = [-1 for v in vertexList]
    m = {}
    for i in xrange(len(vertexList)):
        m[vertexList[i]] = i

    N = newGraph(len(vertexList))
    for e in edges:
        N[m[e[0]]][m[e[1]]] = 1
        N[m[e[1]]][m[e[0]]] = 1

    return N, vertexList

def edgesToVerts(s):
    """ Turn a list of edges into a list of verticies """

    o = set()
    for e in s:
        o.add(e[0])
        o.add(e[1])
    return o

def getAllTripples(G):

    triList = []

    for i in xrange(len(G)-1):
        for j in xrange(i+1,len(G)):
            if G[i][j]:
                for k in xrange(len(G)):
                    if k != i and k != j and (not G[i][k]) and (not G[j][k]):
                        triList.append((i,j,k))

    return triList

def getTripplesOnEdge(G,e):

    triList = []

    for i in xrange(len(G)):
        if (i not in e) and (not G[i][e[0]]) and (not G[i][e[1]]):
            triList.append((e[0],e[1],i))

    return triList



# Return a list of edges that would turn kites into 4-cliques if added.
def getKiteEdges(G):
    L = set()
    for i in xrange(len(G)-2):
        for j in xrange(i+1,len(G)-1):
            if G[i][j] == 1:
                for k in xrange(j+1,len(G)):
                    #print i,j,k
                    if G[i][k]==1 and G[j][k]==1:
                        #print i, j, k, "found"
                        # We have a triangle.
                        #for l in range(k+1, len(G)):
                        for l in xrange(i+1,len(G)):
                            if l != k and G[l][i]==1 and G[l][j]==1:
                            #if G[l][i]==1 and G[l][j]==1:
                                #print "add", (l,k)
                                L.add(sortPair((l, k)))
                            if l != j and G[l][i]==1 and G[l][k]==1:
                            #if G[l][i]==1 and G[l][k]==1:
                                #print "add", (l,j)
                                L.add(sortPair((l, j)))
                            if l != i and G[l][k]==1 and G[l][j]==1:
                            #if G[l][k]==1 and G[l][j]==1:
                                #print "add", (l,i)
                                L.add(sortPair((l, i)))

    return L


# returns a set of edges forming a double kite or 5 wheel from a defining tripple
def getEdgesFromKite(G,tri):
    L = set([sortPair([tri[1], tri[2]])])

    for v in (tri[1], tri[2]):
        done = False
        for i in xrange(len(G)):
            if i in tri:
                continue  
            if G[i][tri[0]] and G[i][v]:
                for j in xrange(len(G)):
                    if j in (i,) + tri:
                        continue
                    if G[i][j] and G[j][tri[0]] and G[j][v]:
                        L.add(sortPair((v,i)))
                        L.add(sortPair((v,j)))
                        L.add(sortPair((i,j)))
                        L.add(sortPair((i,tri[0])))
                        L.add(sortPair((j,tri[0])))
                        done = True
                        break

            if done:
                break

    if len(L) not in (10, 11):
        print
        print L
        print tri
        #import util
        #util.displayGraph(G)
        print "Oops"
        print "Cliqie:", hasClique(G)
        exit()

    return L


# returns a set of edges from a clique
def getEdgesFromClique(G,C):
    L = [ [C[0],C[1]],
          [C[0],C[2]],
          [C[0],C[3]],
          [C[1],C[2]],
          [C[1],C[3]],
          [C[2],C[3]]]

    return set([sortPair(x) for x in L])


# returns a set of edges from a clique
def getEdgesFromKClique(E):
    C = list(E)
    L = set()
    for i in range(len(C)-1):
        for j in range(i+1, len(C)):
            L.add( (C[i], C[j]) ) 

    return set([sortPair(x) for x in L])


# Get the list of missing edges that could form 4-cliques, and see if any of them pair for an add edge rule.
# (returns true if there is a five wheel or double kite subgraph, kite edge list otherwise)
def leafCheckBase(G):
    #print "clique: ", hasClique(G)
    edgeList = tuple(getKiteEdges(G))
    #print edgeList
    #t = '5'
    for i in xrange(len(edgeList)-1):
        for j in xrange(i+1, len(edgeList)):
            if edgeList[i][0] == edgeList[j][0] and G[edgeList[i][1]][edgeList[j][1]] == 1:
                #print edgeList[i][0], edgeList[i][1], edgeList[j][1]
                #if len(getEdgesFromKite(G, (edgeList[i][0], edgeList[i][1], edgeList[j][1]))) == 11:
                #    t = 'h'
                return True, (edgeList[i][0], edgeList[i][1], edgeList[j][1])
            if edgeList[i][0] == edgeList[j][1] and G[edgeList[i][1]][edgeList[j][0]] == 1:
                #print edgeList[i][0], edgeList[i][1], edgeList[j][0]
                #if len(getEdgesFromKite(G, (edgeList[i][0], edgeList[i][1], edgeList[j][0]))) == 11:
                #    t = 'h'
                return True, (edgeList[i][0], edgeList[i][1], edgeList[j][0])
            if edgeList[i][1] == edgeList[j][0] and G[edgeList[i][0]][edgeList[j][1]] == 1:
                #print edgeList[i][1], edgeList[i][0], edgeList[j][1]
                #if len(getEdgesFromKite(G, (edgeList[i][1], edgeList[i][0], edgeList[j][1]))) == 11:
                #    t = 'h'
                return True, (edgeList[i][1], edgeList[i][0], edgeList[j][1])
            if edgeList[i][1] == edgeList[j][1] and G[edgeList[i][0]][edgeList[j][0]] == 1:
                #print edgeList[i][1], edgeList[i][0], edgeList[j][0]
                #if len(getEdgesFromKite(G, (edgeList[i][1], edgeList[i][0], edgeList[j][0]))) == 11:
                #    t = 'h'
                return True, (edgeList[i][1], edgeList[i][0], edgeList[j][0])
    
    return False, edgeList


# Get the list of missing edges that could form 4-cliques, and see if any of them pair for an add edge rule.
# (returns true if there is a five wheel or double kite subgraph, kite edge list otherwise)
def isLeaf(G):
    r = leafCheckBase(G)
    if r[0]:
        return True, getEdgesFromKite(G, r[1])
    else:
        return r

# Get the list of missing edges that could form 4-cliques, and see if any of them pair for an add edge rule.
# (returns true if there is a five wheel or double kite subgraph, kite edge list otherwise)
def isLeafAlt(G):
    r = leafCheckBase(G)
    if r[0]:
        return r
    else:
        return False, False


def hasClique(G):
    for i in xrange(len(G)-3):
        for j in xrange(i+1,len(G)-2):
            if G[i][j] == 1:
                for k in xrange(j+1,len(G)-1):
                    if G[i][k]==1 and G[j][k]==1:
                        # We have a triangle.
                        for l in xrange(k+1, len(G)):
                            if G[l][i]==1 and G[l][j]==1 and G[l][k]==1:
                                #return [i, j, k, l]
                                return getEdgesFromClique(G,[i, j, k, l])

    return False

global cliqueCache
cliqueCache = {}

def kCliqueRec(G,k,s):
    #print "Enterting:", k, s
    if (k, s) in cliqueCache:
        #print "cache:", cliqueCache[(k,s)]
        return cliqueCache[(k,s)]

    if k == 0:
        return s

    for i in xrange(len(G)):
        if i not in s:
            con = True
            for v in s:
                if not G[i][v]:
                    con = False
                    break
            if con:
                r = kCliqueRec(G,k-1,s.union([i]))
                if r:
                    cliqueCache[(k,s)] = r
                    #print "Returing", r, "on hit on ", i
                    return r

    cliqueCache[(k,s)] = False
    #print "Returing False"
    return False

def hasKclique(G,k):
    global cliqueCache
    cliqueCache = {}
    r = kCliqueRec(G,k,frozenset())
    if r:
        r = getEdgesFromKClique(r)
    return r

def hasKcliqueOnEdge(G,k,e):
    global cliqueCache
    cliqueCache = {}
    r = kCliqueRec(G,k-2,frozenset(e))
    if r:
        r = getEdgesFromKClique(r)
    return r


def hasCliqueOnEdge(G,e):
    for k in xrange(len(G)-1):
        if k in e:
            continue
        if G[e[0]][k]==1 and G[e[1]][k]==1:
            # We have a triangle.
            for l in xrange(k+1, len(G)):
                if l in e:
                    continue
                if G[l][e[0]]==1 and G[l][e[1]]==1 and G[l][k]==1:
                    #return [e[0], e[1], k, l]
                    return getEdgesFromClique(G,[e[0],e[1], k, l])

    return False

def getKiteEdgesOnEdge(G, e):
    L = set()
    for k in xrange(len(G)):
        if G[e[0]][k]==1 and G[e[1]][k]==1:
            for l in xrange(len(G)):
                if l != k and G[l][e[0]]==1 and G[l][e[1]]==1:
                    L.add(sortPair((l, k)))

                if l != e[1] and G[l][e[0]] == 1 and G[l][k] == 1:
                    L.add(sortPair((l, e[1])))

                if l != e[0] and G[l][k]==1 and G[l][e[1]]==1:
                    L.add(sortPair((l, e[0])))

    return L

# I don't know what this is
def getKiteEdgesEx(G, e):
    L = []
    for i in range(len(G)-2):
        if i in e:
            continue
        for j in range(i+1,len(G)-1):
            if j in e:
                continue
            if G[i][j] == 1:
                for k in range(j+1,len(G)):
                    if k in e:
                        continue
                    #if v:
                    #    print i,j,k
                    if G[i][k]==1 and G[j][k]==1:
                        #if v:
                        #    print i, j, k, "found"
                        # We have a triangle.
                        #for l in range(k+1, len(G)):
                        for l in range(len(G)):
                            if l in e:
                                continue
                            if G[l][i]==1 and G[l][j]==1:
                                L.append((l, k))
                            if G[l][i]==1 and G[l][k]==1:
                                L.append((l, j))
                            if G[l][k]==1 and G[l][j]==1:
                                L.append((l, i))

    return L

# returns true if double kite, kite edge list otherwise.
def isLeafOnEdge(G, e, edgeList):

    newEdges = getKiteEdgesOnEdge(G,e)
    #if not newEdges:
    #    return edgeList

    #edgeList = getKiteEdgesEx(G,e)
    #print newEdges
    #print edgeList

    fullList = newEdges.union(edgeList)

    for e1 in newEdges:
        for e2 in fullList:
            if e1 == e2:
                continue
            if e1[0] == e2[0] and G[e1[1]][e2[1]]:
                return True, getEdgesFromKite(G, (e1[0], e1[1], e2[1]))
            elif e1[0] == e2[1] and G[e1[1]][e2[0]]:
                return True, getEdgesFromKite(G, (e1[0], e1[1], e2[0]))
            elif e1[1] == e2[0] and G[e1[0]][e2[1]]:
                return True, getEdgesFromKite(G, (e1[1], e1[0], e2[1]))
            elif e1[1] == e2[1] and G[e1[0]][e2[0]]:
                return True, getEdgesFromKite(G, (e1[1], e1[0], e2[0]))

    # check if this edge is the base of a double kite.
    # this might be wrong
    for e1 in fullList:
        if e[0] in e1:
            for e2 in fullList:
                if e1 == e2:
                    continue
                if e[1] in e2:
                    if e2[0] in e1 or e2[1] in e1:
                        if e1[0] == e2[0] or e1[0] == e2[1]:
                            v = e1[0]
                        elif e1[1] == e2[0] or e1[1] == e2[1]:
                            v = e1[1]
                        return True, getEdgesFromKite(G, (v, e[0], e[1]))
                
    return False, fullList


# returns true if double kite, kite edge list otherwise.
def isLeafOnEdgeAlt(G, e, edgeList):

    newEdges = getKiteEdgesOnEdge(G,e)
    #if not newEdges:
    #    return edgeList

    #edgeList = getKiteEdgesEx(G,e)
    #print newEdges
    #print edgeList

    fullList = newEdges.union(edgeList)

    for e1 in newEdges:
        for e2 in fullList:
            if e1 == e2:
                continue
            if e1[0] == e2[0] and G[e1[1]][e2[1]]:
                return True, (e1[0], e1[1], e2[1])
            elif e1[0] == e2[1] and G[e1[1]][e2[0]]:
                return True, (e1[0], e1[1], e2[0])
            elif e1[1] == e2[0] and G[e1[0]][e2[1]]:
                return True, (e1[1], e1[0], e2[1])
            elif e1[1] == e2[1] and G[e1[0]][e2[0]]:
                return True, (e1[1], e1[0], e2[0])

    # check if this edge is the base of a double kite.
    # this might be wrong
    for e1 in fullList:
        if e[0] in e1:
            for e2 in fullList:
                if e1 == e2:
                    continue
                if e[1] in e2:
                    if e2[0] in e1 or e2[1] in e1:
                        if e1[0] == e2[0] or e1[0] == e2[1]:
                            v = e1[0]
                        elif e1[1] == e2[0] or e1[1] == e2[1]:
                            v = e1[1]
                        return True, (v, e[0], e[1])
                
    return False, fullList


# returns true if double kite, false otherwise

# performance seems to be unimpressive
def hasDoubleKiteOnEdge(G,e):
    for i in xrange(len(G)):
        if i in e:
            continue
        if G[i][e[0]] and G[i][e[1]]:
            # Triangle.
            #print "Triangle", e[0], e[1], i
            for j in xrange(len(G)):
                if j in e or j == i:
                    continue
                v = None
                #print "j:", j, e, i
                if G[j][e[0]] and G[j][e[1]]:
                    v = i
                elif G[j][e[0]] and G[j][i]:
                    v = e[1]
                elif G[j][e[1]] and G[j][i]:
                    v = e[0]
                #print v
                if v != None:
                    # Single Kite!
                    #print "Single Kite", e[0], e[1], i, j, v
                    for x in (v,j):
                        #print "x =", x
                        for k in xrange(len(G)):
                            #print "k:", k
                            if k in (v,j):
                                continue
                            if G[x][k]:
                                #print "Bonus edge on", k
                                for l in xrange(len(G)):
                                    if l in (e[0],e[1],i,j,k):
                                        continue
                                    #print "l:", l
                                    if G[k][l] and G[x][l]:
                                        # annother triangle!
                                        #print "Annother Triangle"
                                        #print e[0], e[1], i, j, k, l
                                        for m in xrange(len(G)):
                                            if m in (e[0],e[1],i,j,k,l):
                                                continue
                                            if (G[m][j] or G[m][v]) and G[m][k] and G[m][l]:
                                                return True

    #print e
    # Not part of a triangle.  Is the new edge the connecting edge in any pair of double kites?
    for i in xrange(len(G)-1):
        if i in e:
            continue
        if G[e[0]][i]:
            for j in xrange(i+1,len(G)):
                if j in e:
                    continue
                if G[e[0]][j] and G[e[0]][i] and G[i][j]:
                    # Triangle!
                    #print "Triangle:", e[0], i, j
                    for k in xrange(len(G)):
                        if k in e + (i,j):
                            continue
                        if G[i][k] and G[j][k]:
                            # Sinlge kite!
                            # k is the top of our kite.
                            #print "Kite:", k
                            for l in xrange(len(G)):
                                if l in e + (i,j,k):
                                    continue
                                if G[l][k] and G[l][e[1]]:
                                    # bridge between end of edge and top of kite
                                    #print "Bridge:", l
                                    for m in xrange(len(G)):
                                        if m in e + (i,j,k,l):
                                            continue
                                        if G[m][l] and G[m][k] and G[m][e[1]]:
                                            #print "Double:", m
                                            return True




    return False

                    
