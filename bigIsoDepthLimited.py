#!/usr/bin/env python

"""

BFS search to find long chains of add-edge operations on graphs that don't branch because of isomorphism.



Continue on if:
    Iso
    One edge is leaf
    One edge is leaf at specified depth

Todo:
    iso hash caching on extraLeafCheck
    unification of main loop and extraLeafCheck
        Need to think about unlimited depth mainline vs limited depth leaf checking
    clean up output?
        Need to think about garunteed smallest constuction of leaf on context

"""

# random thought:
#   Doesn't find isomorphisms, but a node can be expressed as a set of added edges.
#   Could be a useful transposition table alternative.

import graphs
import util

topDepth = 3

bestKnown = -1

#G = graphs.Cyclotomic13
G = util.loadFromDesc(graphs.Grotzsch)
#G = util.loadFromDesc(graphs.Chvatal)
#G = util.loadFromDesc(graphs.Brinkman)
#G = graphs.Gruenbaum
#G = graphs.Qt49
#G = util.loadFromDesc(graphs.Dodec)
#import mycUtil
#G = mycUtil.genMycRing(7)
#import seriesGen
#G = seriesGen.genGraph(4)
#G = util.loadFromDesc(graphs.Toft)
#G = graphs.t1
#G[9][10] = 1
#G[10][9] = 1
#G[14][10] = 1
#G[10][14] = 1
#G[14][16] = 1
#G[16][14] = 1


from util import sortPair
from hajosUtil import *
from iso import iso
isoTool = iso()

global stack
stack = []
freq = 200

from heapq import *


def addEdge(G, e, iso=True):
    #print "addEdge:", e
    #stack.append(e)
    if iso:
        isoTool.addEdge(e)
    G[e[0]][e[1]] = 1
    G[e[1]][e[0]] = 1

def delEdge(G, e, iso=True):
    #print "delEdge:", e
    #stack.pop()
    if iso:
        isoTool.delEdge(e)
    G[e[0]][e[1]] = 0
    G[e[1]][e[0]] = 0


def leafCheck(G, e=False,kiteEdges=False):
    if e:
        c = hasCliqueOnEdge(G,e)
    else:
        c = hasClique(G)
    if c:
        return '4', [], edgesToVerts(c), c
    else:
        if kiteEdges:
            v = isLeafOnEdgeAlt(G,e,kiteEdges)
        else:
            v = isLeafAlt(G)
        if v[0]:
            edgeList = getEdgesFromKite(G, v[1])
            if len(edgeList) == 11:
                t = 'h'
            else:
                t = '5'
            return t, v[1], edgesToVerts(edgeList), edgeList
        #if v[0]:
            #return v[1], v[2]
        else:
            return False, False, False, False

def calcSize(cons, us= frozenset(('4',))):
    # calculate the size of the constrution

    # doesn't find smallest possible construciton if there are multiple 
    # with varying length constructions of a graph

    # returns the size, and the list of unique grahps in the construction

    # possible optimization:
    #   if we have a unterminated branch, i.e. []
    #   and we don't have any L2 graphs in our usedSet
    #   then we know the min construction is 1 greater
    #   than what we are currently returning.


    usedSet = set(us)
    emptyBranch = False
    hasL2 = False

    def calcSizeRec(cons):
        if cons == []:
            emptyBranch = True
            return 1 # minimum construction for an empty branch is 1

        if cons[0]:
            if cons[0] in usedSet or cons[0] == 'm':
                return 0 # this graph has already been seen.  No cost.

            usedSet.add(cons[0])
      
            if cons[0] in ['4', '5', 'h']:
                return 1
            else:
                hasL2 = True

        return 1 + calcSizeRec(cons[2]) + calcSizeRec(cons[3])


    # should return +1 for the 4 clique, but -1 for the completed graph
    #return 1 + calcSizeRec(cons), frozenset(usedSet) 
    if cons == []:
        return 1, frozenset(usedSet)
    #else:
    #    return 1 + calcSizeRec(cons[2]) + calcSizeRec(cons[3]), frozenset(usedSet) 
    else:
        size = 1 + calcSizeRec(cons[2]) + calcSizeRec(cons[3])
        if emptyBranch and not hasL2:
            size += 1
        return size, frozenset(usedSet) 


