
"""

Adjacency martix graph utils.

"""

def countEdges(G):
    c = 0
    for i in range(len(G)-1):
        for j in range(i,len(G)):
            if G[i][j]:
                c += 1    

    return c


def sortPair(t):
    if t[0] > t[1]:
        return (t[0],t[1])
    else:
        return (t[1],t[0])


def loadFromDesc(d):
    G = [[ 0 for i in range(d['n'])] for j in range(d['n'])]
    if 'e' in d:
        for a,b in d['e']:
            G[a-1][b-1] = 1
            G[b-1][a-1] = 1
    else:
        for a,b in d['0e']:
            G[a][b] = 1
            G[b][a] = 1


    return G

def printGraph(G):
    print "\n".join(map(str, G))

def printDOT(G):
    print "graph untitled"
    print "{ splines = \"true\" ;"
    for i in range(len(G)):
        for j in range(i+1, len(G)):
            if G[i][j] == 1:
                print "\t", i, "--", j, ";"
    print "}"

def getOmniScript(G, labels = None):
    out = ""
    out += """\
tell application "OmniGraffle 5"
    activate
    set doc to (make new document)
    set page breaks visible of doc to false
    
    tell canvas of front window\n"""

    for i in range(len(G)):
        if labels:
            l = labels[i]
        else:
            l = i
        out += "\t\tset n%i to make new shape at end of graphics with properties {textPosition:{0.1, 0.15}, size:{32.0, 32.0}, name:\"Circle\", vertical padding:0, textSize:{0.8, 0.7}, text:{text:\"%i\", alignment:center}}\n" % (i, l)

    for i in range(0,len(G)):
        for j in range(i+1, len(G)):
            if G[i][j] == 1:
                out += "\t\tset l%it%i to make new line at end of graphics\n" % (i,j)
                out += "\t\t\tset source of l%it%i to n%i\n" % (i,j,i)
                out += "\t\t\tset destination of l%it%i to n%i\n" % (i,j,j)

    out += "\tend tell\n"
    out += """\
    set automatic layout of layout info of canvas of front window to true
    tell canvas of front window to layout

    set adjusts pages of canvas of front window to true

    set type of layout info of canvas of front window to force directed
    tell canvas of front window to layout

    set zoomed of front window to false
    set zoomed of front window to true
   
    set automatic layout of layout info of canvas of front window to false
"""
    out += "end tell\n"

    return out

def addOmniLine(a, b):
    out += """\
tell application "OmniGraffle 5"
    activate
    tell canvas of front window\n"""
   
    out += "make new line at end of graphics with properties {point list: {{%i, %i}, {%i, %i}}}\n" % (a[0], a[1], b[0], b[1])

    out += """
    end tell
end tell\n"""

    runOmniScript(out) 


def getLabelPos(layout, vOffset=100):
    xMin = min(layout.values(), key=lambda p: p[0])[0]
    yMin = min(layout.values(), key=lambda p: p[1])[1]
    xMax = max(layout.values(), key=lambda p: p[0])[0]
    yMax = max(layout.values(), key=lambda p: p[1])[1]

    width = xMax - xMin
    height = yMax - yMin

    x = xMin + width/2
    y = yMax + vOffset

    return x, y


