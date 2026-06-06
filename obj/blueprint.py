class Cell:
  def __init__(self, Content=0, Walls=0b0000, Doors=0b0000):
    if(Content<0 or Content>3):
      raise Exception("ArgumentOutOfRange")
    self._content = Content # 0=path; 1=void; 2=filled; 3=transition
    if(Walls>0b1111 or Walls<0b000):
      raise Exception("ArgumentOutOfRange")
    self._walls = Walls # 0b1010
    if(Doors>0b1111 or Doors<0b000):
      raise Exception("ArgumentOutOfRange")
    self._doors = Doors # 0b1010

  #getters
  def content(self):
    return self._content
  def walls(self):
    return self._walls
  def doors(self):
    return self._doors
  
  #setters
  def set_content(c):
    if(c<0 or c>3):
      raise Exception("ArgumentOutOfRange")
    self._content = c
  def set_walls(w):
    if(w>0b1111 or w<0b000):
      raise Exception("ArgumentOutOfRange")
    self._walls = w # 0b1010
  def set_doors(d):
    if(d>0b1111 or d<0b000):
      raise Exception("ArgumentOutOfRange")
    self._doors = d # 0b1010


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
  def name():
    return self._name
  def length():
    return self._length
  def width():
    return self._width
  def grid():
    return self._grid
  def get_cell(x,y):
    return self._grid[x][y]

  #setters
  def rename(s):
    self._name = s
  def set_cell(x,y,c):
    if not isinstance(c,Cell):
      raise Exception("InvalidArgument")
    self._grid[x][y] = c

  #methods
  def reset(self):
    for i in range(self._length):
      for j in range(self._width):
        self._grid[i][j] = Cell()
  
  def resize(self, X, Y):
    #resize deletes grid
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
