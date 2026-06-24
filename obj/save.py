import xml.etree.ElementTree as ET
import os

from obj.items import *
from obj.pawns import *
from obj.player import *
from obj.blueprint import *
from obj.game import *

TARGET_DIRECTORY = "./projects/"

def ntab(x):
    res = ""
    for i in range(x):
        res += "    "
    return res



def toXML(o,indent=0):

    items = Item()
    pawns = NPC()
    pc = PC()
    player = Player()
    blueprint = Blueprint()
    prop = Prop()
    cell = Cell()
    game = Game()
    #TODO Player Instance ?
    res = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    if (o is None):
        res += ntab(indent) + "<Empty></Empty>\n" 
    elif isinstance(o,items.Item):
        res = ntab(indent) + "<Item\n"
        res += ntab(indent+1) + "name=\"" + o.name() + "\"\n" 
        res += ntab(indent+1) + "type=\"" + str(o.type()) + "\"\n"
        res += ntab(indent+1) + "description=\"" + o.description() + "\"\n"
        res += ntab(indent) + "/>\n"
   

    elif isinstance(o,pawns):
        res = ntab(indent) + "<NPC\n"
        res += ntab(indent+1) + "alignement=\"" + str(o.alignement()) + "\"\n" 
        res += ntab(indent+1) + "name=\"" + o.name() + "\"\n"
        
        res += ntab(indent+1) + "description=\"" + o.description() + "\"\n"
        res += ntab(indent) + ">\n"
        res += ntab(indent+1) + "<inventory>\n"
        for i in o.inventory():
            res += toXML(i,indent+2) 
        res += ntab(indent+1) + "</inventory>\n"
        res += ntab(indent+1) + "<stats>\n"
        for s in o.stats():
            res += ntab(indent+2) + "<couple\n"
            res += ntab(indent+3) + "stat=\"" + s + "\"\n"
            res += ntab(indent+3) + "value=\"" + str(o.stats()[s]) + "\"\n"
            res += ntab(indent+2) + "/>\n"
        res += ntab(indent+1) + "</stats>\n"
        res += ntab(indent) + "</NPC>\n"


    elif isinstance(o,pc):
        res = ntab(indent) + "<PC\n"
        res += ntab(indent+1) + "ID=\"" + str(o.player()) + "\"\n" 
        res += ntab(indent+1) + "name=\"" + o.name() + "\"\n"
        res += ntab(indent+1) + "description=\"" + o.description() + "\"\n"
        res += ntab(indent) + ">\n"
        res += ntab(indent+1) + "<inventory>\n"
        for i in o.inventory():
            res += toXML(i,indent+2) 
        res += ntab(indent+1) + "</inventory>\n"
        res += ntab(indent+1) + "<stats>\n"
        for s in o.stats():
            res += ntab(indent+2) + "<couple\n"
            res += ntab(indent+3) + "stat=\"" + s + "\"\n"
            res += ntab(indent+3) + "value=\"" + str(o.stats()[s]) + "\"\n"
            res += ntab(indent+2) + "/>\n"
        res += ntab(indent+1) + "</stats>\n"
        res += ntab(indent) + "</PC>\n"


    elif isinstance(o,player):
        raise Exception("NotHandled?")
        #TODO

    elif isinstance(o,prop):
        res = ntab(indent) + "<Prop\n"
        res += ntab(indent+1) + "name=\"" + o.name() + "\"\n" 
        res += ntab(indent+1) + "type=\"" + str(o.type()) + "\"\n"
        res += ntab(indent+1) + "description=\"" + o.description() + "\"\n"
        res += ntab(indent) + "/>\n"


    elif isinstance(o,cell):
        res = ntab(indent) + "<Cell\n"
        #note: retrieve bin from string with bin(int(x,2)) 
        res += ntab(indent+1) + "ground=\"" + str(o.ground()) + "\"\n"
        res += ntab(indent+1) + "walls=\"" + str(bin(o.walls())) + "\"\n"
        res += ntab(indent+1) + "doors=\"" + str(bin(o.doors())) + "\"\n"
        res += ntab(indent) + ">\n"
        res += ntab(indent+1) + "<contents>\n" 
        for p in o.contents():
            res += toXML(p,indent+2)
        res += ntab(indent+1) + "</contents>\n"
        res += ntab(indent) + "</Cell>\n"


    elif isinstance(o,blueprint):
        res = ntab(indent) + "<Blueprint\n"
        res += ntab(indent+1) + "name=\"" + o.name() + "\"\n"
        res += ntab(indent+1) + "length=\"" + str(o.length()) + "\"\n"
        res += ntab(indent+1) + "width=\"" + str(o.width()) + "\"\n"
        res += ntab(indent) + ">\n"
        res += ntab(indent+1) + "<grid>\n" 
        for i in range(o.length()):
            res += ntab(indent+2) + "<row>\n"
            for j in range (o.width()):
                res += toXML(o.get_cell(i,j),indent+3) #PROBABLY NOT GOOD? 
            res += ntab(indent+2) + "</row>\n"
        res += ntab(indent+1) + "</grid>\n" 
        res += ntab(indent) + "</Blueprint>\n"


    elif isinstance(o,game):
        #BE CAREFUL - WILL CREATE FILES
        res = ntab(indent) + "<Game\n"
        res += ntab(indent +1) + "name=\"" + o.name() + "\"\n"
        res += ntab(indent) + ">\n"

        #All [thing]List attributes are implicit in their directories
        local_path = TARGET_DIRECTORY + o.name() + "/"
        i=1
        for e in o.items():
            try:
                f = open(local_path + "Items/"+"Item#"+str(i)+"-"+e.name()+".xml","x")
            except FileExistsError:
                f = open(local_path + "Items/"+"Item#"+str(i)+"-"+e.name()+".xml","w")
            finally:
                f.write(toXML(e))
                f.close()
            i+=1

        i=1
        for e in o.characters():
            try:
                if(isinstance(e,pawns)):
                    f = open(local_path + "Sheets/PC"+"Sheet#"+str(i)+"-"+e.name()+".xml","x")
                f = open(local_path + "Sheets/"+"Sheet#"+str(i)+"-"+e.name()+".xml","x")
            except FileExistsError:
                if(isinstance(e,pawns)):
                    f = open(local_path + "Sheets/PC"+"Sheet#"+str(i)+"-"+e.name()+".xml","w")
                f = open(local_path + "Sheets/"+"Sheet#"+str(i)+"-"+e.name()+".xml","w")
            finally:
                f.write(toXML(e))
                f.close()
            i+=1

        i=1
        for e in o.props():
            try:
                f = open(local_path + "Blueprints/Props"+"Prop#"+str(i)+"-"+e.name()+".xml","x")
            except FileExistsError:
                f = open(local_path + "Blueprints/Props"+"Prop#"+str(i)+"-"+e.name()+".xml","w")
            finally:
                f.write(toXML(e))
                f.close()
            i+=1

        i=1
        for e in o.blueprints():
            try:
                f = open(local_path + "Blueprints/"+"Blueprint#"+str(i)+"-"+e.name()+".xml","x")
            except FileExistsError:
                f = open(local_path + "Blueprints/"+"Blueprint#"+str(i)+"-"+e.name()+".xml","w")
            finally:
                f.write(toXML(e))
                f.close()
            i+=1

        res += ntab(indent+1) + "<layers>\n"
        for l in o.layers():
            res += ntab(indent+2) + "<layer\n"
            res += ntab(indent+3) + "name=\"" + l + "\"\n"
            res += ntab(indent+2) + ">\n"
            res += toXML(o.layers()[l],indent+3) + "\n"
            res += ntab(indent+2) + "</layer>\n"
        res += ntab(indent+1) + "</layers>\n"
        
        res += ntab(indent+1) + "<pawns>\n"
        for p in o.pawns():
            res += ntab(indent+2) + "<pawn\n"
            res += ntab(indent+3) + "posX=\"" + str(p[0]) + "\"\n"
            res += ntab(indent+3) + "posY=\"" + str(p[1]) + "\"\n"
            res += ntab(indent+3) + "layer=\"" + p[2] + "\"\n"
            res += ntab(indent+2) + ">\n"
            res += toXML(o.pawns()[p],indent+3) + "\n"
            res += ntab(indent+2) + "</pawn>\n"
        res += ntab(indent+1) + "</pawns>\n"
        
        res += ntab(indent+1) + "<notes>\n"
        for nte in o.notes():
            res += ntab(indent+2) + "<note\n"
            res += ntab(indent+3) + "name=\"" + nte[0] + "\"\n"
            res += ntab(indent+3) + "text=\"" + nte[1] + "\"\n"
            res += ntab(indent+2) + "/>\n"
        res += ntab(indent+1) + "</notes>\n"
        res += ntab(indent) + "</Game>\n"
        
        try:
            f = open(local_path + o.name()+".xml","x")
        except FileExistsError:
            f = open(local_path + o.name()+".xml","w")
        finally:
            f.write(res)
            f.close()


    else:
        raise Exception("ObjectNotHandled")


    return res



