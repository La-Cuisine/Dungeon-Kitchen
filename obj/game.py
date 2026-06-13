import blueprint 
import pawns
import player

class game:
  def __init__(self):
    #TODO
    self.__base_length = 50
    self.__base_width = 50
    self._layers = dict()# (layer_name:map)
    self._pawns = dict()# ((x,y):occupant)
    self._notes = []#TODO ((name,text))
  
  #getters
  def layers(self):
    return self._layers
  def get_layer(self,s):
    if not(s in self._layers):
      raise Exception("LayerDoesNotExist")
  def pawns(self):
    return self._pawns
  def get_pawn(self,x,y):
    if(not((x,y) in self._pawns)):
      raise Exception("PawnNotFound")

  #setters
  #TODO

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
  def switch_layers(self,s1,s2):
    if not(s1 in self._layers):
      raise Exception("LayerDoesNotExist")
    if not(s2 in self._layers):
      raise Exception("LayerDoesNotExist")
    limbo = self._layers[s2]
    self._layers[s2] = self._layers[s1]
    self._layers[s1] = limbo



  def add_pawn(self,p,x,y,l):
    if((x,y) in self._pawns):
      raise Exception("CellAlreadyOccupied")
    if(not (l in self._layers)):
      raise Exception("LayerDoesNotExist")
    if(x<0 or x>self._layers[l].length() or y<0 or y>self._layers[l].width()):
      raise Exception("IndexOutOfRange")
    if((not isinstance(p,NPC)) and (not isinstance(p,PC))):
      raise Exception("InvalidArgument")
    self._pawns[(x,y)] = p
  def remove_pawn(self,x,y):
    if(not((x,y) in self._pawns)):
      raise Exception("PawnNotFound")
    res = self._pawns[(x,y)] 
    del self._pawns[(x,y)]
    return res
  def move_pawn(self, x1, y1, x2, y2):
    if(not((x1,y1) in self._pawns)):
      raise Exception("PawnNotFound")
    if((x2,y2) in self._pawns):
      raise Exception("CellAlreadyOccupied")
    self._pawns[(x2,y2)] = self._pawns[(x1,y1)]
    del self._pawns[(x1,y1)]
  def switch_pawns(self, x1, y1, x2, y2):
    if(not((x1,y1) in self._pawns)):
      raise Exception("PawnNotFound")
    if(not((x2,y2) in self._pawns)):
      raise Exception("PawnNotFound")
    limbo = sel._pawns[(x2,y2)]
    self._pawns[(x2,y2)] = self._pawns[(x1,y1)]
    self._pawns[(x1,y1)] = limbo

