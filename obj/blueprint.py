class Prop:
  def __init__(self, Name, Type=0, Description="", State=0):
    self._name = Name
    self._type = Type
    self._desc = Description
    self._state = State #ex: 0=Neutral; 1=Activated
  
  #getters
  def name(self):
    return self._name
  def type(self):
    return self._type
  def description(self):
    return self._desc
  def state(self):
    return self._state

  #setters 
  def rename(self,n):
    self._name = n
  def redefine(self,t):
    self._type = t
  def redescribe(self,d):
    self._desc = d
  def restate(self,s):
    self._state = s

  #methods
  def activate(self):
    self._state = 1
  def deactivate(self):
    self._state = 0
  def succ(self):
    self._state +=1
  def pred(self):
    self._state -=1



class Cell:
  def __init__(self, Contents=[], Ground=0, Walls=0b0000, Doors=0b0000):
    self._contents = Contents
    if(Ground<0 or Ground>4):
      raise Exception("ArgumentOutOfRange")
    self._ground = Ground # 0=terrain; 1=floor; 2=void; 3=solid; 4=transition
    if(Walls>0b1111 or Walls<0b000):
      raise Exception("ArgumentOutOfRange")
    self._walls = Walls # 0b1010 = NESW
    if(Doors>0b1111 or Doors<0b000):
      raise Exception("ArgumentOutOfRange")
    self._doors = Doors # 0b1010 = NESW

  #getters
  def contents(self):
    return self._contents
  def ground(self):
    return self._ground
  def walls(self):
    return self._walls
  def doors(self):
    return self._doors
  
  #setters
  def set_ground(self, c):
    if(c<0 or c>4):
      raise Exception("ArgumentOutOfRange")
    self._ground = c
  def set_walls(self, w):
    if(w>0b1111 or w<0b000):
      raise Exception("ArgumentOutOfRange")
    self._walls = w 
  def set_doors(self, d):
    if(d>0b1111 or d<0b000):
      raise Exception("ArgumentOutOfRange")
    self._doors = d 

  #methods 
  def add_content(self, con):
    if(not isinstance(con,Prop)): 
      raise Exception("InvalidArgument")
    self._contents.append(con)
  def remove_content(self, i):
    res = None
    if(len(self._contents)<i):
      return Exception("IndexOutOfRange")
    res = self._contents[i]
    del self._contents[i]
    return res



class Blueprint: 
  def __init__(self, X, Y, s="Unlabeled"):
    self._name = s
    if(X<1):
      raise Exception("ArgumentOutOfRange")
    if(Y<1):
      raise Exception("ArgumentOutOfRange")
    self._length = X
    self._width = Y
    self._grid = []
    #map initialisation
    for i in range(X):
      l = []
      for j in range(Y):
        l.append(Cell())
      self._grid.append(l)

  #getters
  def name(self):
    return self._name
  def length(self):
    return self._length
  def width(self):
    return self._width
  def grid(self):
    return self._grid
  def get_cell(self,x,y):
    return self._grid[x][y]

  #setters
  def rename(self,s):
    self._name = s
  def set_cell(self,x,y,c):
    if not isinstance(c,Cell):
      raise Exception("InvalidArgument")
    self._grid[x][y] = c

  #methods
  def reset(self):
    for i in range(self._length):
      for j in range(self._width):
        self._grid[i][j] = Cell()
  
  def resize(self, X, Y):
    #resize deletes previous grid
    new = []
    for i in range(X):
      l = []
      for j in range(Y):
          l.append(Cell())
      new.append(l)
    self._grid = new
    self._length = X
    self._width = Y

  def insert(self,mp,posX,posY):
    if(not isinstance(mp,Blueprint)):
      raise Exception("InvalidArgument")
    endX = mp.length()+posX
    if(self.length()<endX):
      endX = self.length()
    endY = mp.length()+posY
    if(self.width()<endY):
      endY = self.width()
    for i in range(posX,endX):    
      for j in range(posY,endY):
        self.set_cell(i,j,mp.get_cell((i-posX),(j-posY)))
