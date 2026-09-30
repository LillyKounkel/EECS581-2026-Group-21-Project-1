import rand

def easy_solve:
  # uncover cells randomly, avoiding flagged or already uncovered cells.
   
def medium_solve:
  #"""
  #Do two rules:
  #  1. if the number of hidden neighbors of a revealed cell equals that cell’s number, the AI should flag all hidden neighbors. 
  #  2. if the number of flagged neighbors of a revealed cell equals that cell’s number, the AI should open all other hidden neighbors. 
  #  If no rule applies, just call easy_solve() to uncover random tile.
  #"""
  
def hard_solve:
  #  If three side-by-side revealed cells show “1-2-1,” 
  #  the two outer hidden neighbors are mines (and should be flagged), while the inner hidden neighbor is safe (and should be opened).
  #  If this rule does not apply, call medium_solve()
