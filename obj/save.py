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
        res += ntab(indent+1) + "ground=\"" + str(bin(o.ground())) + "\"\n"
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


def fromXML(path):
    raise Exception("NotImplemented")
    tree = ET.parse(path)
    root = tree.getroot()
    print (root.tag, root.attrib)
    #here for test
    print(". . .") 
    for child in root:
        if child is None:
            continue
        print(child.tag,child.attrib)#child.attrib)
        if( child.tag == "inventory" or child.tag == "stats" or child.tag == "grid" ):
            for great in child:
                if(great.tag == "row"):
                    for cell in great:
                        print(cell.tag,cell.attrib)
                        for cont in cell:
                            if cont is None:
                                continue
                            for it in cont:
                                if it is None:
                                    continue
                                print(it.tag,it.attrib)
                print(great.tag,great.attrib)


    
###################TEST##########################

bp = blueprint.Blueprint(10,10)
bp.set_cell(9,9, (blueprint.Cell( {blueprint.Prop("Levier",1,"ça tire")} )) )
#bp.get_cell(9,9).remove_content(0)

new1 = items.Item("Balle",1,"Rigolo")
new = pawns.NPC()
new.addItem(new1)
new.add_stat("INT",14)
new.redescribe("BLABLA BLA")
#print(toXML(new))
#print(toXML(bp))
#print(fromXML("test1.xml"))
#print(fromXML("test2.xml"))

