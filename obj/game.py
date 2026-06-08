import blueprint 

class game:
  def __init__(self):
    #???
    self.__base_length = 100
    self.__base_width = 100
    self._layers = dict() #(layer_name:map)
    self._notes = dict()
  
  #getters
  def layers(self):
    return self._layers

  #setters

  #methods
  def new_layer(self, s="", X=0, Y=0, m=None):
    if (s==""):
      name = "Untitled "
      name += (len(self._layers)+1)
    else:
      if s in self._layers:
        raise Exception("NameAlreadyInUse")
      else:
        name = s
    if (not(m is None)) and (not isinstance(m,Blueprint)):
      raise Exception("InvalidArgument")
    else:
      if m is None:
        new = Blueprint(self._base_length, self._base_width) 
        if not(X<1 or Y<1):
          new.resize(X,Y)
      else: 
        new = m
      self._layers[name] = m
  
  def remove_layer(self,s):
    if not(s in self._layers):
      raise Exception("DoesNotExist")
    else:
      del self._layers[s]
