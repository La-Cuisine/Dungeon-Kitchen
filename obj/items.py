class Item:
  def __init__(self,Name):
    self._name = Name 
    self._type = 0 #TODO
    self._desc = ""

  #getters
  def name(self):
    return self._name
  def type(self):
    return self._type
  def decription(self):
    return self._desc

  #setters
  def rename(self,N):
    self._name = N
  def redefine(self,t):
    self._type = t
  def redescribe(self,d):
    self._type = d
