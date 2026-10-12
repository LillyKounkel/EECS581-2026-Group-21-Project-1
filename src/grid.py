'''
Author: Jocelyn Miller
Last Modified: 10.11.26
Modification: Ashton - Added a flag count
              Han Zheng - clarified file documentation only.
Purpose: This module defines the Cell and Grid classes, which represent the state of a Minesweeper game board. 
Each Cell tracks whether it contains a mine, whether it has been revealed or flagged, and how many adjacent mines it has. 
The Grid class manages a 2D array of Cells and provides methods to access their status and render the game state.
Inputs: row/column coordinates, cell state changes, mine count, and render parameters.
Outputs: Cell/Grid state queries and rendered status information.
External sources: None documented.
'''

import pyray as rl


class Cell:
    def __init__(self): # Initalizes the Cell class with default values for mine, revealed, flagged, and adjacent properties
        self.mine = False
        self.revealed = False
        self.flagged = False
        self.adjacent = 0

    def reveal(self): # If the cell is not flagged, it sets the revealed property to True, indicating that the cell has been revealed in the game.
        if not self.flagged:
            self.revealed = True

    def flag(self): # If the cell is not revealed, it toggles the flagged property, allowing the player to mark or unmark the cell as potentially containing a mine.
        if not self.revealed:
            self.flagged = not self.flagged


class Grid:
    def __init__(self, size=10): #Initializes the Grid class with a specified size (defaulting to 10). It creates a 2D array of Cell objects, representing the Minesweeper game board.
        if size <= 0:
            raise ValueError("Grid size must be positive")

        self.size = size
        self.cells = [
            [Cell() for _ in range(size)]
            for _ in range(size)
        ]

    def _cell_at(self, row, col): # This private method retrieves the Cell object at the specified row and column coordinates. It raises an IndexError if the coordinates are outside the bounds of the grid.
        if not (0 <= row < self.size and 0 <= col < self.size):
            raise IndexError("Cell coordinates are outside the grid")
        return self.cells[row][col]

    def get_cell(self, row, col): # This public method provides access to the Cell object at the specified row and column coordinates by calling the private _cell_at method. It allows other parts of the program to query the state of individual cells in the grid.
        return self._cell_at(row, col)

    def is_mine(self, row, col): # This method checks whether the Cell at the specified coordinates contains a mine. It returns True if the cell has a mine, and False otherwise. It uses the private _cell_at method to access the cell.
        return self._cell_at(row, col).mine

    def is_revealed(self, row, col): # This method checks whether the Cell at the specified coordinates has been revealed. It returns True if the cell is revealed, and False otherwise.
        return self._cell_at(row, col).revealed

    def is_flagged(self, row, col): # This method checks whether the Cell at the specified coordinates has been flagged. It returns True if the cell is flagged, and False otherwise.
        return self._cell_at(row, col).flagged

    def adjacent_mines(self, row, col): # This method returns the number of adjacent mines for the Cell at the specified coordinates.
        return self._cell_at(row, col).adjacent

    def flag_count(self): #This method calculates and returns a flags placed count
        return sum(
            1
            for row in self.cells
            for cell in row
            if cell.flagged
        )

    def render_status(self, font, mine_count, x=0, y=0, width=None, height=48): # This method renders a status bar at the specified (x, y) position on the screen, displaying the number of mines left to flag. It calculates the number of flagged cells and subtracts that from the total mine count to determine how many mines are left. The status bar is drawn as a black rectangle with white text showing the remaining mines. If no width is provided, it defaults to the full screen width.
        if width is None:
            width = rl.get_screen_width()

        mines_left = mine_count - int(self.flag_count())

        rl.draw_rectangle(x, y, width, height, rl.BLACK)
        rl.draw_text(
            f"Mines left: {mines_left}",
            x + 12,
            y + 16,
            20,
            rl.WHITE,
        )

        # shows the amount of flags remaining in the status bar on the right side
        flags_text = f"Flags Placed: {self.flag_count()}"
        flags_width = rl.measure_text(flags_text, 20)
        rl.draw_text(
            flags_text,
            x + width - flags_width - 12,
            y + 16,
            20,
            rl.WHITE,
        )
