'''
Contains classes managing questlines
'''

class Questline(object):
    def __init__(self, name, start_node=None, quest_nodes=None):
        self.name = name
        self.curr_node = start_node
        self.quest_nodes = {}
        if quest_nodes==None:
            quest_nodes = []
        for n in quest_nodes:
            self.quest_nodes[n.val] = n

    def addQuestNode(self, val, node):
        if self.curr_node is None:
            self.curr_node = node
        self.quest_nodes[val] = node

    def getQuestDescription(self, val):
        if val not in self.quest_nodes:
            print("[!] Given quest value does not exist")
        else:
            print(self.quest_values[val])

    def progress(self, val):
        if val not in self.curr_node.transitions:
            print("[!] Given quest value not valid transition")
        elif val in self.quest_nodes:
            self.curr_node = self.quest_nodes[val]
        else:
            print("[!] Given quest value does not exist")
    def force(self,val):
        if val in self.quest_nodes:
            self.curr_node = self.quest_nodes[val]
        else:
            print("[!] Given quest value does not exist")

    def currValue(self):
        return self.curr_node.val

    def getCurrDetails(self):
        return self.curr_node.getDetails()

    def getCurrTrans(self):
        return self.curr_node.getTransitionDetails()

    def __repr__(self):
        return self.name+"{"+",".join([str(self.quest_nodes[qn]) for qn in self.quest_nodes])+"}"

class QuestNode(object):
    def __init__(self,val,details="NO DESC",transitions=None):
        '''
        :param val: Quest value of node
        :param transitions: map of valid {value:description}
        '''
        self.val = val
        if transitions==None:
            self.transitions = {}
        else:
            self.transitions = transitions
        self.details = details

    def addTransition(self, val, desc=""):
        if val in self.transitions:
            print("[!] Overwriting transition: {0}:{1}".format(val,self.transitions[val]))
        self.transitions[val] = desc

    def setDescription(self,desc):
        self.details = desc

    def getTransitionDetails(self):
        trans = []
        for k in self.transitions:
            trans.append("{0}: {1}".format(k,self.transitions[k]))
        return trans

    def getDetails(self):
        return self.details

    def __repr__(self):
        if self.details is None:
            return str(self.val)
        else:
            return str(self.val)+":"+self.details