def fromXMLTree(root):
    #TODO Player Instance ? + Cleanup
    observe = root.tag
    new = None
    if(observe == "Item"):
        i = 0
        t = 0
        d = ""
        for att in root.attrib:
            if i==0:
                s = root.attrib[att]
            if i==1:
                t = int(root.attrib[att])
            if i==2:
                d = root.attrib[att]
            i+=1
        new = Item(s,t,d)
    

    elif(observe == "NPC"):
        i = 0
        a = 0
        n = "Unknown"
        for att in root.attrib:
            if i==0:
                a = int(root.attrib[att])
            if i==1:
                n = root.attrib[att]
            if i==2:
                d = root.attrib[att]
            i+=1
        new = NPC(n,a)
        new.redescribe(d)
        for child in root:
            if(child.tag == "inventory"):
                for it in child:
                    new.addItem(fromXMLTree(it))
            if(child.tag == "stats"):
                for c in child:
                    s=""
                    v=None
                    j=0
                    for e in c.attrib:
                        if(j==0):
                            s = c.attrib[e]
                        else:
                            v = c.attrib[e]
                        j += 1
                    new.add_stat(s,v)


    elif(observe == "PC"):
        i = 0
        ID = 0
        n = "Unknown"
        for att in root.attrib:
            if i==0:
                ID = int(root.attrib[att])
            if i==1:
                n = root.attrib[att]
            if i==2:
                d = root.attrib[att]
            i+=1
        new = PC(ID,n)
        new.redescribe(d)
        for child in root:
            if(child.tag == "inventory"):
                for it in child:
                    new.addItem(fromXMLTree(it))
            if(child.tag == "stats"):
                for c in child:
                    s=""
                    v=None
                    j=0
                    for e in c.attrib:
                        if(j==0):
                            s = c.attrib[e]
                        else:
                            v = int(c.attrib[e]) #Maybe not int depends on rules
                        j += 1
                    new.add_stat(s,v)


    elif(observe == "Player"): #???
        raise Exception("NotHandled?")
        #TODO

    elif(observe == "Prop"):
        i = 0
        t = 0
        d = ""
        s = 0
        for att in root.attrib:
            if i==0:
                n = root.attrib[att]
            if i==1:
                t = int(root.attrib[att])
            if i==2:
                d = root.attrib[att]
            if i==3:
                s = int(root.attrib[att])
            i+=1
        new = Prop(n,t,d,s)


    elif(observe == "Cell"):
        i = 0
        g = 0
        w = 0b0
        d = 0b0
        for att in root.attrib:
            if i==0:
                g = int(root.attrib[att])
            if i==1:
                w = (int(root.attrib[att],2))
            if i==2:
                d = (int(root.attrib[att],2))
            i+=1
        new = Cell([],g,w,d)
        for child in root:
            for cont in child:
                new.add_content(fromXMLTree(cont))


    elif(observe == "Blueprint"):
        i = 0
        n="Unlabeled"
        for att in root.attrib:
            if i==0:
                n = root.attrib[att]
            if i==1:
                l = int(root.attrib[att])
            if i==2:
                w = int(root.attrib[att])
            i+=1
        new = Blueprint(l,w,n)
        for grid in root:
            y = 0
            for row in grid:
                x = 0 
                for cell in row:
                    new.set_cell(x,y,fromXMLTree(cell))
                    x+=1
                y+=1


    elif(observe == "Game"):
        for att in root.attrib:
            n = root.attrib[att]
        new = Game(n,False)
        for tab in root:
            if (tab.tag == "layers"):
                for l in tab:
                    for att in l.attrib:
                        if(att=="name"):
                            layer_name = l.attrib[att]
                    for child in l:
                        bp = fromXMLTree(child)
                    new.new_layer(layer_name,0,0,bp)
            if (tab.tag == "pawns"):
                for p in tab:
                    x = (-1)
                    y = (-1)
                    for att in p.attrib:
                        if(att=="posX"):
                            x = int(p.attrib[att])
                        elif(att=="posY"):
                            y = int(p.attrib[att])
                        else:
                            layer = p.attrib[att]
                    for child in p:
                        sheet = fromXMLTree(child)
                    new.add_pawn(sheet,x,y,layer)
            if (tab.tag == "notes"):
                for nte in tab:
                    name=""
                    text=""
                    for att in nte.attrib:
                        name = nte.atrib[0]
                        text = nte.attrib[1]
                    new.add_note(text,name)
       
        local_path = TARGET_DIRECTORY + n + "/"
        for it in os.listdir(local_path+"Items/"):
            new.add_item(fromXML(local_path+"Items/"+it))
        for npc in os.listdir(local_path+"Sheets/"):
            if(npc.endswith(".xml")): 
                new.add_character(fromXML(local_path+"Sheets/"+npc))
        for pc in os.listdir(local_path+"Sheets/PC/"):
            new.add_character(fromXML(local_path+"Sheets/PC"+pc))
        for blp in os.listdir(local_path+"Blueprints/"):
            if(blp.endswith(".xml")): 
                new.add_blueprint(fromXML(local_path+"Blueprints/"+blp))
        for pr in os.listdir(local_path+"Blueprints/Props/"):
            new.add_prop(fromXML(local_path+"Blueprints/"+pr))
        #for pl in listdir(local_path+"Player/"):


    else:
        raise Exception("InvalidObject")

    
    return new

def fromXML(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return fromXMLTree(root)
   
###################TEST##########################

"""
bp = blueprint.Blueprint(10,10)
bp.set_cell(9,9, (blueprint.Cell( {blueprint.Prop("Levier",1,"ça tire")} )) )
#print(toXML(bp)) # >> test2.xml
#print(fromXML("test2.xml"))
"""

"""
new1 = items.Item("Balle",1,"Rigolo")
new = pawns.NPC()
new.addItem(new1)
new.add_stat("INT",14)
new.redescribe("BLABLA BLA")
#print(toXML(new)) # >> test1.xml
#print(toXML(fromXML("test1.xml")))
"""

"""
#need the previous two
#TO BE EXECUTED AT : ../Dungeon-Kitchen/
g = game.Game("HEYITSME") # add False if exists
g.new_layer("1st",10,10,bp)
g.add_blueprint(bp)
g.add_pawn(new,2,2,"1st")
g.add_character(new)
g.add_item(new1)
#toXML(g)
#g1 = fromXML("./projects/HEYITSME/HEYITSME.xml")
#g2 = g1.copy()
#toXML(g2)
"""