import re
import subprocess
import config

p = re.compile('\[ *(.+)\]',re.DOTALL)

p2 = re.compile('[(\s+\d+)]+\n',re.DOTALL)

class iso():
    def __init__(self):
        self.child = subprocess.Popen(config.dreadnaut, -1, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def getGraphHash(self,G):
        child = self.child

        child.stdin.write('n=%i'%(len(G),)+ "\n")
        #print 'n=%i'%(len(G),)+ "\n",
        child.stdin.write("g\n")
        #print "g\n",
        for i in range(len(G)):
            s = ''
            #for j in range(i+1,len(G)):
            for j in range(len(G)):
                if G[i][j]:
                    s += ' ' + str(j)
            s+= ';'
            #print s+"\n",
            child.stdin.write(s+"\n")
            #print s+"\n",
        #print "f=[%i:%i]\n" % (len(G)-2, len(G)-1),
        child.stdin.write("c\n") # Set option getcanon to TRUE
        #print "c\n",
        child.stdin.write("x\n") # Execute nauty.
        #print "x\n",
        child.stdin.write("z\n") # Type two 8-digit hex numbers whose value depends only on h.
        #print "z\n",
        child.stdin.write("F\n") # Flush output
        #child.stdin.write("q\n")
        child.stdin.flush()
        r = []
        n = child.stdout.readline()
        while n != '\n':
            #print n
            r.append(n)
            n = child.stdout.readline()
            #print n,

        r = p.findall(r[-1])[0]

        #print r
        return r

    def setGraph(self,G):
        child = self.child

        #print 'n=%i'%(len(G),)+ "\n"
        child.stdin.write('n=%i'%(len(G),)+ "\n")
        child.stdin.write("g\n")
        for i in range(len(G)):
            s = ''
            #for j in range(i+1,len(G)):
            for j in range(len(G)):
                if G[i][j]:
                    s += ' ' + str(j)
            s+= ';'
            #print s+"\n",
            child.stdin.write(s+"\n")
        #print "f=[%i:%i]\n" % (len(G)-2, len(G)-1),
        child.stdin.write("c\n")
        child.stdin.flush()

    def addEdge(self,e):
        child = self.child

        child.stdin.write("e\n")
        child.stdin.write(str(e[0]) + ":" + str(e[1]) + "\n")
        child.stdin.write(".\n")
        child.stdin.flush()

    def delEdge(self,e):
        child = self.child

        child.stdin.write("e\n")
        child.stdin.write(str(e[0]) + ":-" + str(e[1]) + "\n")
        child.stdin.write(".\n")
        child.stdin.flush()


    def getHash(self):
        child = self.child

        child.stdin.write("x\n") # Execute nauty.
        child.stdin.write("z\n") # Type two 8-digit hex numbers whose value depends only on h.
        child.stdin.write("F\n") # Flush output
        #child.stdin.write("q\n")
        child.stdin.flush()
        r = []
        n = child.stdout.readline()
        while n != '\n':
            #print n
            r.append(n)
            n = child.stdout.readline()

        r = p.findall(r[-1])[0]

        #print r
        return r

    def getForwardMap(self,bmap):
        fmap = [-1 for i in range(len(bmap))] 

        for i in range(len(bmap)):
            fmap[bmap[i]] = i

        return fmap

    def getCannon(self):
        child = self.child

        child.stdin.write("b\n") # get the label and the canonically labelled graph
        child.stdin.write("F\n") # Flush output
        child.stdin.flush()

        r = []
        n = child.stdout.readline()
        while n != '\n':
            #print n
            r.append(n)
            n = child.stdout.readline()

        r = map(int, p2.findall(''.join(r))[0].split())

        #print r
        #print getForwardMap(r)
        return r, self.getForwardMap(r)
