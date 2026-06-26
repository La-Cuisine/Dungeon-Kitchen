import os

from obj.items import *
from obj.skills import *
from obj.blueprint import *
from obj.pawns import *
from obj.player import *


def generate_FileSystemProject(project_name):
    try:
        os.mkdir("./projects/"+project_name)
    except FileExistsError:
        if(os.path.isdir("./projects/"+project_name)):
            return generate_FileSystemProject(project_name+"(1)")
    
    os.makedirs("./projects/"+project_name+"/Assets/Images")
    os.mkdir("./projects/"+project_name+"/Assets/Images/Cells")
    os.mkdir("./projects/"+project_name+"/Assets/Images/Props")
    os.mkdir("./projects/"+project_name+"/Assets/Images/Items")
    os.mkdir("./projects/"+project_name+"/Assets/Images/Skills")
    os.mkdir("./projects/"+project_name+"/Assets/Images/Characters")
    os.mkdir("./projects/"+project_name+"/Items")
    os.mkdir("./projects/"+project_name+"/Skills")
    os.makedirs("./projects/"+project_name+"/Sheets/PC")
    os.makedirs("./projects/"+project_name+"/Blueprints/Props")
    #os.mkdir("./projects/"+project_name+"/Players")
    #Object Class Game is stored locally in the project_name directory 
    return project_name



