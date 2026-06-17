class Item:
    def __init__(self, Name, Type=0, Description=""):
        self._name = Name 
        self._type = Type #TODO
        self._desc = Description

    #getters
    def name(self):
        return self._name
    def type(self):
        return self._type
    def decription(self):
        return self._desc

    #setters
    def rename(self,n):
        self._name = n
    def redefine(self,t):
        self._type = t
    def redescribe(self,d):
        self._desc = d

    #methods
    def copy(self):
        return Item(self._name, self._type, self._desc)
