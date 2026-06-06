import items

class NPC:
  def __init__(self,Name):
    #???
    self._size = 1 #i.e nbCells occupied
    self._align = 0 # 0:Neutral; 1:Ally; 2:Hostile
    self._name = Name
    self._stats = dict() #ex: INT:14 /alt INT:(14,(+2))
    #modifiers?
    self._desc = ""
    self._inv = []

  #getters
  def size(self):
    return self._size
  def alignement(self):
    return self._align
  def name(self):
    return self._name
  def stats(self):
    return self._stats
  def description(self):
    return self._desc
  def inventory(self):
    return self._inv

  #setters
  def resize(self, s):
    self._size = s
  def realign(self, a):
    if(a>3 or a<0):
      raise Exception("ArgumentOutOfRange")
    self._align = a
  def rename(self, n):
    self._name = n
  def alter_stat(self,s,v):
    if not s in self._stats:
      raise Exception("DoesNotExist")
    self._stats[s] = v
  def redescribe(self, d):
    self._desc = d

  #methods
  def addItem(self,it):
    if not isinstance(it,Item):
      raise Exception("InvalidArgument")
    self._inv.append(it)
  
  def removeItem(self,i):
    if(i> len(self._inv) or i<0):
      raise Exception("IndexOutOfRange")
    res = self._inv[i]
    self._inv.pop(i)
    return res

class PC:
  def __init__(self):
    #???
    self._playerID = 0 #Unassigned
    self._name = "Unknown"
    self._stats = dict() #ex: INT:14 /alt INT:(14,(+2))
    self._desc = ""
    self._inv = []

  #getters
  def player(self):
    return self._playerID
  def name(self):
    return self._name
  def stats(self):
    return self._stats
  def description(self):
    return self._desc
  def inventory(self):
    return self._inv

  #setters
  def reassign(self, ID):
    self._playerID = ID
  def alter_stat(self,s,v):
    if not s in self._stats:
      raise Exception("DoesNotExist")
    self._stats[s] = v
  def rename(self, n):
    self._name = n
  def redescribe(self, d):
    self._desc = d

  #methods
  def addItem(self,it):
    if not isinstance(it,Item):
      raise Exception("InvalidArgument")
    self._inv.append(it)
  
  def removeItem(self,i):
    if(i> len(self._inv) or i<0):
      raise Exception("IndexOutOfRange")
    res = self._inv[i]
    self._inv.pop(i)
    return res
