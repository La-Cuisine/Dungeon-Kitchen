from obj.pawns import *

class Player:
    def __init__(self, Name, ID=0):
        #TODO
        self._playerID = ID
        self.__mdp = "1234"
        self._char = None #ref instead of raw ?
        self._notes = dict()

    #getters
    def ID(self):
        return self._playerID
    def character(self):
        return self._char
    def notes(self):
        return self._notes
    def get_note(self,i):
        if(0 > i or i > len(self._notes)):
            raise Exception("IndexOutOfRange")
        return self._notes[i]
    
    #setters
    def reassign(self, ID):
        self._playerID = ID
    def newRole(self, sheet):
        if(not (isinstance(sheet,pawns.PC))):
            raise Exception("InvalidArgument")
        self._char = sheet

    #method
    def check_password(self, mdp):
        return (self.__mdp == mdp)
    def _edit_password(self, mdp, new):
        self.__mdp = new

    def add_note(self,text,name="Untitled"):
        self._notes.append((name,text))
    def remove_note(self, i):
        if(0>i or i> len(self._notes)):
            raise Exception("IndexOutOfRange")
        res = self._notes[i]
        del self._notes[i]
        return res
