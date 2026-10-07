'''
Author: Max Toney, Cooper Fish
Last Modified: 10.07.26
Modification: Gaven - changed place_mines to exclude a 3x3 area rather than one cell
Modifier: Han Zheng - prevent duplicate mine generation in the same game
Purpose: This module defines the Logic class, which tracks the state of the game. It places the mines, counts the adjacent mines for each cell, reveals cells, and checks for a win or a loss.
External sources: OpenAI Codex - generative AI assistance with Han Zheng's maintenance changes.
'''

import random
from grid import Grid

class Logic: #determines the logic of the game
    def __init__(self, mine_count, size=10): # stores the mine count, marks the game as not over, and creates the Grid of cells.
        self.mine_count = mine_count #mine counter
        self.game_over = False #status of if the game is still ongoing 
        self.grid = Grid(size)
        self.mines_placed = False
    
    def place_mines(self, safe_row=None, safe_col=None):# randomly places mines on the grid, leaving out the clicked cell and its 8 neighbors when a safe cell is given, then calculates the adjacent mine counts.
        if self.mines_placed:
            return
        all_cells = [
            (r, c)
            for r in range(self.grid.size)
            for c in range(self.grid.size)
        ] # builds list of all (r,c)
        if safe_row is not None and safe_col is not None:
            # protect the first click cell and its neighbors from being a mine
            for r in range(safe_row - 1, safe_row + 2):
                for c in range(safe_col - 1, safe_col + 2):
                    if (r, c) in all_cells:
                        all_cells.remove((r, c))

        mine_locations = random.sample(all_cells, self.mine_count) # pick unique random cells for mines
        for row, col in mine_locations:
            self.grid.get_cell(row, col).mine = True # mark that cell as a mine
        self.calc_adjacency() # calculate adjacency counts now that mines are placed
        self.mines_placed = True

    def calc_adjacency(self): # counts the mines surrounding every non-mine cell and stores the count on the cell.
        for row in range(self.grid.size):
            for col in range(self.grid.size):
                cell = self.grid.get_cell(row, col) # targets the cell we're counting for
                if cell.mine:
                    continue # mines don't need a count
                count = 0
                for row_change in [-1, 0, 1]: # scan all 8 surrounding cells
                    for col_change in [-1, 0, 1]:
                        if row_change == 0 and col_change == 0: 
                            continue # skip the cell itself
                        next_row = row + row_change # row of the neighbor being checked
                        next_col = col + col_change # col of the neighbor being checked
                        if next_row < 0 or next_row >= self.grid.size:
                            continue # stay in bounds vertically
                        if next_col < 0 or next_col >= self.grid.size:
                            continue # stay in bounds horizontally
                        if self.grid.get_cell(next_row, next_col).mine:
                            count += 1 # found a neighboring mine
                cell.adjacent = count # store the final count on the cell

    def reveal_cell(self, row, col): # reveals a cell unless already revealed or flagged. Revealing a mine ends the game, and revealing a cell with 0 adjacent mines starts revealing its neighbors.
        cell = self.grid.get_cell(row, col) #targets the cell we are revealing
        if cell.revealed: #if already revealed, return
            return
        if cell.flagged: #if flagged, don't reveal
            return
        cell.reveal() #reveals cell
        if cell.mine: #checks if the cell is a mine
            self.loss() #if it is, game over :(
            return
        if cell.adjacent == 0: #checks if revealed cell has no adjacent mines
            self.recursive_reveal(row, col) #if yes, recurse

    def recursive_reveal(self, row, col): # calls reveal_cell on all 8 neighbors of an empty cell. Since reveal_cell calls this again for every empty neighbor, the reveal spreads until it reaches cells with adjacent mines.
        for row_change in [-1, 0, 1]: #changes the row and col to focus on adjacent cells
            for col_change in [-1, 0, 1]:
                if row_change == 0 and col_change == 0: #checks if its focusing on the orignal cell
                    continue #if yes, go back
                next_row = row + row_change #initializes the next row and col of focus
                next_col = col + col_change
                if next_row < 0 or next_row >= self.grid.size: #keeps a user from revealing a cell out of bounds
                    continue
                if next_col < 0 or next_col >= self.grid.size:
                    continue
                self.reveal_cell(next_row, next_col) #runs the reveal function on the next targeted cell.

    def check_win(self): # returns True and ends the game if every safe cell has been revealed, otherwise returns False
        for row in range(self.grid.size):
            for col in range(self.grid.size):
                cell = self.grid.get_cell(row, col) # targets the cell we're checking
                if not cell.mine and not cell.revealed:
                    return False # a safe cell is still hidden
        self.game_over = True # every safe cell is revealed
        return True

    def loss(self): # game is over after a mine is revealed
        self.game_over = True #changes the game over status to true
        #might add more. reveal all mines on loss maybe?
