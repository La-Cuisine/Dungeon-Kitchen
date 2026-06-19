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
        res = ntab(indent) + "<Item>\n"
        res += ntab(indent+1) + "<name>" + o.name() + "</name>\n" 
        res += ntab(indent+1) + "<type>" + str(o.type()) + "</type>\n"
        res += ntab(indent+1) + "<description>" + o.description() + "</description>\n"
        res += ntab(indent) + "</Item>\n"
    
    elif isinstance(o,pawns.NPC):
        res = ntab(indent) + "<NPC>\n"
        res += ntab(indent+1) + "<alignement>" + str(o.alignement()) + "</alignement>\n" 
        res += ntab(indent+1) + "<name>" + o.name() + "</name>\n"
        res += ntab(indent+1) + "<stats>\n"
        for s,v in o.stats():
            res += ntab(indent+2) + "<couple>\n"
            res += ntab(indent+3) + "<stat>" + s + "</stat>\n"
            res += ntab(indent+3) + "<value>" + str(v) + "</value>\n"
            res += ntab(indent+2) + "</couple>\n"
        res += ntab(indent+1) + "</stats>\n"
        res += ntab(indent+1) + "<description>" + o.description() + "</description>\n" 
        res += ntab(indent+1) + "<inventory>\n"
        for i in o.inventory():
            res += toXML(i,indent+2) 
        res += ntab(indent+1) + "</inventory>\n"
        res += ntab(indent) + "</NPC>\n"

    elif isinstance(o,pawns.PC):
        res = ntab(indent) + "<PC>\n"
        res += ntab(indent+1) + "<ID>" + str(o.player()) + "</ID>\n" 
        res += ntab(indent+1) + "<name>" + o.name() + "</name>\n"
        res += ntab(indent+1) + "<stats>\n"
        for s,v in o.stats():
            res += ntab(indent+2) + "<couple>\n"
            res += ntab(indent+3) + "<stat>" + s + "</stat>\n"
            res += ntab(indent+3) + "<value>" + str(v) + "</value>\n"
            res += ntab(indent+2) + "</couple>\n"
        res += ntab(indent+1) + "</stats>\n"
        res += ntab(indent+1) + "<description>" + o.description() + "</description>\n" 
        res += ntab(indent+1) + "<inventory>\n"
        for i in o.inventory():
            res += toXML(i,indent+2) 
        res += ntab(indent+1) + "</inventory>\n"
        res += ntab(indent) + "</PC>\n"

    elif isinstance(o,player.Player):
        raise Exception("NotHandled?")

    elif isinstance(o,blueprint.Prop):
        res = ntab(indent) + "<Prop>\n"
        res += ntab(indent+1) + "<name>" + o.name() + "</name>\n" 
        res += ntab(indent+1) + "<type>" + str(o.type()) + "</type>\n"
        res += ntab(indent+1) + "<description>" + o.description() + "</description>\n"
        res += ntab(indent) + "</Prop>\n"

    elif isinstance(o,blueprint.Cell):
        res = ntab(indent) + "<Cell>\n"
        res += ntab(indent+1) + "<contents>\n" 
        for p in o.contents():
            res += toXML(p,indent+2)
        res += ntab(indent+1) + "</contents>\n" 
        res += ntab(indent+1) + "<ground>" + str(bin(o.ground())) + "</ground>\n"
        res += ntab(indent+1) + "<walls>" + str(bin(o.walls())) + "</walls>\n"
        res += ntab(indent+1) + "<doors>" + str(bin(o.doors())) + "</doors>\n"
        res += ntab(indent) + "</Cell>\n"

    elif isinstance(o,blueprint.Blueprint):
        res = ntab(indent) + "<Blueprint>\n"
        res += ntab(indent+1) + "<name>" + o.name() + "</name>\n"
        res += ntab(indent+1) + "<length>" + str(o.length()) + "</length>\n"
        res += ntab(indent+1) + "<width>" + str(o.width()) + "</width>\n"
        res += ntab(indent+1) + "<grid>\n" 
        for i in range(o.length()):
            res += ntab(indent+2) + "<row>\n"
            for j in range (o.width()):
                res += toXML(o.get_cell(i,j),indent+3)
            res += ntab(indent+2) + "</row>\n"
        res += ntab(indent+1) + "</grid>\n" 
        res += ntab(indent) + "</Blueprint>\n"


    elif isinstance(o,game.Game):
        raise Exception("NotHandled?")

    else:
        raise Exception("ObjectNotHandled")

    return res


def fromXML(path):
    tree = ET.parse(path)
    root = tree.getroot()
    print (root.tag, root.attrib)
    print(". . .")
    #here blueprint for test
    for child in root:
        #note text is between marks, attrib is x=value within marks 
        print(child.tag,child.text)#child.attrib)


    
###################TEST##########################

new1 = items.Item("Balle",1,"Rigolo")
new = pawns.NPC()
new.addItem(new1)
new.redescribe("BLABLA BLA")
#print(toXML(new))
#print(fromXML("test.xml"))
