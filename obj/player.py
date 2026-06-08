import pawns

class Player:
  def __init__(self, Name, ID=0):
    self._playerID = ID
    self.__mdp = "1234"
    self._char = None
    self._notes = dict()

  #getters
  def ID(self):
    return self._playerID
  def character(self):
    return self._char
  
  #setters
  def reassign(self, ID):
    self._playerID = ID
  def newRole(self, sheet):
    if(not (isinstance(sheet,PC))):
      raise Exception("InvalidArgument")
    self._char = sheet

  #method
  def check_password(self, mdp):
    return (sel.__mdp == mdp)
  def _edit_password(self, mdp, new):
    self.__mdp = new
