# Architecture Breakdown

### Goal: Discuss the purpose of each file, class, and associated functions to clarify how the program works
---

## main.py
* main - The entry point of the program. Handles resources and moving between the menu and game states.
* draw_background - This draws at the start of every frame to ensure old frames don't bleed into the next.
  
## board.py
* Board Class
The Board class draws the 10 by 10 Minesweeper grid and the top status bar, and reads mouse input each frame to update the game through the Logic class.
    * render - Called once per frame. Handles input, then draws the status bar, the grid, and the row/column labels, in that order.
    * _cell_at - Converts a screen pixel position (such as the mouse position) into a (row, column) grid coordinate, or returns None if the position falls outside the grid.
    * _handle_input - Reads the mouse each frame. A left click reveals a cell (placing mines first if it's the very first click of the game, so that click is always safe) and checks for a win or loss afterward. A right click toggles a flag on a covered cell.
    * _reveal_all_mines - After a loss, marks every mine cell as revealed so the player can see where all the mines were.
    * _draw_status_bar - Draws the black top bar showing mines/flags remaining (via the Grid class's render_status), plus centered text showing whether the game is Playing, a Victory, or a Loss.
    * _draw_grid - Draws all 100 cells based on their current state: covered cells (highlighted on hover, with an "F" if flagged) or revealed cells (blank, a colored adjacent-mine number, or a mine).
    * _draw_labels - Draws the A-J column letters above the grid and the 1-10 row numbers to its left, centered against each corresponding column and row.

## grid.py
* Cell Class  
The Cell class will hold the information for a given square in the Minesweeper board. This information includes if the cell is flagged, if the cell has a mine, if the cell has been revealed to the player, and how many mines are adjacent to the cell.
    * reveal - If the cell has not been flagged, it will be revealed to the player
    * flag - If the cell has not been revealed, the flagged property will be toggled, so the player can flag and unflag cells.
  
* Grid Class
The Grid class will create a 10 by 10 grid of cells, that can be used to render the board to screen and organize the board data.
    * _cell_at - When given a row and column, this private function will retrieve the Cell at the given location. It will throw an index error if the cell is unreachable.
    * get_cell - The public method that other classes will use to get information at a particular point, by giving it a row and column within the Grid.
    * is_mine - This checks if the Cell at the given row and column inputs is a mine.
    * is_flagged - This checks if the Cell at the given row and column inputs has been flagged.
    * is_revealed - This checks if the Cell at the given row and column inputs has been revealed by the player.
    * adjacent_mines - When given a specific row and column, it returns the number of adjacent mines to that Cell.
    * render_status - This renders the status bar on the top left of the screen. For now, it just shows the remaining number of mines, which is calculated by taking the number of mines and subtracting the number of flagged Cells from it

## minesweeper_logic.py
* Logic Class  
  * place_mines - When the first cell is clicked to start the game, this function randomly places mines on the grid, excluding whichever cell was clicked and it's adjacent cells.
  * calc_adjacency - Counts the mines adjacent to any non-mine cell and stores the count on the cell.
  * reveal_cell - Reveals a cell. If the cell is a mine, it ends the game. If the cell has zero adjacent mines, it reveals all surrounding cells.
  * recursive_reveal - Continuously recalls the reveal_cell function if the conditions are right.
  * check_win - Ends the game with a victory if every non-mine cell is revealed.
  * loss - Ends the game in a loss if any mine cell is revealed.

## menu.py
* Menu class
Stores options to set up the game with (currently just mine count). Renders the title screen and input elements to edit options with.
    * render - Draws and handles input for the menu screen in the current frame.
    
* Slider class
Stores one numeric value and draws a slider widget to edit it with.
     * render - Draws the slider to the screen and tracks when it is hovered over. Also calls _handle_mouse_input.
     * _handle_mouse_input - Watches mouse input whenever the slider is being hovered. Watches for clicks to grab the slider, and moves with the cursor while grabbed.

* button - A standalone function to render a button widget. Draws the button and returns True if the area drawn to is clicked.


## Project 2 extension

<!-- Modifier: Han Zheng, 2026-10-11. Purpose: link the current architecture.
External source: OpenAI Codex assisted this addition; Project 1 content retained. -->

The inherited description above records Project 1. In Project 2, mine placement
is deferred in `Logic.reveal_cell` after revealed/flagged/game-over guards, so
manual and AI reveals share first-move protection. `Board` adds difficulty/move
controls and a `GameTimer`, synchronizes victory/loss after either kind of move,
and retains the original coordinate labels. `main.py` retains menu/reset flow.

See [Project 2 design and diagrams](project2.md) for the current relationships.
