'''
Author: Gaven Behrends
Last Modified: 10.11.26
Modification: Abstract start button into a standalone function so main can use it.
              Also improved comments
              Han Zheng - clarified file documentation only.
Purpose: This module defines the Menu and Slider classes and the button helper function. The Menu draws the options panel where the number of mines is set and the game is started.
        The slider is used to change the mine count, while the button is used for the game start button and used in main.py for the end of game buttons
Inputs: mouse input, mine-count slider state, font and optional cover image.
Outputs: updated menu/slider state and whether Start Game was clicked.
External sources: None documented.
'''

import pyray as rl

# Local constants
_MINIMUM_MINES = 10
_MAXIMUM_MINES = 20
_DEFAULT_MINES = 15
_SLIDER_HEIGHT = 8

# This class manages configuration state before a game has started, and
# renders an interface for changing settings. Currently only mine count.
class Menu:
    # sets the default mine count, creates the mines slider with its minimum, maximum, and default values, and stores the font.
    def __init__(self, font, cover_image=None):
        self.selected_mine_count = 15
        self.mines_slider = Slider("Mines:",
                _DEFAULT_MINES, _MINIMUM_MINES, _MAXIMUM_MINES)
        self.font = font
        self.cover_image = cover_image

    # draws the options panel, title, mines slider, and Start Game button. Returns True on the frame the Start Game button is clicked.
    def render(self):
        screen_width = rl.get_screen_width()
        screen_height = rl.get_screen_height()

        # Draw humorous image
        if self.cover_image is not None:
            image_size = screen_height
            image_src = rl.Rectangle(0, 0, self.cover_image.width, self.cover_image.height)
            image_rect = rl.Rectangle(-50, 0, image_size, image_size)
            rl.draw_texture_pro(self.cover_image, image_src, image_rect,
                                [0,0], 0, rl.WHITE)
        # Draw the game title
        rl.draw_text_ex(self.font, "Minesweeper", [20, 20],
                        40, 2, rl.RAYWHITE)

        # Determine the portion of the screen the menu should use
        panel_rect = rl.Rectangle(
            screen_width // 2 + 4,
            4,
            screen_width // 2 - 8,
            screen_height - 8,
        )
        rl.draw_rectangle_rec(panel_rect, [0,0,0,240])

        # Draw the menu title
        title = "Options"
        title_size = rl.measure_text_ex(self.font, title, 30, 2) 
        title_x = panel_rect.x + (panel_rect.width - title_size.x) // 2 # centers the title
        rl.draw_text_ex(self.font, title, [title_x, panel_rect.y + 8],
                        30, 2, rl.WHITE)

        # Include the mine count slider
        self.mines_slider.x = int(panel_rect.x + 16)
        self.mines_slider.y = int(panel_rect.y + 60 + title_size.y)
        self.mines_slider.width = int(panel_rect.width - 32)
        self.mines_slider.render(self.font)

        # Include a start button and return its status so the game knows when to start
        button_rect = rl.Rectangle(
            panel_rect.x + 16,
            self.mines_slider.y + 60,
            panel_rect.width - 32,
            40,
        )
        return button(button_rect, "Start Game", self.font)


# This class stores one numeric value and draws a slider widget to edit it
class Slider():
    def __init__(self, label, initial, minimum, maximum, step=1.0): # stores the slider's label, current value, range, step size, its position, and hover/grab state.
        self.label = label
        self.value = initial
        self.x = 0
        self.y = 0
        self.width = 100
        self.minimum = minimum
        self.maximum = maximum
        self._step = step
        self._hovered = False
        self._grabbed = False

    # Draw the slider, and also initiate hovers
    def render(self, font):
        # Compute position and bounds of slider components
        slider_position = self.value - self.minimum
        slider_size = self.maximum - self.minimum
        slider_ratio = slider_position / slider_size
        offset = slider_ratio * self.width

        # Draw empty slider
        rl.draw_rectangle_rounded(
                rl.Rectangle(self.x, self.y, self.width, _SLIDER_HEIGHT), 
                1.0, 32, rl.LIGHTGRAY)
        # Draw the filled portion of the slider
        rl.draw_rectangle_rounded(
                rl.Rectangle(self.x, self.y, offset, _SLIDER_HEIGHT),
                1.0, 32, rl.DARKBLUE)

        # Compute handle position
        handle_radius = _SLIDER_HEIGHT * 1.2
        handle_y = int(self.y + _SLIDER_HEIGHT / 2)

        # Detect hovering state and draw handle
        self._hovered = rl.check_collision_point_circle(
                rl.get_mouse_position(), [self.x + offset, handle_y], handle_radius)
        rl.draw_circle(
                int(self.x + self.width * slider_ratio),
                handle_y, handle_radius, rl.RAYWHITE)
        rl.draw_circle(
                int(self.x + self.width * slider_ratio),
                handle_y, handle_radius * 0.8,
                rl.GRAY if self._hovered or self._grabbed else rl.DARKGRAY)

        # Run input handling here
        self._handle_mouse_input()
        
        # Draw the label, if applicable
        if len(self.label) != 0:
            label_str = self.label + " " + str(self.value)
            label_size = rl.measure_text_ex(font, label_str, 20, 2)
            rl.draw_text_ex(font, label_str, [self.x, self.y - label_size.y - 4],
                            20, 2, rl.WHITE)

    # Update according to mouse input
    def _handle_mouse_input(self):
        mb = rl.MouseButton.MOUSE_BUTTON_LEFT

        # Releasing the mouse button ceases grabbing
        if rl.is_mouse_button_up(mb):
            self._grabbed = False

        # Start grabbing when clicking the handle
        elif self._hovered and rl.is_mouse_button_pressed(mb):
            self._grabbed = True
        
        if self._grabbed:
            rl.set_mouse_cursor(rl.MouseCursor.MOUSE_CURSOR_RESIZE_EW)
            
            # The slider will attempt to match the mouse x while grabbed
            target_x = rl.get_mouse_x()

            # Full slider case
            if target_x >= self.x + self.width:
                self.value = self.maximum
                return
            # Empty slider case
            if target_x < self.x:
                self.value = self.minimum
                return
            # Otherwise, compute the value based on position
            percentage = (target_x - self.x) / self.width
            target_value = percentage * (self.maximum - self.minimum) + self.minimum
            self.value = int(round(target_value / self._step) * self._step)
        elif self._hovered:
            rl.set_mouse_cursor(rl.MouseCursor.MOUSE_CURSOR_POINTING_HAND)


# This function draws a button and returns True if it's been clicked.
def button(rectangle, label, font):
    hovered = rl.check_collision_point_rec(rl.get_mouse_position(), rectangle)

    rl.draw_rectangle_rec(rectangle, rl.BLUE if hovered else rl.DARKBLUE)
    label_size = rl.measure_text_ex(font, label, 20, 2)
    label_x = rectangle.x + (rectangle.width - label_size.x) // 2
    label_y = rectangle.y + (rectangle.height - label_size.y) // 2
    rl.draw_text_ex(font, label, [label_x, label_y], 20, 2, rl.WHITE)

    return hovered and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)
