
# noinspection PyPep8Naming
class World(object):
    def __init__(self):
        self.questlines = {}
        self.hour = 0
        self.nodes = {}

    def getWorldAttr(self, name):
        if name == "hour":
            return self.getHourOfDay()
        elif name=="day":
            return self.getDay()
        elif name=="weekday":
            return self.getDayOfWeek()
        elif name in self.questlines:
            return self.questlines[name].currValue()
        return None

    def addWorldNode(self,node):
        if node.name in self.nodes:
            print "[!] Overwriting node "+node.name
        self.nodes[node.name] = node

    def addQuestline(self, questline):
        if questline.name in self.questlines:
            print("[!] Overwriting quest "+questline.name)
        self.questlines[questline.name] = questline

    def getNode(self,nodename):
        if nodename not in self.nodes:
            return None
        else:
            return self.nodes[nodename]

    def addHour(self, delta):
        self.hour += delta

    def addQuestState(self, quest, val=0):
        if quest in self.questlines:
            self.questlines[quest].progress(val)
        else:
            print("[!] No quest "+quest)

    def getHourOfDay(self):
        return self.hour%24

    def getDay(self):
        return self.hour/24

    def getDayOfWeek(self):
        return (self.hour/24)%7

# noinspection PyPep8Naming
class WorldNode(object):
    def __init__(self, name, description="NO DESC"):
        '''
        :param name: name of node
        :param description: {"direction":WorldNode}
        '''
        self.name = name
        self.adjacents = {}
        self.possibleCharacters = []
        self.description = description
        self.dummy_nodes = {}

    def setDescription(self, desc):
        self.description = desc

    def addDummyNode(self, direction, nodename):
        '''
        :param direction: i.e. north, in cave, ...
        :param nodename: name of world node
        '''
        if direction in self.dummy_nodes:
            print "[!] Overwriting direction "+direction
        self.dummy_nodes[direction] = nodename

    def linkNodes(self, world):
        '''
        Links nodes added by addDummyNode
        :param world: World in which to look
        '''
        for d in self.dummy_nodes:
            n = self.dummy_nodes[d]
            self.addNode(d,world.getNode(n))

    def addNode(self, direction, node):
        if direction in self.adjacents:
            print "[!] Overwriting direction "+direction
        self.adjacents[direction] = node

    def addCharacter(self, character):
        if character in self.possibleCharacters:
            print "[!] Duplicating character "+character.name
        self.possibleCharacters.append(character)

    def getActiveCharacters(self,world):
        chars = []
        for c in self.possibleCharacters:
            if c.alive:
                eval_dict = c.getEvalDict(world)
                if eval_dict["NODE"]==self.name:
                    chars.append((c,eval_dict["NAME"],eval_dict["DESC"]))
        return chars