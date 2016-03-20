import os

from AutoTokenizer import FileTokenizer
from DMEval import *
from World import *
from Quests import *
from Characters import *

DEFAULT_QUESTFILE = "/quests.txt"
DEFAULT_QUESTDIR = "/quests"
DEFAULT_CHARFILE = "/characters.txt"
DEFAULT_CHARDIR = "/characters"
DEFAULT_WORLDDIR = "/world"

class DMParseClass:
    t = "UNKNOWN"
    def getType(self):
        return self.t

class DMObject(DMParseClass):
    def __init__(self,label,value):
        self.k = label
        self.v = value
        self.t = "OBJECT"

    def __repr__(self):
        return (str(self.k)+"{"+str(self.v)+"}")
    def __str__(self):
        return self.__repr__()

class DMItem(DMParseClass):
    def __init__(self,item):
        self.v = item
        self.t = "ITEM"
    def __repr__(self):
        return "("+str(self.v)+")"
    def __str__(self):
        return self.__repr__()

class DMAssign(DMParseClass):
    def __init__(self,label,value):
        self.k = label
        self.v = value
        self.t = "ASSIGN"
    def __repr__(self):
        return "("+str(self.k)+"="+str(self.v)+")"
    def __str__(self):
        return self.__repr__()

class WorldParser:
    def __init__(self, filename):
        self.worldpath = filename

        if not os.path.isdir(self.worldpath):
            print("[!] Path is not world directory")

        self.questpath = self.worldpath+DEFAULT_QUESTFILE
        if not os.path.exists(self.questpath):
            if os.path.isdir(self.worldpath+DEFAULT_QUESTDIR):
                self.questpath = self.worldpath+DEFAULT_QUESTDIR
            else:
                print("[!] No quest file found: "+self.questpath)
                print("[!] No quest dir found: "+self.worldpath+DEFAULT_QUESTDIR)

        self.characterpath = self.worldpath+DEFAULT_CHARFILE
        if not os.path.exists(self.characterpath):
            if os.path.isdir(self.worldpath+DEFAULT_CHARDIR):
                self.characterpath = self.worldpath+DEFAULT_CHARDIR
            else:
                print("[!] No character file found: "+self.characterpath)
                print("[!] No character dir found: "+self.worldpath+DEFAULT_CHARDIR)

        self.worldnodepath = self.worldpath+DEFAULT_WORLDDIR
        if not os.path.isdir(self.worldnodepath):
            print("[!] No world nodes found: "+self.worldnodepath)

    def parse(self):
        '''
        Parses directory
        :return: World object containing all relevant data
        '''
        quests = self.parseQuests()
        characters = self.parseCharacters()
        worldnodes = self.parseWorldNodes()

        w = World()

        for node in worldnodes:
            w.addWorldNode(node)
        for node in worldnodes:
            node.linkNodes(w)
        for character in characters:
            character.linkPossibleNodes(w)
        for quest in quests:
            w.addQuestline(quest)
        return w

    def parseQuests(self):
        questobjects = self.parseDMObjectsFromFiles(self.questpath)
        return self.convertDMObjectsToQuests(questobjects)

    def parseCharacters(self):
        characterobjects = self.parseDMObjectsFromFiles(self.characterpath)
        return self.convertDMObjectsToCharacters(characterobjects)

    def parseWorldNodes(self):
        worldobjects = self.parseDMObjectsFromFiles(self.worldnodepath)
        return self.convertDMObjectsToWorldNodes(worldobjects)

    def convertDMObjectsToWorldNodes(self, dmobjects):
        nodes = []
        for dmo in dmobjects:
            name, worldnode = dmo.k, dmo.v
            node = WorldNode(name)
            for obj in worldnode:
                if obj.getType()=="ITEM":
                    node.setDescription(obj.v)
                elif obj.getType()=="OBJECT":
                    if obj.k.upper()=="TRANS":
                        label, transitions = self.convertDMObjectToDict(obj)
                        for k in transitions:
                            node.addDummyNode(k,transitions[k])
                    else:
                        print("[!] Unknown node attribute "+str(obj)+" in node "+name)
                elif obj.getType()=="ASSIGN":
                    print("[!] Unexpected assignment "+str(obj)+" in node "+name)
            nodes.append(node)
        return nodes

    def convertDMObjectsToCharacters(self, dmobjects):
        chars = []
        for dmo in dmobjects:
            name, charobj = dmo.k, dmo.v
            character = WorldCharacter(name)
            for obj in charobj:
                if obj.getType()=="OBJECT":
                    character.addWorldEval(WorldEval(obj))
                elif obj.getType()=="ASSIGN":
                    character.addCharacteristic(obj.k,obj.v)
                else:
                    print("[!] Warning: unknown object: "+str(obj))
            chars.append(character)
        return chars

    def convertDMObjectsToQuests(self, dmobjects):
        '''
        Converts a list of dmobjects to quests
        :param dmobjects: dmobjects with appropraite properties
        :return: list of questlines
        '''
        quests = []
        for dmo in dmobjects:
            # questobj should be a list of nodes
            questname, questobj = dmo.k, dmo.v
            ql = Questline(questname)
            for qo in questobj:
                # Val is qnode value
                # qnodeobj is description and transitions
                val, qnodeobj = qo.k, qo.v
                qn = QuestNode(int(val), qnodeobj[0].v)
                if len(qnodeobj)>1:
                    for trans in qnodeobj[1:]:
                        colonindx = trans.v.find(":")
                        if colonindx>-1:
                            t = int(trans.v[:colonindx])
                            det = trans.v[colonindx+1:]
                            qn.addTransition(t, det)
                        else:
                            qn.addTransition(int(trans.v))
                ql.addQuestNode(int(val), qn)
            quests.append(ql)
        return quests

    def parseDMObjectsFromFiles(self, fileordir):
        '''
        Returns a list of DM objects from a directory of files or single file
        :param fileordir: filepath or directory with files
        :return: list of dmobjects
        '''
        dm_objects = []
        if os.path.isdir(fileordir):
            for (path, dirs, files) in os.walk(fileordir):
                for f in files:
                    tok = FileTokenizer(path+"/"+f)
                    new_quests = self.consumeDMObjects(tok)
                    dm_objects.extend(new_quests)
        else:
            tokenizer = FileTokenizer(fileordir)
            dm_objects = self.consumeDMObjects(tokenizer)
        return dm_objects

    def consumeDMObjects(self,tokenizer):
        '''
        Returns list of DM objects
        :param tokenizer: input tokenizer containing multiple DM Objects
        :return: [DMObjects]
        '''
        quests = []
        while tokenizer.hasNext():
            quest = self.consumeDMObject(tokenizer)
            quests.append(quest)
        return quests

    def consumeDMObject(self, tokenizer, id=None):
        '''
        obj := id { obj_or_item }
        obj_or_item := obj, obj_or_item | item, obj_or_item
        item := TEXT
        '''
        # First thing we see should be a quest id
        if id==None:
            id = tokenizer.consume()
        open = tokenizer.consume()
        if open!="{":
            raise Exception("[!] Expect { opening object but found "+open)
        object_contents = []
        while True:
            val = tokenizer.peek()
            if val=="}":
                # End of object
                tokenizer.consume()
                return DMObject(id, object_contents)
            else:
                text = tokenizer.consume()
                open = tokenizer.peek()
                if open=="{":
                    # Object
                    object_contents.append(self.consumeDMObject(tokenizer, text))
                    comma = tokenizer.consume()
                    if comma != ",":
                        raise Exception("[!] Expected comma between entries")
                elif open=="=":
                    # Set value
                    tokenizer.consume()
                    text_acc = ""
                    n_text = ""
                    while n_text!=",":
                        text_acc += n_text
                        n_text = tokenizer.consume()
                    object_contents.append(DMAssign(text,text_acc))
                else:
                    # Item
                    n_text = ""
                    while n_text!=",":
                        text += n_text
                        n_text = tokenizer.consume()
                    object_contents.append(DMItem(text))

    def convertDMObjectToDict(self,dmobject):
        label = dmobject.k
        new_dict = {}
        entries = dmobject.v
        for e in entries:
            if e.getType()=="ASSIGN":
                new_dict[e.k] = e.v
            else:
                print("[!] Unexpected entry in obj dictionary "+str(e))
        return label, new_dict

def listAllFilesInDir(dirname, maxdepth=10):
    list = []
    depth = 0
    for (dirpath, dirnames, filenames) in os.walk(dirname):
        list += [dirpath + f for f in filenames]
        depth += 1
        if depth>maxdepth:
            print("[!] Max depth reached "+dirpath)
            break
    return list