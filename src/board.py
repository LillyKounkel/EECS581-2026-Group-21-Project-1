'''
Authors: Sakthivel Sivasubramanian, Anthony Tran
Last Modified: 10.07.26
Modification: Added comments; added A-J column and 1-10 row coordinate labels
Modifier: Han Zheng - preserve safe first reveal when clicking flagged cells
Purpose: This module defines the Board class, which draws the 10 x 10 Minesweeper grid nad the top status bar.
        It reads the mouse each frame (left click reveals, right click flags) and uses the Logic class to track the game
External sources: Claude (Anthropic) - column-letter loop, label layout approach, and typo
        fixes in _draw_labels. All other original code by the named authors.
        OpenAI Codex - generative AI assistance with Han Zheng's maintenance changes.
'''

import pyray as rl # pyray is the library 
from minesweeper_logic import Logic # this tracks the state of the game and ill use that 

# constants for the 10 x 10 board
_BoardRows = 10
_BoardColumns = 10
_CELL_size = 32  # was 36; shrunk to make room for the label gutter
_Cell_Padding = 2 # gap between cells 
_Top_Space = 60  # this is reserved aboce the grid to show status text 

_LABEL_GUTTER = 24
_LABEL_FONT_SIZE = 18
_LABEL_PAD = 6  # gap between the row numbers and the grid
_LABEL_COLOR = rl.RAYWHITE

# colors 
_NUMBER_COLORS = {
    1: rl.BLUE, # 1 = blue ... 
    2: rl.DARKGREEN,
    3: rl.RED,
    4: rl.DARKBLUE,
    5: rl.MAROON,
    6: rl.SKYBLUE,
    7: rl.BLACK,
    8: rl.LIME,
}

CoveredColor = rl.ORANGE # color for covered cell 
CoveredColorClick = rl.LIME 
UncoveredColor = rl.RAYWHITE
FlagColor= rl.RED
MineColor = rl.BLACK
GridLineColors = rl.VIOLET 