class Game:
    def __init__(self,name="Untitled_Session",new=True):
        #TODO
        #self._name = name
        self.__base_length = 64
        self.__base_width = 64
        self._layers = dict() #(layer_name:Blueprint)
        self._pawns = dict() #((x,y,layer_name):Pawn)
        
        self._assets = dict() #(asset_type:assetList)
        self._assets["Images"] = dict() #(imageTypeList)
        self._assets["Images"]["Cells"] = []
        self._assets["Images"]["Props"] = []
        self._assets["Images"]["Items"] = []
        self._assets["Images"]["Skills"] = []
        self._assets["Images"]["Characters"] = []
        
        self._itemList = [] #(Item)
        self._skillList = [] #(Skill)
        self._charList = [] #(PC/NPC)
        self._propList = [] #(Prop)
        self._bpList = [] #(Blueprint)
        self._notes = [] #((name,text))
        
        if(new):
            self._name = generate_FileSystemProject(name)
        else:
            self._name = name


    #getters
    def name(self):
        return self._name
    def layers(self):
        return self._layers
    def get_layer(self,s):
        if not(s in self._layers):
            raise Exception("LayerDoesNotExist")
        return self._layers[s]
    def pawns(self):
        return self._pawns
    def get_pawn(self,x,y,l):
        if(not((x,y,l) in self._pawns)):
            raise Exception("PawnNotFound")
        return self._layers[(x,y,l)]
    def assets(self):
        return self._assets
    def get_assetList(self,al):
        if not(al in self._assets):
            raise Exception("AssetDoesNotExist")
        return self._assets[al]
    def images(self):
        return self._assets["Images"]
    def get_imageFolderList(self,Folder):
        if not(Folder in self._assets["Images"]):
            raise Exception("ImageTypeDoesNotExist")
        return self._assets["Images"][Folder]
    def get_imagePath(self,Folder,i):
        if not(Folder in self._assets["Images"]):
            raise Exception("ImageTypeDoesNotExist")
        if not(i in self._assets["Images"][Folder]):
            raise Exception("IndexOutOfRange")
        return self._assets["Images"][Folder][i]
    def items(self):
        return self._itemList
    def get_item(self,i):
        if not(i in self._itemList):
            raise Exception("ItemDoesNotExist")
        return self._itemList[i]
    def skills(self):
        return self._skillList
    def get_skill(self,s):
        if not(s in self._skillList):
            raise Exception("SkillDoesNotExist")
        return self._itemList[s]
    def characters(self):
        return self._charList
    def get_character(self,c):
        if not(c in self._charList):
            raise Exception("CharacterDoesNotExist")
        return self._charList[c]
    def props(self):
        return self._propList
    def get_prop(self,p):
        if not(p in self._propList):
            raise Exception("PropDoesNotExist")
        return self._propList[p]
    def blueprints(self):
        return self._bpList
    def get_blueprint(self,bp):
        if not(bp in self._bpList):
            raise Exception("BlueprintDoesNotExist")
        return self._bpList[bp]
    def notes(self):
        return self._notes
    def get_note(self,i):
        if(0 > i or i > len(self._notes)):
            raise Exception("IndexOutOfRange")
        return self._notes[i]



    #setters
    def rename(self,n):
        os.rename(self._name,n)
        self._name = n



    #methods
    def new_layer(self, s="", X=0, Y=0, m=None):
        if (s==""):
            name = "Untitled "
            name += (len(self._layers)+1)
        else: 
            name = s
        if name in self._layers:
            raise Exception("NameAlreadyInUse")
        if (not(m is None)) and (not isinstance(m,Blueprint)):
            raise Exception("InvalidArgument")
        else:
            if m is None:
                new = Blueprint(self._base_length, self._base_width) 
                if not(X<1 or Y<1):
                    new.resize(X,Y)
            else: 
                new = m
            self._layers[name] = new
    def remove_layer(self,s):
        if not(s in self._layers):
            raise Exception("LayerDoesNotExist")
        res = self._layers[s] 
        del self._layers[s]
        return res
    def replace_layer(self,s,m):
        if not(s in self._layers):
            raise Exception("LayerDoesNotExist")
        if (not(m is None)) and (not isinstance(m,Blueprint)):
            raise Exception("InvalidArgument")
        self._layers[s] = m
    def swap_layers(self,s1,s2):
        if not(s1 in self._layers):
            raise Exception("LayerDoesNotExist")
        if not(s2 in self._layers):
            raise Exception("LayerDoesNotExist")
        limbo = self._layers[s2]
        self._layers[s2] = self._layers[s1]
        self._layers[s1] = limbo


    def add_pawn(self,p,x,y,l):
        if((x,y,l) in self._pawns):
            raise Exception("CellAlreadyOccupied")
        if(not (l in self._layers)):
            raise Exception("LayerDoesNotExist")
        if(x<0 or x>self._layers[l].length() or y<0 or y>self._layers[l].width()):
            print(x,y)
            print("\n")
            raise Exception("IndexOutOfRange")
        if((not isinstance(p,NPC)) and (not isinstance(p,PC))):
            raise Exception("InvalidArgument")
        self._pawns[(x,y,l)] = p
    def remove_pawn(self,x,y,l):
        if(not((x,y,l) in self._pawns)):
            raise Exception("PawnNotFound")
        res = self._pawns[(x,y,l)] 
        del self._pawns[(x,y,l)]
        return res
    def move_pawn(self, x1, y1, l1, x2, y2, l2):
        if(not((x1,y1,l1) in self._pawns)):
            raise Exception("PawnNotFound")
        if((x2,y2,l2) in self._pawns):
            raise Exception("CellAlreadyOccupied")
        self._pawns[(x2,y2,l2)] = self._pawns[(x1,y1,l1)]
        del self._pawns[(x1,y1,l1)]
    def swap_pawns(self, x1, y1, l1, x2, y2, l2):
        if(not((x1,y1,l1) in self._pawns)):
            raise Exception("PawnNotFound")
        if(not((x2,y2,l2) in self._pawns)):
            raise Exception("PawnNotFound")
        limbo = self._pawns[(x2,y2,l2)]
        self._pawns[(x2,y2,l2)] = self._pawns[(x1,y1,l1)]
        self._pawns[(x1,y1,l1)] = limbo


    def add_image(self,Folder,path):
        if not(Folder in self._assets["Images"]):
            raise Exception("ImageTypeDoesNotExist")
        self._assets["Images"][Folder].append(path)
    def remove_image(self,Folder,i):
        if not(Folder in self._assets["Images"]):
            raise Exception("ImageTypeDoesNotExist")
        if not(i in self._assets["Images"][t]):
            raise Exception("IndexOutOfRange")
        res = self._assets["Images"][Folder][i]        
        del self._assets["Images"][Folder][i]
        return res
    
    
    def add_item(self, it):
        if(not isinstance(it, Item)):
            raise Exception("InvalidArgument")
        self._itemList.append(it)
    def remove_item(self, i):
        if(0>i or i> len(self._itemList)):
            raise Exception("IndexOutOfRange")
        res = self._itemList[i]
        del self._itemList[i]
        return res

    def add_skill(self, sk):
        if(not isinstance(sk, Skill)):
            raise Exception("InvalidArgument")
        self._skillList.append(sk)
    def remove_skill(self, i):
        if(0>i or i> len(self._skillList)):
            raise Exception("IndexOutOfRange")
        res = self._skillList[i]
        del self._skillList[i]
        return res

    def add_character(self, c):
        if((not isinstance(c,NPC)) and (not isinstance(c,PC))):
            raise Exception("InvalidArgument")
        self._charList.append(c)
    def remove_character(self, i):
        if(0>i or i> len(self._charList)):
            raise Exception("IndexOutOfRange")
        res = self._charList[i]
        del self._charList[i]
        return res

    def add_prop(self, p):
        if(not isinstance(p, Prop)):
            raise Exception("InvalidArgument")
        self._propList.append(p)
    def remove_prop(self, i):
        if(0>i or i> len(self._propList)):
            raise Exception("IndexOutOfRange")
        res = self._propList[i]
        del self._propList[i]
        return res

    def add_blueprint(self, bp):
        if(not isinstance(bp, Blueprint)):
            raise Exception("InvalidArgument")
        self._bpList.append(bp)
    def remove_blueprint(self, i):
        if(0>i or i> len(self._bpList)):
            raise Exception("IndexOutOfRange")
        res = self._bpList[i]
        del self._bpList[i]
        return res

    def add_note(self,text,name="Untitled"):
        self._notes.append((name,text))
    def remove_note(self, i):
        if(0>i or i> len(self._notes)):
            raise Exception("IndexOutOfRange")
        res = self._notes[i]
        del self._notes[i]
        return res

    def copy(self):
        res = Game(self._name+" - Copy")
        for l in self._layers:
            res.new_layer(l,0,0,self._layers[l])
        for p in self._pawns:
            res.add_pawn(self._pawns[p],p[0],p[1],p[2])
        for folder in self._assets["Images"]:
            for img in self._assets["Images"][folder]:
                res.add_image(folder,img)
        for it in self._itemList:
            res.add_item(it)
        for sk in self._skillList:
            res.add_skill(sk)
        for c in self._charList:
            res.add_character(c)
        for p in self._propList:
            res.add_prop(p)
        for bp in self._bpList:
            res.add_blueprint(bp)
        for nte in self._notes:
            res.add_note(nte[1],nte[0])

        return res
