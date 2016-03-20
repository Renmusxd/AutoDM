'''
Contains all classes managing characters
'''
from DMEval import *


# noinspection PyPep8Naming
class WorldCharacter(object):
    def __init__(self,name):
        self.characteristics = {"NAME": name}
        self.worldevals = []
        # List of all nodes this character may appear in
        self.nodes = []
        self.alive = True

    def addCharacteristic(self, name, value):
        if name.upper()=="NODE" and value not in self.nodes:
            self.nodes.append(value)
        self.characteristics[name] = value

    def addWorldEval(self, worldeval):
        self.worldevals.append(worldeval)
        for n in worldeval.getNodes():
            if n not in self.nodes:
                self.nodes.append(n)

    def linkPossibleNodes(self, world):
        for n in self.nodes:
            node = world.getNode(n)
            if node:
                node.addCharacter(self)
            else:
                print("[!] Could not find node "+n)

    def getEvalDict(self, world):
        wd = WorldDict(world, self.characteristics)
        running = True
        iters = 0
        while running and iters<MAX_ITERS:
            running = False
            iters += 1
            try:
                for we in self.worldevals:
                    we.evaluate(wd)
            except RerunException as e:
                running = True
        if iters>=MAX_ITERS:
            print("[!] Character iteration limit reached.")
        return wd.vals

    def kill(self):
        self.alive = False

    def isInNode(self,nodename,world):
        if self.alive:
            eval_dict = self.getEvalDict(world)
            if eval_dict["NODE"]==nodename:
                return True
        return False

    def __getitem__(self, item):
        return self.characteristics[item]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "CHAR("+\
               ",".join([ str(k)+":"+str(self.characteristics[k]) for k in self.characteristics])+\
                "){"+",".join([ str(w) for w in self.worldevals ])+"}"