class Board:  # this is for the board instances and renders input for the active game screen
    def __init__(self, font, mine_count): # font ic created 
        self.font = font
        self.logic = Logic(mine_count)  # the game-state engine this board visualizes based on gaven's code 
        self.mine_count = mine_count
        self.first_click = True # tracks if the first click was placed 
        self.win = False # win = all safe cells are revealed 

        grid_width = _BoardColumns * _CELL_size
        self.origin_x = (rl.get_screen_width() - grid_width) // 2 # splits the screen width evenly on both sides centers the grid horizontally
        self.origin_y = _Top_Space + _LABEL_GUTTER # grid starts below the top bar plus the gutter that holds the column letters

    # this shows the board 
    def render(self):
        self._handle_input() # checks for clicks
        self._draw_status_bar() # this is between playing, victory, and loss
        self._draw_grid() 
        self._draw_labels()

    # converts a screen  position into (row, column) or none if outside the grid
    def _cell_at(self, x, y):
        column = (x - self.origin_x) // _CELL_size
        row = (y - self.origin_y) // _CELL_size
        if 0 <= row < _BoardRows  and 0 <= column < _BoardColumns:  # this check positions left of or above the grid that would give negative numbers
            return int(row), int(column)
        return None
    # this reads the mouse every frame and updates the states 
    def _handle_input(self): 
        if self.logic.game_over or self.win: # when you win -> the game will not check your mouse clicks 
            return  # ignore clicks once the game has ended

        mouse_pos = rl.get_mouse_position()
        target = self._cell_at(mouse_pos.x, mouse_pos.y)
        if target is None:
            return  # the mouse is outside the grid, so there is nothing to do
        row, column = target

        if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):
            cell = self.logic.grid.get_cell(row, column)
            if cell.flagged or cell.revealed:
                return
            if self.first_click:
                # first click is guaranteed safe
                self.logic.place_mines(row, column)
                self.first_click = False
            self.logic.reveal_cell(row, column) 
            # after every reveal, check whether the game has ended
            if self.logic.game_over: 
                self._reveal_all_mines()  # loss: show where all the mines were
            elif self.logic.check_win():
                self.win = True  # win: every safe cell is revealed

        elif rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_RIGHT):
            # flagging is allowed even before the first reveal
            self.logic.grid.get_cell(row, column).flag() 

    def _reveal_all_mines(self): # reveals every mine on the board after a loss.
        for row in self.logic.grid.cells:
            for cell in row:
                if cell.mine:
                    cell.revealed = True

    def _draw_status_bar(self): # Draws the black top bar with the mine and flag counts, and the game status
        self.logic.grid.render_status(
            self.font,
            self.mine_count,
            0,
            0,
            rl.get_screen_width(),
            _Top_Space,
        )
        # pick the status text 
        if self.win:
            status = "Victory"
        elif self.logic.game_over:
            status = "Game Over - Loss"
        else:
            status = "Playing"
        #Centers horizontally
        status_size = rl.measure_text_ex(self.font, status, 28, 2)
        status_x = (rl.get_screen_width() - status_size.x) // 2
        rl.draw_text_ex(self.font, status, [status_x, 12], 28, 2, rl.WHITE)

    def _draw_grid(self): # draws every cell, covered cells show an F if flagged, revealed cells show a blank square, a mine number, or a mine.
        mouse_pos = rl.get_mouse_position()
        hovered = self._cell_at(mouse_pos.x, mouse_pos.y)  
        # loop through every cell and draw it based on its state
        for row in range(_BoardRows ):
            for column in range(_BoardColumns):
                cell = self.logic.grid.get_cell(row, column)
                # top-left pixel position of this cell
                x = self.origin_x + column * _CELL_size
                y = self.origin_y + row * _CELL_size
                rect = rl.Rectangle(x, y, _CELL_size - _Cell_Padding, _CELL_size - _Cell_Padding)

                if cell.revealed:
                    rl.draw_rectangle_rec(rect, UncoveredColor)
                    # draw the mine as a black circle in the middle of the cell
                    if cell.mine:
                        center_x = x + _CELL_size // 2
                        center_y = y + _CELL_size // 2
                        rl.draw_circle(int(center_x), int(center_y), _CELL_size * 0.25, MineColor)
                    # draw the adjacent mine count colored by its value
                    elif cell.adjacent > 0:
                        number = str(cell.adjacent)
                        color = _NUMBER_COLORS.get(cell.adjacent, rl.BLACK)
                        text_size = rl.measure_text_ex(self.font, number, 22, 1)
                        text_x = x + (_CELL_size - text_size.x) // 2
                        text_y = y + (_CELL_size - text_size.y) // 2
                        rl.draw_text_ex(self.font, number, [text_x, text_y], 22, 1, color)
                    # adjacent == 0 and not a mine: leave the cell blank, per spec

                else:
                    # covered cells change color when the mouse is over them
                    is_hovered = hovered == (row, column)
                    rl.draw_rectangle_rec(rect, CoveredColorClick if is_hovered else CoveredColor)
                    if cell.flagged:
                        # draw an F centered on flagged cells
                        flag_size = rl.measure_text_ex(self.font, "F", 20, 1)
                        flag_x = x + (_CELL_size - flag_size.x) // 2
                        flag_y = y + (_CELL_size - flag_size.y) // 2
                        rl.draw_text_ex(self.font, "F", [flag_x, flag_y], 20, 1, FlagColor)
                # outline every cell
                rl.draw_rectangle_lines_ex(rect, 1, GridLineColors)
    
    def _draw_labels(self):
        #For the column letters, A-J, above the each column, centered.
        for column in range (_BoardColumns):
            letter = chr(ord('A')+ column)
            size = rl.measure_text_ex(self.font, letter, _LABEL_FONT_SIZE, 1)
            cell_x = self.origin_x + column * _CELL_size
            label_x = cell_x + (_CELL_size - size.x) //2
            label_y = self.origin_y - _LABEL_GUTTER + (_LABEL_GUTTER - size.y) //2
            rl.draw_text_ex(self.font, letter, [label_x, label_y], 
                            _LABEL_FONT_SIZE,1, _LABEL_COLOR)
        #For row numbers 1-10, centered to the right of each row
        for row in range (_BoardRows):
            number = str(row + 1)
            size= rl.measure_text_ex(self.font, number, _LABEL_FONT_SIZE, 1)
            cell_y = self.origin_y + row * _CELL_size
            label_y = cell_y + (_CELL_size - size.y)//2 
            label_x = self.origin_x - _LABEL_PAD - size.x
            rl.draw_text_ex(self.font, number, [label_x, label_y],
                            _LABEL_FONT_SIZE, 1, _LABEL_COLOR)
