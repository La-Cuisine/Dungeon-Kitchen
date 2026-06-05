class cell:
  def __init__(self, Content, State, Walls):
    self.content = Content
    self.state = State
    self.walls = Walls

class map: 
  def __init__(self, X, Y):
    self._name = "Untitled"
    self._length = X
    self._width = Y
    self._grid = []
    #map initialisation
    for i in range(X):
      l = []
      for j in range(Y):
        l.append(0)
      self._grid.append(l)
  def __init__(self, s, X, Y):
    self._name = s
    self._length = X
    self._width = Y
    self._grid = []
    #map initialisation
    for i in range(X):
      l = []
      for j in range(Y):
        l.append(0)
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

  #setters
  def rename(s):
    self._name = s
  def set_cell(x,y,content):
    self._grid[x][y] = content

  #methods
  def reset(self):
    for i in range(self._length):
      for j in range(self._width):
        self._grid[i][j] = 0
  
  def resize(self, X, Y):
    new = []
    for i in range(X):
      l = []
      for j in range(Y):
          l.append(0)
      new.append(l)
    self._grid = new
    self._length = X
    self._width = Y
