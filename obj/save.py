import xml.etree.ElementTree as ET

import items
import pawns
import player
import blueprint
import game

def ntab(x):
    res = ""
    for i in range(x):
        res += "    "
    return res

def toXML(o,indent=0):
    #TODO #INACCURATE ?
    res = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    if (o is None):
        res += ntab(indent) + "<Empty></Empty>\n" 
    elif isinstance(o,items.Item):
        res = ntab(indent) + "<Item\n"
        res += ntab(indent+1) + "name=\"" + o.name() + "\"\n" 
        res += ntab(indent+1) + "type=\"" + str(o.type()) + "\"\n"
        res += ntab(indent+1) + "description=\"" + o.description() + "\"\n"
        res += ntab(indent) + "/>\n"
    
    elif isinstance(o,pawns.NPC):
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

    elif isinstance(o,pawns.PC):
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

    elif isinstance(o,player.Player):
        raise Exception("NotHandled?")

    elif isinstance(o,blueprint.Prop):
        res = ntab(indent) + "<Prop\n"
        res += ntab(indent+1) + "name=\"" + o.name() + "\"\n" 
        res += ntab(indent+1) + "type=\"" + str(o.type()) + "\"\n"
        res += ntab(indent+1) + "description=\"" + o.description() + "\"\n"
        res += ntab(indent) + "/>\n"

    elif isinstance(o,blueprint.Cell):
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

    elif isinstance(o,blueprint.Blueprint):
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


    elif isinstance(o,game.Game):
        raise Exception("NotHandled?")

    else:
        raise Exception("ObjectNotHandled")

    return res

def fromXMLTree(root):
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
        new = items.Item(s,t,d)
    
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
        new = pawns.NPC(n,a)
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
        new = pawns.PC(ID,n)
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
        new = blueprint.Prop(n,t,d,s)
    
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
        new = blueprint.Cell([],g,w,d)
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
        new = blueprint.Blueprint(l,w,n)
        for grid in root:
            y = 0
            for row in grid:
                x = 0 
                for cell in row:
                    new.set_cell(x,y,fromXMLTree(cell))
                    x+=1
                y+=1

    elif(observe == "Game"): #???
        raise Exception("NotHandled?")
    else:
        raise Exception("InvalidObject")
    return new

def fromXML(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return fromXMLTree(root)
   
###################TEST##########################

#bp = blueprint.Blueprint(10,10)
#bp.set_cell(9,9, (blueprint.Cell( {blueprint.Prop("Levier",1,"ça tire")} )) )
#bp.get_cell(9,9).remove_content(0)

#new1 = items.Item("Balle",1,"Rigolo")
#new = pawns.NPC()
#new.addItem(new1)
#new.add_stat("INT",14)
#new.redescribe("BLABLA BLA")

#print(toXML(new))

#print(toXML(bp))

#print(toXML(fromXML("test1.xml")))
#print(fromXML("test2.xml"))

