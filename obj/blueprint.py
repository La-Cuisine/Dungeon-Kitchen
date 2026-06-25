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
    
    def copy(self):
        return Prop(self._name, self._type, self._desc, self._state)


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
    def get_content(self,i):
        if(i<0 or i>len(self._contents)):
            return Exception("IndexOutOfRange")
        return self._contents[i]
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

    def copy(self):
        return Cell(self._contents, self._ground, self._walls, self._doors)



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
        if(x<0 or y<0 or x>self._length or y>self._width):
            raise Exception("IndexOutOfRange")
        return self._grid[x][y]
    def get_cellContents(self,x,y):
        return self.get_cell(x,y).contents()
    def get_cellContent(self,x,y,i):
        return self.get_cell(x,y).get_content(i)


    #setters
    def rename(self,s):
        self._name = s
    def set_cell(self,x,y,c):
        if not isinstance(c,Cell):
            raise Exception("InvalidArgument")
        if(x<0 or y<0 or x>self._length or y>self._width):
            raise Exception("IndexOutOfRange")
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
        if(posX>endX or posY>endY):
            raise Exception("InvalidOriginIndex")
        for i in range(posX,endX):    
            for j in range(posY,endY):
                self.set_cell(i,j,mp.get_cell((i-posX),(j-posY)))
    
    def cell_add_content(self,x,y,p):
        if(x<0 or y<0 or x>self._length or y>self._width):
            raise Exception("IndexOutOfRange")
        if(not(isinstance(p,Prop))):
            raise Exception("InvalidArgument")
        self._grid[x][y].add_content(p)
    def cell_remove_content(self,x,y,i):
        if(x<0 or y<0 or x>self._length or y>self._width):
            raise Exception("IndexOutOfRange")
        if(i<0 or i>len(self._grid[x][y].contents())):
            raise Exception("IndexOutOfRange")
        return self._grid[x][y].remove_content(i)
    def moveTo_content(self, x1, y1, x2, y2, i):
        if(x1<0 or y1<0 or x1>self._length or y1>self._width):
            raise Exception("IndexOutOfRange")
        if(x2<0 or y2<0 or x2>self._length or y2>self._width):
            raise Exception("IndexOutOfRange")
        if(i<0 or i>len(self._grid[x1][y1].contents())):
            raise Exception("IndexOutOfRange")
        self._grid[x2][y2].add_content(self._grid[x1][y1].get_content(i))
        self._grid[x1][y1].remove_content(i)
    def AllMoveTo_content(self,x1,y1,x2,y2):
        if(x1<0 or y1<0 or x1>self._length or y1>self._width):
            raise Exception("IndexOutOfRange")
        if(x2<0 or y2<0 or x2>self._length or y2>self._width):
            raise Exception("IndexOutOfRange")
        for i in range(len(self._grid[x1][y1].contents())):
            self._grid[x2][y2].add_content(self._grid[x1][y1].get_content(0))
            self._grid[x1][y1].remove_content(0)
    def switch_content(self,x1,y1,x2,y2):
        if(x1<0 or y1<0 or x1>self._length or y1>self._width):
            raise Exception("IndexOutOfRange")
        if(x2<0 or y2<0 or x2>self._length or y2>self._width):
            raise Exception("IndexOutOfRange")
        acc = []
        tmp = len(self._grid[x1][y1].contents())
        for i in range(tmp):
            acc.append(self._grid[x1][y1].get_content(0))
            self._grid[x1][y1].remove_content(0)
        self.AllMoveTo_content(x2,y2,x1,y1)
        for j in range(tmp):
            self._grid[x2][y2].add_content(acc[j])    

   
    def copy(self):
        new = Blueprint(self._length, self._width, (self._name +" - Copy"))
        new.insert(self)
        return new
