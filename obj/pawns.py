import items

class NPC:
    def __init__(self, Name="Unknown", Alignement=0):
        #TODO
        self._align = Alignement # 0:Neutral; 1:Ally; 2:Hostile
        self._name = Name
        self._stats = dict() #ex: INT:14 /alt INT:(14,(+2))
        #modifiers?
        self._desc = ""
        self._inv = []

    #getters
    def alignement(self):
        return self._align
    def name(self):
       return self._name
    def stats(self):
       return self._stats
    def get_stat(self,s):
        if not s in self._stats:
          raise Exception("DoesNotExist")
        return self._stats[s] 
    def description(self):
        return self._desc
    def inventory(self):
        return self._inv

    #setters
    def realign(self, a):
        if(a>3 or a<0):
          raise Exception("ArgumentOutOfRange")
        self._align = a
    def rename(self, n):
        self._name = n
    def redescribe(self, d):
        self._desc = d

    #methods
    def add_stat(self,s,v=None):
        if s in self._stats:
          raise Exception("NameAlreadyInUse")
        self._stats[s] = v
    def remove_stat(self,s):
        if not s in self._stats:
          raise Exception("DoesNotExist")
        del self._stats[s]
    def alter_stat(self,s,v):
        if not s in self._stats:
          raise Exception("DoesNotExist")
        self._stats[s] = v
   
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
    
    def copy(self):
        new = NPC(self._name, self._align)
        new.redescribe(self._desc)
        for e in self._inv:
          new.addItem(e)
        for k in self._stats:
          new.add_stat(k, self._stats[k])
        raise Exception("NotImplemented")
        return new

class PC:
    def __init__(self, ID=0, Name="Unknown"):
        #TODO
        self._playerID = ID #Unassigned
        self._name = Name
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
    def get_stat(self,s):
        if not s in self._stats:
          raise Exception("DoesNotExist")
        return self._stats[s]
    def description(self):
        return self._desc
    def inventory(self):
        return self._inv

    #setters
    def reassign(self, ID):
        self._playerID = ID
    def rename(self, n):
        self._name = n
    def redescribe(self, d):
        self._desc = d

    #methods
    def add_stat(self,s,v=None):
        if s in self._stats:
          raise Exception("NameAlreadyInUse")
        self._stats[s] = v
    def remove_stat(self,s):
        if not s in self._stats:
          raise Exception("DoesNotExist")
        del self._stats[s]
    def alter_stat(self,s,v):
        if not s in self._stats:
          raise Exception("DoesNotExist")
        self._stats[s] = v

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

    def copy(self):
        #playerID resets between instances
        new = PC(0, self._name)
        new.redescribe(self._desc)
        for e in self._inv:
          new.addItem(e)
        for k in self._stats:
          new.add_stat(k, self._stats[k])
        raise Exception("NotImplemented")
        return new