subIso = iso()
def getCriticalHash(G, t, edges1, edges2):
    vMap = {}
    i = 0
    for v in t:
        vMap[v] = i
        i += 1
        
    for e in edges1.union(edges2):
        for v in e:
            if not vMap.has_key(v):
                vMap[v] = i
                i += 1

    subG = util.newGraph(len(vMap))

    subG[vMap[t[0]]][vMap[t[1]]] = 1
    subG[vMap[t[1]]][vMap[t[0]]] = 1

    for e in edges1.union(edges2):
        if G[e[0]][e[1]]:
            subG[vMap[e[0]]][vMap[e[1]]] = 1
            subG[vMap[e[1]]][vMap[e[0]]] = 1

    # Oh fuck, I wasn't doing this before.  Are my results fucked?
    subG[vMap[t[0]]][vMap[t[2]]] = 0
    subG[vMap[t[2]]][vMap[t[0]]] = 0
    subG[vMap[t[1]]][vMap[t[2]]] = 0
    subG[vMap[t[2]]][vMap[t[1]]] = 0

    #print subG
    #util.printGraph(subG)
    #print t
    #print edges1
    #print edges2
    #nSet = edges1.union(edges2)
    #nSet.add((t[0],t[1]))
    #print nSet
    #print len(nSet)
    #util.displayGraph(subG)    
    return subIso.getGraphHash(subG) 


def getEdgesRec(c):
    if c[0] in ['4', '5', 'h']:
        return c[3]
    else:
        return mergeSubgraphs(c[1], getEdgesRec(c[2]), getEdgesRec(c[3]))

def getCombinedCons(G, t, leaf1, leaf2):
   # return getCriticalHash(G, t, leaf1[3], leaf2[3]), t, leaf1[2].union(leaf2[2]), leaf1[3].union(leaf2[3])
    return getCriticalHash(G, t, getEdgesRec(leaf1), getEdgesRec(leaf2)), t, leaf1, leaf2


global hitCount
hitCount = 0
bigTable = {}
def extraLeafCheck(G, depth, ne = None, nKiteEdges=None):
    global hitCount

    # do a depth limited search for a construction.
    # So we take both edges of a triple, and both of the resulting graphs are leafs

    # depth is how many more times we can recurse before finding a leaf.

    # bigTable is a global cache of graphs and depths, but we can only cache negative results.
    # caching on graph isomorphism here doesn't work.
    # You cache a result.  Then you pull that result from the cache later for a new graph.
    # But the indicies are wrong, so your construction is wrong when you sum the graphs.  
    # To make this work, you would have to map back and forth between
    # the canonical indicies and your working indices.

    #h1 = -1


    # depth is part of the hash because just because a graph isn't a leaf at depth 4, doesn't mean it's not a leaf at depth 3
    h1 = isoTool.getHash()
    if (h1, depth) in bigTable:
    #    print "Cache hit:", h1, bigTable[h1]
        hitCount += 1
        return bigTable[(h1, depth)]

    # test if this graph is a leaf.  I.E. contains a 4-clique, 5-wheel, or h graph
    l = leafCheck(G,ne,nKiteEdges)

    # return if we have a leaf, or we have hit our depth limit.
    if l[0] or depth <= 2:  # leafCheck takes care of depth <= 2
        #bigTable[h1] = [l]  # FIXME I think we can cache the negative result here for depth
        return [l]

    # edgeCache caches a result for when an edge participates in multiple tripples.
    edgeCache = {}
    
    retList = []  # we need to return all possible solutions
    usedSets = [] # a list of sets of graphs used for each of the solutions in retLest

    kiteEdges = getKiteEdges(G) # performance optimization

    for t in getAllTripples(G):
        e1 = sortPair([t[0], t[2]])
        e2 = sortPair([t[1], t[2]])

        #print "elc tripple:", t, e1, e2

        # Basic recursive check on the edges

        if edgeCache.has_key(e1):
            r1 = edgeCache[e1]
        else:
            addEdge(G,e1)
            r1 = extraLeafCheck(G,depth-1,e1,kiteEdges)
            delEdge(G,e1)
            edgeCache[e1] = r1
            

        if edgeCache.has_key(e2):
            r2 = edgeCache[e2]
        else:
            addEdge(G,e2)
            r2 = extraLeafCheck(G,depth-1,e2,kiteEdges)
            delEdge(G,e2)
            edgeCache[e2] = r2
        
        # to make this arbitrary depth:
        # leaf1 and leaf2 become lists
        # is that it?
        # Oh, and we are going to need edges for all returns

        # loop across the results
        for l1 in r1:
            for l2 in r2:
                # Found a pair of results that are good.
                # non-good results are in the ret-list? We don't just return empty?
                if l1[0] and l2[0]:
                    #print "t:", t
                    #print "derp1:", l1
                    #print "derp2:", l2


                    #print G
                    #print "big1:", r1
                    #print "big2:", r2
                    #exit()

                    # get the subgraph generated by the hajos sum of the leaf graphs
                    # r is presumably our standard search node quad.  Whatever that is.
                    # this reduces our found construction to a subgraph construction
                    r = getCombinedCons(G, t, l1, l2)

                    # might be able to optimize the above.  We always call it, so we might 
                    # not need to recurse.  In fact, it's kind of goofy that this gets called recursively.

                    #if r[0] == '1bec   e0328 4f4d838':
                    #    print r
                    #    exit()

                    # Do some optimzation to reduce the size of our results

                    # use calcSize to get the set of graphs used in the construction
                    used = calcSize(r)[1]
                    # calcSize doesn't include the root graph in the set, so add it
                    used = used.union([r[0]])

                    # Check if we have already seen a result that uses a subset of the
                    # graphs that we are using.
                    okay = True
                    for s in usedSets:
                        if s.issubset(used):
                            okay = False
                            break
                    
                    # now the other side of the above.  Go through the list, and kill any previous results that
                    # are supersets of the current result.
                    if okay:
                        #this is going to be hacky.
                        #filter the retList if the new construction is a subset of 
                        # any of the constructions in the retlist.
                        newUsed = []
                        newRet = []
                        for i in xrange(len(retList)):
                            s = usedSets[i]
                            if not used.issubset(s):    
                                newUsed.append(s)
                                newRet.append(retList[i])
                        retList = newRet
                        usedSets = newUsed
                        

                        retList.append(r)
                        usedSets.append(used)

    #print "elc ret:", retList
    if retList:
        return retList  # we have a result, we can return it.
                        # unfortunately, our search node format does not cover returning usedSets as well.
    else:
        bigTable[(h1,depth)] = [(False,)] # only cache on failure
        return [(False,)]
    #return False, False

