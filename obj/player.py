from obj.pawns import *

class Player:
    def __init__(self, Name, ID=0):
        self._playerID = ID
        self.__mdp = Name
        self.__name = Name
        self._char = None #ref instead of raw ?
        self._notes = [] # Correction: list au lieu de dict pour correspondre à add_note
        self._pc_file = "" # Ajout pour lier au fichier XML généré par PHP

    # getters
    def ID(self):
        return self._playerID
    def name(self):
        return self.__name
    def password(self):
        return self.__mdp
    def character(self):
        return self._char
    def pc_file(self):
        return self._pc_file
    def notes(self):
        return self._notes
    def get_note(self,i):
        if(0 > i or i >= len(self._notes)):
            raise Exception("IndexOutOfRange")
        return self._notes[i]
    
    # setters
    def reassign(self, ID):
        self._playerID = ID
    def newRole(self, sheet):
        if(not (isinstance(sheet,PC))):
            raise Exception("InvalidArgument")
        self._char = sheet
    def set_pc_file(self, filename):
        self._pc_file = filename
    def rename(self, name):
        self.__name = name

    # methods
    def check_password(self, mdp):
        return (self.__mdp == mdp)
    def _edit_password(self, mdp, new):
        self.__mdp = new

    def add_note(self, text, name="Untitled"):
        self._notes.append((name,text))
    def remove_note(self, i):
        if(0 > i or i >= len(self._notes)):
            raise Exception("IndexOutOfRange")
        res = self._notes[i]
        del self._notes[i]
        return res