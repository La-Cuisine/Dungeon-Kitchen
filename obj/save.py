import xml.etree.ElementTree as ET
import os

from obj.items import *
from obj.skills import *
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
    #TODO Player Instance ?
    res = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    if (o is None):
        res += ntab(indent) + "<Empty></Empty>\n" 
    elif isinstance(o,Item):
        res = ntab(indent) + "<Item\n"
        res += ntab(indent+1) + "name=\"" + o.name() + "\"\n" 
        res += ntab(indent+1) + "type=\"" + str(o.type()) + "\"\n"
        res += ntab(indent+1) + "description=\"" + o.description() + "\"\n"
        res += ntab(indent+1) + "image=\"" + o.image_reference() + "\"\n"
        res += ntab(indent) + "/>\n"


    elif isinstance(o,Skill):
        res = ntab(indent) + "<Skill\n"
        res += ntab(indent+1) + "name=\"" + o.name() + "\"\n" 
        res += ntab(indent+1) + "type=\"" + str(o.type()) + "\"\n"
        res += ntab(indent+1) + "description=\"" + o.description() + "\"\n"
        res += ntab(indent+1) + "image=\"" + o.image_reference() + "\"\n"        
        res += ntab(indent) + "/>\n"
 

    elif isinstance(o,NPC):
        res = ntab(indent) + "<NPC\n"
        res += ntab(indent+1) + "alignement=\"" + str(o.alignement()) + "\"\n" 
        res += ntab(indent+1) + "name=\"" + o.name() + "\"\n"
        res += ntab(indent+1) + "description=\"" + o.description() + "\"\n"
        res += ntab(indent+1) + "image=\"" + o.image_reference() + "\"\n"        
        res += ntab(indent) + ">\n"
        res += ntab(indent+1) + "<inventory>\n"
        for i in o.inventory():
            res += toXML(i,indent+2) 
        res += ntab(indent+1) + "</inventory>\n"
        res += ntab(indent+1) + "<skills>\n"
        for s in o.skills():
            res += toXML(s,indent+2)
        res += ntab(indent+1) + "</skills>\n"
        res += ntab(indent+1) + "<stats>\n"
        for s in o.stats():
            res += ntab(indent+2) + "<couple\n"
            res += ntab(indent+3) + "stat=\"" + s + "\"\n"
            res += ntab(indent+3) + "value=\"" + str(o.stats()[s]) + "\"\n"
            res += ntab(indent+2) + "/>\n"
        res += ntab(indent+1) + "</stats>\n"
        res += ntab(indent) + "</NPC>\n"


    elif isinstance(o,PC):
        res = ntab(indent) + "<PC\n"
        res += ntab(indent+1) + "ID=\"" + str(o.player()) + "\"\n" 
        res += ntab(indent+1) + "name=\"" + o.name() + "\"\n"
        res += ntab(indent+1) + "description=\"" + o.description() + "\"\n"
        res += ntab(indent+1) + "image=\"" + o.image_reference() + "\"\n"        
        res += ntab(indent) + ">\n"
        res += ntab(indent+1) + "<inventory>\n"
        for i in o.inventory():
            res += toXML(i,indent+2) 
        res += ntab(indent+1) + "</inventory>\n"
        res += ntab(indent+1) + "<skills>\n"
        for s in o.skills():
            res += toXML(s,indent+2) 
        res += ntab(indent+1) + "</skills>\n"
        res += ntab(indent+1) + "<stats>\n"
        for s in o.stats():
            res += ntab(indent+2) + "<couple\n"
            res += ntab(indent+3) + "stat=\"" + s + "\"\n"
            res += ntab(indent+3) + "value=\"" + str(o.stats()[s]) + "\"\n"
            res += ntab(indent+2) + "/>\n"
        res += ntab(indent+1) + "</stats>\n"
        res += ntab(indent) + "</PC>\n"


    elif isinstance(o,Player):
        raise Exception("NotHandled?")
        #TODO

    elif isinstance(o,Prop):
        res = ntab(indent) + "<Prop\n"
        res += ntab(indent+1) + "name=\"" + o.name() + "\"\n" 
        res += ntab(indent+1) + "type=\"" + str(o.type()) + "\"\n"
        res += ntab(indent+1) + "description=\"" + o.description() + "\"\n"
        res += ntab(indent+1) + "state=\"" + str(o.state()) + "\"\n"
        res += ntab(indent+1) + "image=\"" + o.image_reference() + "\"\n"
        res += ntab(indent) + "/>\n"


    elif isinstance(o,Cell):
        res = ntab(indent) + "<Cell\n"
        #note: retrieve bin from string with bin(int(x,2)) 
        res += ntab(indent+1) + "ground=\"" + str(o.ground()) + "\"\n"
        res += ntab(indent+1) + "walls=\"" + str(bin(o.walls())) + "\"\n"
        res += ntab(indent+1) + "doors=\"" + str(bin(o.doors())) + "\"\n"
        res += ntab(indent+1) + "image=\"" + o.image_reference() + "\"\n"        
        res += ntab(indent) + ">\n"
        res += ntab(indent+1) + "<contents>\n" 
        for p in o.contents():
            res += toXML(p,indent+2)
        res += ntab(indent+1) + "</contents>\n"
        res += ntab(indent) + "</Cell>\n"


    elif isinstance(o,Blueprint):
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


    elif isinstance(o,Game):
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
        for e in o.skills():
            try:
                f = open(local_path + "Skills/"+"Skill#"+str(i)+"-"+e.name()+".xml","x")
            except FileExistsError:
                f = open(local_path + "Skills/"+"Skill#"+str(i)+"-"+e.name()+".xml","w")
            finally:
                f.write(toXML(e))
                f.close()
            i+=1

        i=1
        for e in o.characters():
            try:
                if(isinstance(e,PC)):
                    f = open(local_path + "Sheets/PC"+"Sheet#"+str(i)+"-"+e.name()+".xml","x")
                f = open(local_path + "Sheets/"+"Sheet#"+str(i)+"-"+e.name()+".xml","x")
            except FileExistsError:
                if(isinstance(e,PC)):
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
    #TODO Player Instance 
    observe = root.tag
    new = None
    if(observe == "Item"):
        for att in root.attrib:
            if (att=="name"):
                s = root.attrib[att]
            if (att=="type"):
                t = root.attrib[att]
            if (att=="description"):
                d = root.attrib[att]
            if (att=="image"):
                img = root.attrib[att]
        new = Item(s,t,d)
        new.new_reference(img)
   

    elif(observe == "Skill"):
        for att in root.attrib:
            if (att == "name"):
                s = root.attrib[att]
            if (att == "type"):
                t = root.attrib[att]
            if (att == "description"):
                d = root.attrib[att]
            if (att == "image"):
                img = root.attrib[att]
        new = Skill(s,t,d)
        new.new_reference(img)

    elif(observe == "NPC"):
        for att in root.attrib:
            if (att == "alignement"):
                a = int(root.attrib[att])
            if (att == "name"):
                n = root.attrib[att]
            if (att == "description"):
                d = root.attrib[att]
            if (att == "image"):
                img = root.attrib[att]
        new = NPC(n,a)
        new.redescribe(d)
        new.new_reference(img)
        for child in root:
            if(child.tag == "inventory"):
                for it in child:
                    new.addItem(fromXMLTree(it))
            if(child.tag == "skills"):
                for sk in child:
                    new.addSkill(fromXMLTree(sk))
            if(child.tag == "stats"):
                for c in child:
                    for e in c.attrib:
                        if(e == "stat"):
                            s = c.attrib[e]
                        else:
                            v = int(c.attrib[e]) #Maybe not int depends on rules
                    new.add_stat(s,v)


    elif(observe == "PC"):
        for att in root.attrib:
            if (att == "ID"):
                ID = int(root.attrib[att])
            if (att == "name"):
                n = root.attrib[att]
            if (att == "description"):
                d = root.attrib[att]
            if (att == "image"):
                img = root.attrib[att]
        new = PC(ID,n)
        new.redescribe(d)
        new.new_reference(img)
        for child in root:
            if(child.tag == "inventory"):
                for it in child:
                    new.addItem(fromXMLTree(it))
            if(child.tag == "skills"):
                for sk in child:
                    new.addSkill(fromXMLTree(sk))           
            if(child.tag == "stats"):
                for c in child:
                    for e in c.attrib:
                        if(e == "stat"):
                            s = c.attrib[e]
                        else:
                            v = int(c.attrib[e]) #Maybe not int depends on rules
                    new.add_stat(s,v)


    elif(observe == "Player"): #???
        raise Exception("NotHandled?")
        #TODO

    elif(observe == "Prop"):
        for att in root.attrib:
            if (att == "name"):
                n = root.attrib[att]
            if (att == "type"):
                t = int(root.attrib[att])
            if (att == "description"):
                d = root.attrib[att]
            if (att == "state"):
                s = int(root.attrib[att])
            if (att == "image"):
                img = root.attrib[att]
        new = Prop(n,t,d,s)
        new.new_reference(img)

    elif(observe == "Cell"):
        for att in root.attrib:
            if (att == "ground"):
                g = int(root.attrib[att])
            if (att == "walls"):
                w = (int(root.attrib[att],2))
            if (att == "doors"):
                d = (int(root.attrib[att],2))
            if (att == "image"):
                img = root.attrib[att]
        new = Cell([],g,w,d)
        new.new_reference(img)
        for child in root:
            for cont in child:
                new.add_content(fromXMLTree(cont))


    elif(observe == "Blueprint"):
        for att in root.attrib:
            if (att == "name"):
                n = root.attrib[att]
            if (att == "length"):
                l = int(root.attrib[att])
            if (att == "width"):
                w = int(root.attrib[att])
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
        for folder in os.listdir(local_path+"Assets/Images/"):
            for img in os.listdir(local_path + "Assets/Images/" + folder +"/"):
                new.add_image(t, local_path+"Assets/Images/"+folder+"/"+img)
        for it in os.listdir(local_path+"Items/"):
            new.add_item(fromXML(local_path+"Items/"+it))
        for sk in os.listdir(local_path+"Skills/"):
            new.add_skill(fromXML(local_path+"Skills/"+sk))
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

