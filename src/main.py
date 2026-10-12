'''
Author: Gaven Behrends
Last Modified: 10.11.26
Modifier: Han Zheng - room for AI controls; preserve chosen AI level on reset.
Inputs/outputs: menu/board events control the window and current game session.
External sources: ChatGPT title image; OpenAI Codex maintenance assistance.
Modification: Add reset buttons to ended games, added comments
Purpose: Entry point of Minesweeper. Creates a window and runs the loop that switches between options menu and the game
        One a game has ended, shows Go to Menu and Reset Buttons 
'''

import pyray as rl
from menu import Menu, button
from board import Board


def main(): # Sets up the window and then runs the main loop until the window is closed. Each frame it draws either the menu or the board, and shows the reset buttons once the game has ended.
    rl.set_config_flags(rl.ConfigFlags.FLAG_MSAA_4X_HINT 
                        | rl.ConfigFlags.FLAG_VSYNC_HINT)
    rl.init_window(640, 560, "Minesweeper")
    rl.set_target_fps(60)

    font = rl.get_font_default()
    # Forgive me for this silliness courtesy of ChatGPT
    cover_image = rl.load_texture("assets/chatgpt_rat.png")
    menu = Menu(font, cover_image)
    board = None # only creates when the player starts the game
    in_game = False # False when still in the menu, True when the game is running
    # main loop: runs once per frame until the window is closed
    while not rl.window_should_close():
        # Reset the cursor each frame, so rendering code can set it per-frame
        rl.set_mouse_cursor(rl.MouseCursor.MOUSE_CURSOR_DEFAULT)

        rl.begin_drawing()
        draw_background()

        if not in_game:
            # menu.render returns True when the game is ready to start
            start_clicked = menu.render()
            if start_clicked:
                # the board is created with mine count the slider is set to
                board = Board(font, menu.mines_slider.value)
                in_game = True
        else:
            assert board is not None
            # board.render() handles game logic and draws the frame
            board.render()
            # allow the player to reset
            if board.logic.game_over:
                # the buttons are at the bottom of the window
                button_width = (rl.get_screen_width() - 60) // 2
                menu_rect = rl.Rectangle(20, rl.get_screen_height() - 50, 
                                         button_width, 40)
                reset_rect = rl.Rectangle(40 + button_width,
                                          rl.get_screen_height() - 50,
                                          button_width, 40)
                # it's not possible for both buttons to be clicked at once,
                # so there is no `elif` here to prevent graphical jank
                if button(menu_rect, "Go to Menu", font):
                    # clearing the board means a new one is created the next time Start Game is clicked
                    in_game = False
                    board = None
                if button(reset_rect, "Reset", font):
                    # a new Board starts a fresh game with the same mine count
                    difficulty = board.ai_difficulty
                    board = Board(font, menu.mines_slider.value)
                    board.ai_difficulty = difficulty

        rl.end_drawing()

    rl.unload_texture(cover_image)
    rl.unload_font(font)
    rl.close_window()


from math import sin


# Draw a subtle animated gradient background
def draw_background():
    t = (sin(rl.get_time()) + 1) / 2
    rl.draw_rectangle_gradient_v(0, 0, rl.get_screen_width(), rl.get_screen_height(),
                                 [0,0,56,255],
                                 rl.color_lerp([0,0,12,255],[0,0,30,255],t))


if __name__ == "__main__":
    main()
