class Item:
    def __init__(self, Name, Type=0, Description=""):
        self._name = Name 
        self._type = Type #TODO
        self._desc = Description
        self._img =  "" # FilePath

    #getters
    def name(self):
        return self._name
    def type(self):
        return self._type
    def description(self):
        return self._desc
    def image_reference(self):
        return self._img

    #setters
    def rename(self,n):
        self._name = n
    def redefine(self,t):
        self._type = t
    def redescribe(self,d):
        self._desc = d
    def new_reference(self,path):
        self._img = path

    #methods
    def copy(self):
        res = Item(self._name, self._type, self._desc)
        res.new_reference(self._img)
        return res
