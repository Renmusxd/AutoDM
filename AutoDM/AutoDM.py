import sys
import os.path

from DMParser import *


class WorldRunner:
    START_NODE = "start"

    def __init__(self, world, output,printwidth=60):
        self.world = world
        self.output = output
        self.current_node = world.getNode(WorldRunner.START_NODE)
        self.pw = printwidth

    def run(self):
        self.printFormat("Welcome Travelers")
        self.describeSetting()
        while True:
            self.printFormat("What will you do?")
            response = raw_input(">> ")
            response_t = response.split()
            cmd, args = response_t[0], response_t[1:]
            if cmd=="exit":
                # save
                break
            elif cmd=="help":
                self.printHelp()
            elif cmd=="teleport":
                self.teleport(args[0])
            elif cmd=="describe" or cmd=="surroundings":
                self.describeSetting()
            elif cmd=="move":
                self.move(" ".join(args))
            elif cmd=="set":
                if len(args)>=2:
                    self.setAttrib(" ".join(args[:-1]),args[-1])
                else:
                    self.printFormat("Error: set [key] [value]")
            elif cmd=="quests":
                self.printAttribs()
            elif cmd=="quest":
                if len(args)>0:
                    self.printQuestTransitions(" ".join(args))
                else:
                    self.printFormat("Error: quest [questname]")
            elif cmd=="get":
                if len(args)>0:
                    self.printFormat(self.world.getWorldAttr(" ".join(args)))
                else:
                    self.printFormat("Error: get [key]")
        self.printFormat("Goodbye!")

    def setAttrib(self,key,value):
        try:
            self.printFormat(key+" -> "+value)
            self.world.addQuestState(key,int(value))
        except ValueError:
            self.printFormat("Error: Quest value must be integer")

    def printAttribs(self):
        self.printFormat("Quests:")
        for k in self.world.questlines:
            dets = (self.world.questlines[k].getCurrDetails())
            self.printFormat("- "+k+":")
            self.printFormat(dets," "*4)

    def printQuestTransitions(self,questname):
        if questname in self.world.questlines:
            ql = self.world.questlines[questname]
            self.printFormat("Name:    "+ql.name)
            self.printFormat("Details: ")
            self.printFormat(ql.getCurrDetails()," "*4)
            self.printFormat("Transitions: ")
            trans = ql.getCurrTrans()
            for t in trans:
                self.printFormat("- "+t)
        else:
            self.printFormat("No such quest")

    def describeSetting(self):
        if self.current_node is None:
            self.printFormat("You are in the void, the endless abyss taunts you")
            self.printFormat("\tyour insanity only grows here")
        else:
            print("="*self.pw)
            self.printFormat("You are in "+self.current_node.name)
            self.printFormat(self.current_node.description)
            print("-"*self.pw)
            active_characters = self.current_node.getActiveCharacters(self.world)
            for (c,name,desc) in active_characters:
                self.printFormat("- "+name)
                self.printFormat(desc," "*4)
            print("-"*self.pw)
            self.printFormat("Directions:")
            for k in self.current_node.adjacents:
                self.printFormat("- "+str(k)+":\t"+self.current_node.adjacents[k].name)
            print("="*self.pw)

    def move(self,direction):
        if direction in self.current_node.adjacents:
            self.current_node = self.current_node.adjacents[direction]
            self.describeSetting()
        else:
            self.printFormat("Not a valid direction")

    def teleport(self,nodename):
        self.printFormat("WHOOSH!")
        self.current_node = self.world.getNode(nodename)
        self.describeSetting()

    def printHelp(self):
        self.printFormat("move [dir] : follow a direction to another location")
        self.printFormat("teleport [name] : set location to node")
        self.printFormat("describe : describe settings")
        self.printFormat("quest [name] : give details on a particular questline")
        self.printFormat("quests : list all quests")
        self.printFormat("get [name] : get value of world attribute / questline")
        self.printFormat("set [name] : set value of world attribute / questline")
        self.printFormat("exit : close client")

    def printFormat(self,s,indent=""):
        s_t = s.split()
        new_s = ""
        curr_line = ""
        for s in s_t:
            if len(curr_line + s)>self.pw:
                if len(new_s)>0:
                    new_s += "\n"
                new_s += indent + curr_line
                curr_line = ""
            curr_line += " " + s
        if len(curr_line)>0:
            if len(new_s)>0:
                new_s += "\n"
            new_s += indent + curr_line
        print(new_s)

if __name__ == "__main__":
    if len(sys.argv)!=3:
        print("CLI usage: python AutoDM.py [worldpath] [outputpath]")
    if len(sys.argv)==3:
        filename = sys.argv[-2]
        outputpath = sys.argv[-1]
    elif len(sys.argv)<3:
        if len(sys.argv)==1:
            while True:
                print("Please enter world path:")
                filename = raw_input(">>")
                if os.path.isdir(filename):
                    break
                print("Invalid path")
        else:
            filename = sys.argv[-1]

        while True:
            print("Please enter save path:")
            outputpath = raw_input(">>")
            if os.path.isdir(outputpath):
                break
            if not os.path.exists(outputpath):
                os.mkdir(outputpath)
                break
            print("Invalid path")

    p = WorldParser(filename)
    w = p.parse()
    wr = WorldRunner(w, outputpath)
    wr.run()
