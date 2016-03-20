from AutoTokenizer import TextTokenizer

MAX_ITERS = 1000


# noinspection PyPep8Naming
class WorldEval(object):
    def __init__(self, dmobject):
        '''
        Contains a condition and a series of operations
        :param condition: function: WorldDict -> boolean
        '''
        self.condstr, objs = dmobject.k, dmobject.v
        self.condition = makeConditionFromString(self.condstr)
        self.nodenames = set()
        self.items = []
        for obj in objs:
            if obj.getType()=="OBJECT":
                we = WorldEval(obj)
                self.addRunWorldEval(we)
                self.nodenames.update(we.getNodes())
            elif obj.getType()=="ASSIGN":
                self.addSetAttribute(obj.k,obj.v)
                if obj.k.upper()=="NODE":
                    self.nodenames.add(obj.v)
            elif obj.getType()=="ITEM":
                if obj.k.upper()=="RERUN":
                    self.addReRun()
                else:
                    print("[!] Unrecognized string: "+obj)
            else:
                print("[!] Warning: unknown object: "+str(obj))

    def addSetAttribute(self,name,value):
        '''
        Adds setAttribute line
        :param name: name of attribute to be set
        :param value: function that takes in a WorldDict, outputs anything
        '''
        self.items.append((0,(name,value)))

    def addRunWorldEval(self, worldeval):
        self.items.append((1,worldeval))

    def addReRun(self):
        self.items.append((2,None))

    def evaluate(self,worldstats):
        if not self.condition(worldstats):
            return
        for (itemtype, item) in self.items:
            if itemtype==0:
                name, value = item
                worldstats[name] = value
            elif itemtype==1:
                item.evaluate(worldstats)
            elif itemtype==2:
                raise RerunException("Rerun called")

    def getNodes(self):
        return list(self.nodenames)

    def __repr__(self):
        return str(self)

    def __str__(self):
        itemstr = []
        for item in self.items:
            if type(item)==tuple:
                itemstr.append(item[1][0]+":"+item[1][1])
            else:
                itemstr.append(str(item))
        return "<"+self.condstr+">:{"+",".join(itemstr)+"}"


# noinspection PyPep8Naming
class WorldDict(object):
    def __init__(self, world, vals=None):
        self.world = world
        if vals is None:
            self.vals = {}
        else:
            self.vals = vals.copy()

    def __getitem__(self, item):
        if item in self.vals: return self.vals[item]
        attr = self.world.getWorldAttr(item)
        if attr is not None: return attr
        raise Exception("[!] Could not find "+item+" in world or local dictionaries")

    def __setitem__(self, key, value):
        self.vals[key] = value

class BinaryOp(object):
    INT_INT = ["+","-","*","/"]
    INT_BOOL = ["<",">","<=",">="]
    BOOL_BOOL = ["and","or","xor","xnor"]

    def __init__(self, left, right, op):
        self.left = left
        self.lprim = (type(left)==int) or (type(left)==bool)
        self.ldict = (type(left)==str)
        self.right = right
        self.rprim = (type(right)==int) or (type(right)==bool)
        self.rdict = (type(right)==str)
        self.op = op

    def eval(self, worldstate):
        if self.op in BinaryOp.INT_INT or self.op in BinaryOp.INT_BOOL:
            if self.lprim:
                l = self.left
            elif self.ldict:
                l = worldstate[self.left]
            else:
                l = self.left.eval(worldstate)
            if self.rprim:
                r = self.right
            elif self.rdict:
                r = worldstate[self.right]
            else:
                r = self.right.eval()
            if self.op=="+": return l+r
            if self.op=="-": return l-r
            if self.op=="*": return l*r
            if self.op=="/": return l/r
            if self.op=="<": return l<r
            if self.op==">": return l>r
            if self.op=="<=": return l<=r
            if self.op==">=": return l>=r
        elif self.op in BinaryOp.BOOL_BOOL:
            if self.lprim:
                l = self.left
            else:
                l = self.left.eval(worldstate)
            if self.rprim:
                r = self.right
            else:
                r = self.right.eval(worldstate)
            if self.op=="and": return l and r
            if self.op=="or": return l or r
            if self.op=="xor": return l != r
            if self.op=="xnor": return l == r
        else:
            raise Exception("[!] Unknown operator "+self.op)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "("+str(self.left)+") "+self.op+" ("+str(self.right)+")"


# noinspection PyPep8Naming
class RerunException(Exception):
    def __init__(self,msg):
        Exception.__init__(msg)


# noinspection PyPep8Naming
def makeConditionFromString(s):
    '''
    Makes a lambda expression from a string
    :param s: string describing condtional expression
    :return: (WorldDict -> boolean)
    '''
    tok = TextTokenizer(s)
    cond = makeBinaryOpFromTokenizer(tok)
    return lambda ws: cond.eval(ws)


# noinspection PyPep8Naming
def makeBinaryOpFromTokenizer(tok):
    ll = tok.consume()
    if ll == "(":
        left = makeBinaryOpFromTokenizer(tok)
        lr = tok.consume()
        if lr != ")":
            raise Exception("[!] Expected closing parenthesis for left operation")
    else:
        try:
            left = int(ll)
        except ValueError:
            left = ll

    op = tok.peek()
    if op == ")":
        return left
    else:
        if op == ">" or op == "<":
            op = tok.consume()
            nxtop = tok.peek()
            if nxtop == "=":
                op += tok.consume()
        else:
            op = tok.consume()

    rl = tok.consume()
    if rl == "(":
        right = makeBinaryOpFromTokenizer(tok)
        rr = tok.consume()
        if rr != ")":
            raise Exception("[!] Expected closing parenthesis for right operation")
    else:
        try:
            right = int(rl)
        except ValueError:
            right = rl
    return BinaryOp(left, right, op)