def getOmniScriptCore(G, labels = None, layout = None, boldEdges=[], arrowEdges=[], groupOffset=0, parentTarget=None, text=None, lineLayout={}):
    out = ""

    group = []
    for i in range(len(G)):
        if labels:
            l = labels[i]
        else:
            l = i
        if layout:
            origin = layout[str(l)]
        else:
            origin = [100+i*40,100]
        out += "\t\tset G%in%i to make new shape at end of graphics with properties {textPosition:{0.1, 0.15}, size:{32.0, 32.0}, name:\"Circle\", vertical padding:0, textSize:{0.8, 0.7}, text:{text:\"%s\", alignment:center}, origin:{%d, %d}}\n" % (groupOffset, i, l, origin[0], origin[1])
        #out += "\t\tset G%in%i to make new shape at end of graphics with properties {textPosition:{0.1, 0.16}, size:{15.0, 15.0}, name:\"Circle\", vertical padding:0, textSize:{0.8, 0.7}, text:{text:\"%s\", alignment: center, size: 11}, draws shadow: false, origin:{%d, %d}}\n" % (groupOffset, i, l, origin[0], origin[1])
        group.append("G" + str(groupOffset) + "n"+str(i))

    for i in range(0,len(G)):
        for j in range(i+1, len(G)):
            if G[i][j] == 1:
                #if i in invMap and j in invMap and sortPair((invMap[i], invMap[j])) in boldEdges:
                lineName = "G%il%it%i" % (groupOffset, i, j)
                if sortPair((labels[i], labels[j])) in boldEdges:
                    out += "\t\tset %s to connect G%in%i to G%in%i with properties {thickness:2}\n" % (lineName, groupOffset,  i,groupOffset,  j)
                elif (labels[i], labels[j]) in arrowEdges:
                    out += "\t\tset %s to connect G%in%i to G%in%i with properties {head type:\"FilledArrow\", stroke pattern:1}\n" % (lineName, groupOffset,  i,groupOffset,  j)
                elif (labels[j], labels[i]) in arrowEdges:
                    out += "\t\tset %s to connect G%in%i to G%in%i with properties {head type:\"FilledArrow\", stroke pattern:1}\n" % (lineName, groupOffset,  j,groupOffset,  i)
                else:
                    out += "\t\tset %s to connect G%in%i to G%in%i\n" % (lineName, groupOffset,  i,groupOffset,  j)

                if lineLayout and (labels[i], labels[j]) in lineLayout:
                    midPoints = lineLayout[(labels[i], labels[j])]
                    
                    out += "\t\tset oldPoints to point list of %s\n" % (lineName,)
                    out += "\t\tset newPoints to {}\n"
                    out += "\t\tcopy item 1 of oldPoints to end of newPoints\n"
                    for p in midPoints:
                        out += "\t\tcopy {%d, %d} to end of newPoints\n" % (p[0], p[1])
                    out += "\t\tcopy item 2 of oldPoints to end of newPoints\n"
                    out += "\t\tset point list of %s to newPoints\n" % (lineName,)


                group.append("G" + str(groupOffset) + "l" + str(i) + "t" + str(j))
                #out += "tell (make new line) to set {source, destination} to {n%i, n%i}\n" % (i, j)
                """
                out += "\t\tset l%it%i to make new line at end of graphics\n" % (i,j)
                out += "\t\t\tset source of l%it%i to n%i\n" % (i,j,i)
                out += "\t\t\tset destination of l%it%i to n%i\n" % (i,j,j)
                """

    if text:
        out += "\t\tset G%iT to make new shape at end of graphics with properties {fill:no fill, draws shadow:false, autosizing:full, origin:{%i, %i}, text:{size: 14, text:\"%s\"}, draws stroke:false}\n" % (groupOffset, text[1][0], text[1][1], text[0])
        group.append("G" + str(groupOffset) + "T")

    if layout:
        out += "\t\tset G" + str(groupOffset) + " to assemble { " + ", ".join(group) + " }\n"
        if parentTarget is not None:
            out += "\t\tconnect G%i to G%i with properties {head type:\"FilledArrow\", thickness:2, head scale:2}\n" % (groupOffset, parentTarget)

    return out


def wrapOmniScript(s, tree=True):
    out = """\
tell application "OmniGraffle 5"
    activate

    set doc to (make new document)
    set page breaks visible of doc to false

    set adjusts pages of canvas of front window to true
    
    tell canvas of front window\n"""

    out += s

    out += "\tend tell\n"

    out += """\
    set automatic layout of layout info of canvas of front window to true
    tell canvas of front window to layout

    set adjusts pages of canvas of front window to true
"""
    if tree:
            out += """\
    set type of layout info of canvas of front window to hierarchical
    set direction of layout info of canvas of front window to bottom to top
"""
    else:
            out += """\
    set type of layout info of canvas of front window to force directed
"""
    out += """\
    tell canvas of front window to layout
    set zoomed of front window to false
    set zoomed of front window to true
       
    set automatic layout of layout info of canvas of front window to false

    # Nuke line midpoints:
    repeat with L in lines of canvas of front window
        set pl to point list of L
        set point list of L to {item 1 of pl, item (count of pl) of pl}
    end repeat

    """

    out += "end tell\n"

    return out


def getOmniScriptAlt(G, labels = None, layout = None, newDoc=True, tree=False, boldEdges=[], arrowEdges=[], groupOffset=0, parentTarget=None, text=None, lineLayout={}):
    if not labels:
        labels = range(len(G))

    invMap = {}
    for i in range(len(labels)):
        invMap[labels[i]] = i
        

    out = ""
    out += """\
tell application "OmniGraffle 5"
    activate"""

    if newDoc:
        out += """\

    set doc to (make new document)
    set page breaks visible of doc to false

    # Turn off the outline, needs Assistive access though :-/
    #tell application "System Events"
    #    click menu item "Outline" of ((process OmniGraffle 5)'s (menu bar 1)'s 
    #            (menu bar item "View")'s (menu "View"))
    #end tell

    """

    out += """\

    set adjusts pages of canvas of front window to true
    
    tell canvas of front window\n"""

    out += getOmniScriptCore(G, labels, layout, boldEdges, arrowEdges, groupOffset, parentTarget, text, lineLayout)

    out += "\tend tell\n"
    if not layout:
        out += """\
    set automatic layout of layout info of canvas of front window to true
    tell canvas of front window to layout

    set adjusts pages of canvas of front window to true
"""
        if tree:
            out += """\
    set type of layout info of canvas of front window to hierarchical
"""
        else:
            out += """\
    set type of layout info of canvas of front window to force directed
"""
        out += """\
    tell canvas of front window to layout
"""

        out += """\
    set zoomed of front window to false
    set zoomed of front window to true
       
    set automatic layout of layout info of canvas of front window to false
        """

    out += "end tell\n"

    #print out

    return out


def printOmniScript(G,labels=None,layout=None, tree=False):
    print getOmniScriptAlt(G,labels,layout, tree)