def getConsList(cons):
    if cons == []:
        return ['[]']

    if cons[0] in ['4', '5', 'h','m']:
        return [cons[0]]

    if cons[0]:
        return [cons[0]]

    return [] + getConsList(cons[2]) + getConsList(cons[3])


def insertBranch(cons,branch):
    #print "cons:", cons
    #print "branch:", branch

    if cons == []:
        return branch

    if cons[0] in ['4', '5', 'h']:
        return cons

    # This might be better, but not sure about correctness
    #if cons[0] != False:
    #    return cons
    
    #if cons[3] != []:
    #    return cons

    #print "rec"
    return [cons[0], cons[1], cons[2], insertBranch(cons[3],branch)]


def isoBFS(G):

    table = {}

    isoTool.setGraph(G)

    todo = [ (0,0,[]) ]

    best = bestKnown
    bestList = []
    hitTotal = 0

    def end(signal=None, func=None):
        print
        print "Considered:", hitTotal
        print best
        print '\n'.join(str(x) for x in bestList)

        print hitCount
        if signal:
            import sys
            sys.exit()

    import signal
    signal.signal(signal.SIGINT, end)

    sortCount = 0
    # Main BFS loop
    while len(todo) > 0:
        hitTotal += 1
        #print todo
        (cost, depth, cons) = heappop(todo)
        #(cost, depth, cons) = todo.pop()
        #print todo
        #print c
        #print triList
        
        #verb = False
        #if getConsList(cons) == ['m', 'm', '1bec f08dccc 707af4d', '[]']:
        #    print "yep"
        #    print cons
        #    print calcSize(cons)
        #    verb = True
        #    #exit()

        #print "cons:", c
        # Add in all of the edges needed for G
        c = cons
        while c!= []:
            ta = c[1]
            addEdge(G, (ta[1],ta[2]))
            c = c[3]

        #th = isoTool.getHash()  # doesn't have a performance impact
        th = 1
        #print "considering:", cons
        currentSize, usedSet = calcSize(cons)
        #if best != -1 and calcSize(cons)[0] > best:
        if best != -1 and currentSize > best:
            # strip off the edges added at this stage of the BFS
            c = cons
            while c!= []:
                ta = c[1]
                delEdge(G, (ta[1],ta[2]))
                c = c[3]
            continue


        edgeCache = {}
        # loop across all of the tripples to check where to continue the search

        for t in getAllTripples(G):
            e1 = sortPair([t[0], t[2]])
            e2 = sortPair([t[1], t[2]])

            #print "tripple:", t, e1, e2

            #print "calling left:"
            if edgeCache.has_key(e1):
                h1, leafList1 = edgeCache[e1]
            else:
                addEdge(G,e1)
                h1 = isoTool.getHash()
                leafList1 = extraLeafCheck(G,topDepth,e1)
                #leaf1, cons1 = leafCheck(G)
                edgeCache[e1] = h1, leafList1
                delEdge(G,e1)
                

            #print "calling right:"
            if edgeCache.has_key(e2):
                h2, leafList2 = edgeCache[e2]
            else:
                addEdge(G,e2)
                h2 = isoTool.getHash()
                #if h1 != h2:
                leafList2 = extraLeafCheck(G,topDepth,e2)
                    #leaf2, cons2 = leafCheck(G)
                edgeCache[e2] = h2, leafList2
                delEdge(G,e2)

            #print "leafList1:", leafList1
            #print "leafList2:", leafList2

            #for leaf1, cons1 in leafList1:
            #    for leaf2, cons2 in leafList2:
            for leafNode1 in leafList1:
                for leafNode2 in leafList2:
                    haveCons = False
                    #if h1 == h2 or (leafNode1[0] and leafNode1[0] == leafNode2[0]):
                    if h1 == h2:
                        leftBranch = ('m', [], [], [])
                        #if leafNode1[0] in ('4', '5', 'h'):
                        if leafNode1[0]:
                            rightBranch = leafNode1
                            haveCons = True
                            h = h1, h2
                            #h = False
                        else:
                            rightBranch = []
                            h = h1
                        # uhm.  Not sure about this.  Seems like a big change:
                        #nt = t[:]
                        nt = t[1], t[0], t[2]
                    elif leafNode1[0] and leafNode2[0]:
                        leftBranch = leafNode1
                        rightBranch = leafNode2
                        nt = t[:]
                        haveCons = True
                        h = sortPair((h1,h2))
                        #h = False
                    elif leafNode1[0]:
                        leftBranch = leafNode1
                        rightBranch = []
                        nt = t[:]
                        h = h2
                    elif leafNode2[0]:
                        leftBranch = leafNode2
                        rightBranch = []
                        nt = t[1], t[0], t[2]
                        h = h1
                    else:
                        continue

                    newCons = insertBranch(cons,[False, nt, leftBranch, rightBranch])
                    #newSize, used = calcSize(newCons)
                    newSize, used = calcSize([False, nt, leftBranch, rightBranch], usedSet)
                    newSize = newSize + currentSize - 1
                    #if newSize2+currentSize-1 != newSize or used != used2:
                    #    print "fail"
                    #    print cons
                    #    print newCons
                    #    print [False, nt, leftBranch, rightBranch]
                    #    print
                    #    print currentSize, usedSet
                    #    print newSize, used
                    #    print newSize2, used2
                    #    exit()
                    score = newSize
                    #score = 1.0/newSize
                    #score = (depth+1)/(newSize**2*1.0)
                    #score = (newSize**2*1.0)/(depth+1)
                    #print newCons
                    #print getConsList(newCons)

                    #print "result:", (h,used,newSize)
                    #print "in table:", (h,used,newSize) in table

                    if (h,used,newSize) not in table:
                        table[(h,used,newSize)] = True

                        print "remaining:", len(todo), "best:", best, "size:", newSize, "score:", score, "cons:", getConsList(newCons)
                        if haveCons: # we have a construction
                            if best == -1 or newSize < best:
                                best = newSize
                                bestList = []
                            if newSize == best:
                                #bestList.append((c, t, code, (leaf1, leaf2), (cons1, cons2),used))
                                bestList.append(newCons)

                        elif best == -1 or newSize <= best:
                            heappush(todo, (score,depth+1,newCons))
                            #todo.append((score,depth+1,newCons))
                            #todo.insert(0, (score,depth+1,newCons))
                

        # strip off the edges added at this stage of the BFS
        c = cons
        while c!= []:
            ta = c[1]
            delEdge(G, (ta[1],ta[2]))
            c = c[3]

        #table[th] = True


    end()


if __name__ == "__main__":

    #util.displayGraph(G);exit()
        
    #import cProfile
    #import pstats
    #cProfile.run("isoBFS(G)", 'fooprof')
    #p = pstats.Stats('fooprof')
    ##p.strip_dirs().sort_stats('cumulative').print_stats(10)
    #p.strip_dirs().sort_stats('time').print_stats(10)
    #exit()

    isoBFS(G)