def fromXML(path,Type=""):
    tree = ET.parse(path) #TODO Secure this if possible; Parse exposed to attacks
    root = tree.getroot()
    if(Type == "Blueprint" and root.tag != "Blueprint"):
        raise Exception("NotBlueprintFile")
    elif(Type == "Prop" and root.tag != "Prop"):
        raise Exception("NotPropFile")
    elif(Type == "Cell" and root.tag != "Cell"):
        raise Exception("NotCellFile")
    elif(Type == "Item" and root.tag != "Item"):
        raise Exception("NotItemFile")
    elif(Type == "Skill" and root.tag != "Skill"):
        raise Exception("NotSkillFile")
    elif(Type == "NPC" and root.tag != "NPC"):
        raise Exception("NotNPCFile")
    elif(Type == "PC" and root.tag != "PC"):
        raise Exception("NotPCFile")
    elif(Type == "Player" and root.tag != "Player"):
        raise Exception("NotPlayerFile")
    elif(Type == "Game" and root.tag != "Game"):
        raise Exception("NotGameFile")
    elif(Type != ""):
        raise Exception("UnhandledClassFile")
    return fromXMLTree(root)

def toXML_saveto(o,path):
    res = toXML(o)
    if(isinstance(o,Game)):
        raise Exception("ObjectAlreadySaved")
    try:
        f = open(path + o.name()+".xml","x")
    except FileExistsError:
        f = open(path + o.name()+".xml","w")
    finally:
        f.write(res)
        f.close()