def runOmniScript(script):
    import subprocess

    proc = subprocess.Popen('osascript', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
   
    proc.communicate(script)

    proc.wait()


def displayGraph(G,labels=None,layout=None, newDoc=True, tree=False, boldEdges=[], arrowEdges=[], groupOffset=0, parentTarget=None):

    """ 
    Requires OmniGraffle on OS X. 
    """

    runOmniScript(getOmniScriptAlt(G,labels,layout,newDoc,tree,boldEdges,arrowEdges,groupOffset, parentTarget))


def getGraphLayoutWtihLines(graphFile):
    script = """\
tell application "OmniGraffle 5"
    activate
    set nodes to {}
    set edges to {}
    set doc to (open """+ '"' + graphFile + '"' + """)
    set c to first canvas of doc
    repeat with S in shapes of c
        set pair to {}
        if name of S is "Circle" then
            copy (get text of S) to end of pair
            copy (get origin of S) to end of pair
            copy pair to end of nodes
        end if
    end repeat
    repeat with L in lines of c
        set LD to {}
        copy text of source of L to end of LD
        copy text of destination of L to end of LD
        copy point list of L to end of LD
        copy LD to end of edges
    end repeat
    return {nodes, edges}
end tell
"""
    import subprocess

    proc = subprocess.Popen(['osascript', '-s', 's'],  stdin=subprocess.PIPE, stdout=subprocess.PIPE)
   
    #proc.communicate(script)
    proc.stdin.write(script)
    proc.stdin.close()

    layoutData = proc.stdout.read()
    proc.kill()

    layoutData = layoutData.replace('{', '[')
    layoutData = layoutData.replace('}', ']')
   
    import json 
    layoutObj = json.loads(layoutData)
  
    layoutMap = {}
    for v in layoutObj[0]:
        layoutMap[v[0]] = v[1]         

    lineMap = {}
    for l in layoutObj[1]:
        points = l[2][1:-1]
        if points:
            l[0] = int(l[0])
            l[1] = int(l[1])
            lineMap[(l[0],l[1])] = points
            lineMap[(l[1],l[0])] = list(reversed(points))

    return layoutMap, lineMap


def getGraphLayout(graphFile):
    """ 
    Requires OmniGraffle on OS X. 
    """
    script = """\

tell application "OmniGraffle 5"
    activate
    set output to {}
    set doc to (open """+ '"' + graphFile + '"' + """)
    set c to first canvas of doc
    repeat with i from 1 to count of shapes of c
        set pair to {}
        if name of shape i of c is "Circle" then
            copy (get text of shape i of c) to end of pair
            copy (get origin of shape i of c) to end of pair
            copy pair to end of output
        end if
    end repeat
    return output
end tell
"""

    import subprocess

    proc = subprocess.Popen(['osascript', '-s', 's'],  stdin=subprocess.PIPE, stdout=subprocess.PIPE)
   
    #proc.communicate(script)
    proc.stdin.write(script)
    proc.stdin.close()

    layoutData = proc.stdout.read()
    proc.kill()

    layoutData = layoutData.replace('{', '[')
    layoutData = layoutData.replace('}', ']')
   
    import json 
    layoutList = json.loads(layoutData)
  
    layoutMap = {}
    for v in layoutList:
        layoutMap[v[0]] = v[1]         

    return layoutMap

def getGraphEdges(graphFile):
    """ 
    Requires OmniGraffle on OS X. 
    """
    script = """\
tell application "OmniGraffle 5"
    activate
    set output to {}
    set doc to (open """+ '"' + graphFile + '"' + """)
    set c to first canvas of doc
    repeat with i from 1 to count of lines of c
        set pair to {}
        copy text of source of line i of c to end of pair
        copy text of destination of line i of c to end of pair
        copy pair to end of output
    end repeat
    return output
end tell
"""


    import subprocess

    proc = subprocess.Popen(['osascript', '-s', 's'],  stdin=subprocess.PIPE, stdout=subprocess.PIPE)
   
    #proc.communicate(script)
    proc.stdin.write(script)
    proc.stdin.close()

    layoutData = proc.stdout.read()
    proc.kill()

    layoutData = layoutData.replace('{', '[')
    layoutData = layoutData.replace('}', ']')
   
    import json 
    edgeList = json.loads(layoutData)
  
    #layoutMap = {}
    #for v in layoutList:
    #    layoutMap[v[0]] = v[1]         

    return edgeList


def copyGraph(G):
    G2 = []
    for r in G:
        G2.append(r[:])

    return G2


def newGraph(n):
    return [[0 for i in range(n)] for j in range(n)]


def newClique(k):
    N = newGraph(k)
    for i in range(k-1):
        for j in range(i+1, k):
            N[i][j] = 1
            N[j][i] = 1

    return N

def adjList(G):
    d = {}
    for i in range(len(G)):
        l = []
        for j in range(len(G)):
            if G[i][j]:
                l.append(j)
        d[i] = l[:]

    return d


def isSymetric(G):
    for i in range(len(G)):
        for j in range(len(G)):
            if G[i][j] != G[j][i]:
                return False
    return True

