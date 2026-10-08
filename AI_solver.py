import rand

def easy_solve: #Mason's work
  # uncover cells randomly, avoiding flagged or already uncovered cells.
   available_cells = []
  #Find cells that are neither covered or flagged.
  for row in range(logic.grind.size):
    for column in range(logic.grid_size):
      if not logic.grid.is_revealed(row, column) and not logic.grid.is_flagged(row, colum)
        available_cells.append((row, column))
  #Reveal a random cell.
  if available_cells:
    cell = random.choice(available_cells)
    logic.reveal_cell(cell[0], cell[1])

def medium_solve:
  #"""
  #Do two rules:
  #  1. if the number of hidden neighbors of a revealed cell equals that cell’s number, the AI should flag all hidden neighbors. 
  #  2. if the number of flagged neighbors of a revealed cell equals that cell’s number, the AI should open all other hidden neighbors. 
  #  If no rule applies, just call easy_solve() to uncover random tile.
  #"""
  
def hard_solve(logic): #Austin, note: this is a mess and I don't think there are ways to make it not a mess
  #  If three side-by-side revealed cells show “1-2-1,” 
  #  the two outer hidden neighbors are mines (and should be flagged), while the inner hidden neighbor is safe (and should be opened).
  #  If this rule does not apply, call medium_solve()
  grid = logic.grid

  while(not done)
    done=True
    for x in range(grid.size):
      for y in range(grid):
        cell = grid.get_cell(x,y)
        #ignore unrevealed tiles or non-2s
        if not cell.revealed:
          continue
        if not cell.adjacent==2:
          continue
        #filter for 1-2-1 setups, and branch on vertical or horizontal setups
        if(x>0 and x<(grid.size-1)):
          if(grid.get_cell(x-1,y).revealed and grid.get_cell(x-1,y).adjacent==1):
            if(grid.get_cell(x+1,y).revealed and grid.get_cell(x+1,y).adjacent==1):
              #branch on which side is already revealed
              if(grid.get_cell(x-1,y-1).revealed and grid.get_cell(x+1,y-1).revealed and grid.get_cell(x,y-1).revealed):
                #skip previously handled instances
                if(grid.get_cell(x-1,y+1).flagged):
                  continue
                #flag and reveal
                grid.get_cell(x-1,y+1).flag()
                grid.get_cell(x+1,y+1).flag()
                logic.reveal_cell(x,y+1)
                done=False
              elif(grid.get_cell(x-1,y+1).revealed and grid.get_cell(x+1,y+1).revealed and grid.get_cell(x,y+1).revealed):
                #skip previously handled instances
                if(grid.get_cell(x-1,y-1).flagged):
                  continue
                #flag and reveal
                grid.get_cell(x-1,y-1).flag()
                grid.get_cell(x+1,y-1).flag()
                logic.reveal_cell(x,y-1)
                done=False
        if(y>0 and y<(grid.size-1)):
          if(grid.get_cell(x,y-1).revealed and grid.get_cell(x,y-1).adjacent==1):
            if(grid.get_cell(x,y+1).revealed and grid.get_cell(x,y+1).adjacent==1):
              #branch on which side is already revealed
              if(grid.get_cell(x-1,y-1).revealed and grid.get_cell(x-1,y+1).revealed and grid.get_cell(x-1,y).revealed):
                #skip previously handled instances
                if(grid.get_cell(x+1,y+1).flagged):
                  continue
                #flag and reveal
                grid.get_cell(x+1,y+1).flag()
                grid.get_cell(x+1,y-1).flag()
                logic.reveal_cell(x+1,y)
                done=False
              elif(grid.get_cell(x+1,y-1).revealed and grid.get_cell(x+1,y+1).revealed and grid.get_cell(x+1,y).revealed):
                #skip previously handled instances
                if(grid.get_cell(x-1,y-1).flagged):
                  continue
                #flag and reveal
                grid.get_cell(x-1,y-1).flag()
                grid.get_cell(x-1,y+1).flag()
                logic.reveal_cell(x-1,y)
                done=False
  medium_solve() #TODO whoever implements medium_solve() please make sure this has the right parameters