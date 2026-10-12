"""Project 2 deterministic regression tests. Author: Han Zheng, 2026-10-11.
Purpose: verify AI, existing manual play, shared board state, timer and main loop.
Inputs: fixed grids, seeded randomness and mocked input/clock. Output: unittest results.
External source: OpenAI Codex assisted with test implementation.
"""
import random
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import AI_solver as ai
import board as board_module
import main as main_module
from board import Board
from game_timer import GameTimer
from minesweeper_logic import Logic


def fixture(size=3):
    logic = Logic(0, size)
    logic.mines_placed = True
    for row in logic.grid.cells:
        for cell in row:
            cell.revealed = True
            cell.adjacent = 8  # Isolate the clue under test; prevent unrelated flood.
    return logic


def hidden(logic, *positions):
    for p in positions:
        logic.grid.get_cell(*p).revealed = False


def make_board(mines=15):
    with patch.object(board_module.rl, "get_screen_width", return_value=640):
        return Board(None, mines)


def mouse(board, row, col, right=False):
    pos = SimpleNamespace(x=board.origin_x + col * 32 + 5,
                          y=board.origin_y + row * 32 + 5)
    which = board_module.rl.MouseButton.MOUSE_BUTTON_RIGHT if right else board_module.rl.MouseButton.MOUSE_BUTTON_LEFT
    with patch.object(board_module.rl, "get_mouse_position", return_value=pos), patch.object(board_module.rl, "is_mouse_button_pressed", side_effect=lambda b: b == which):
        board._handle_input()


class SolverTests(unittest.TestCase):
    def test_easy_selects_exactly_one_legal_cell(self):
        logic = fixture()
        hidden(logic, (0, 0), (0, 1), (2, 2))
        logic.grid.get_cell(0, 0).flag()
        def choose(options):
            self.assertEqual(options, [(0, 1), (2, 2)])
            return (2, 2)
        with patch.object(ai.random, "choice", side_effect=choose):
            self.assertTrue(ai.easy_solve(logic))
        self.assertTrue(logic.grid.is_revealed(2, 2))
        self.assertFalse(logic.grid.is_revealed(0, 1))
        self.assertTrue(logic.grid.is_flagged(0, 0))

    def test_easy_no_legal_cell(self):
        logic = fixture()
        with patch.object(ai.random, "choice") as choice:
            self.assertFalse(ai.easy_solve(logic))
            choice.assert_not_called()

    def test_medium_rule_one_preserves_existing_flag(self):
        logic = fixture()
        hidden(logic, (0, 0), (0, 1))
        logic.grid.get_cell(0, 0).flag()
        logic.grid.get_cell(1, 1).adjacent = 2
        self.assertTrue(ai.medium_solve(logic))
        self.assertTrue(logic.grid.is_flagged(0, 0))
        self.assertTrue(logic.grid.is_flagged(0, 1))
        self.assertFalse(logic.grid.is_revealed(0, 1))

    def test_medium_rule_two_never_reveals_flags(self):
        logic = fixture()
        hidden(logic, (0, 0), (0, 1), (0, 2))
        logic.grid.get_cell(0, 0).flag()
        logic.grid.get_cell(1, 1).adjacent = 1
        self.assertTrue(ai.medium_solve(logic))
        self.assertFalse(logic.grid.is_revealed(0, 0))
        self.assertTrue(logic.grid.is_revealed(0, 1))
        self.assertTrue(logic.grid.is_revealed(0, 2))

    def test_medium_zero_clue(self):
        logic = fixture()
        hidden(logic, (0, 1))
        logic.grid.get_cell(1, 1).adjacent = 0
        self.assertTrue(ai.medium_solve(logic))
        self.assertTrue(logic.grid.is_revealed(0, 1))

    def test_medium_fallback(self):
        with patch.object(ai, "easy_solve", return_value=True) as easy:
            logic = fixture()
            self.assertTrue(ai.medium_solve(logic))
            easy.assert_called_once_with(logic)

    def pattern(self, center, direction, sign, size=5, exterior=False):
        logic = fixture(size)
        dr, dc = direction
        r, c = center
        clues = [(r-dr, c-dc), center, (r+dr, c+dc)]
        targets = [(x+sign*dc, y+sign*dr) for x,y in clues]
        hidden(logic, *targets)
        for p, n in zip(clues, (1, 2, 1)):
            logic.grid.get_cell(*p).adjacent = n
        logic.grid.get_cell(*targets[0]).mine = True
        logic.grid.get_cell(*targets[2]).mine = True
        if exterior:
            hidden(logic, (targets[0][0]-dr, targets[0][1]-dc),
                   (targets[2][0]+dr, targets[2][1]+dc))
        return logic, targets

    def test_hard_horizontal_vertical_both_sides(self):
        for direction in ((0,1), (1,0)):
            for sign in (-1,1):
                with self.subTest(direction=direction, sign=sign):
                    logic, targets = self.pattern((2,2), direction, sign, exterior=True)
                    logic.grid.get_cell(*targets[0]).flag()
                    with patch.object(ai, "medium_solve") as medium:
                        self.assertTrue(ai.hard_solve(logic))
                        medium.assert_not_called()
                    self.assertTrue(logic.grid.is_flagged(*targets[0]))
                    self.assertTrue(logic.grid.is_flagged(*targets[2]))
                    self.assertTrue(logic.grid.is_revealed(*targets[1]))
                    self.assertFalse(logic.game_over)

    def test_hard_all_grid_edges(self):
        for direction, center, sign in [((0,1),(0,1),1), ((0,1),(2,1),-1),
                                         ((1,0),(1,0),1), ((1,0),(1,2),-1)]:
            with self.subTest(direction=direction, center=center):
                logic, targets = self.pattern(center, direction, sign, size=3)
                self.assertTrue(ai.hard_solve(logic))
                self.assertTrue(logic.grid.is_revealed(*targets[1]))
                self.assertTrue(logic.grid.is_flagged(*targets[0]))
                self.assertTrue(logic.grid.is_flagged(*targets[2]))

    def test_hard_rejects_ambiguous_opposite_side(self):
        logic, targets = self.pattern((2,2), (0,1), 1)
        hidden(logic, (1,2))
        with patch.object(ai, "medium_solve", return_value=False) as medium:
            self.assertFalse(ai.hard_solve(logic))
            medium.assert_called_once_with(logic)
        self.assertFalse(logic.grid.is_flagged(*targets[0]))

    def test_hard_rejects_flagged_center_and_exterior(self):
        for flag in [(3,2), (3,0)]:
            logic, _ = self.pattern((2,2), (0,1), 1, exterior=True)
            logic.grid.get_cell(*flag).flag()
            with patch.object(ai, "medium_solve", return_value=False) as medium:
                ai.hard_solve(logic)
                medium.assert_called_once_with(logic)
            self.assertTrue(logic.grid.is_flagged(*flag))
            self.assertFalse(logic.grid.is_revealed(*flag))

    def test_hard_fallback_uses_medium_rule(self):
        logic = fixture()
        hidden(logic, (0,0))
        logic.grid.get_cell(1,1).adjacent = 1
        self.assertTrue(ai.hard_solve(logic))
        self.assertTrue(logic.grid.is_flagged(0,0))

    def test_small_grids_and_neighbors_never_out_of_bounds(self):
        for size in (1,2,3,5):
            for solver in ai.SOLVERS.values():
                self.assertFalse(solver(fixture(size)))
            for r in range(size):
                for c in range(size):
                    for x,y in ai.get_neighbors(r,c,size):
                        self.assertTrue(0 <= x < size and 0 <= y < size)
                        self.assertNotEqual((x,y),(r,c))

    def test_all_solvers_ignore_ended_game(self):
        for solver in ai.SOLVERS.values():
            logic = fixture()
            logic.game_over = True
            with patch.object(logic, "reveal_cell") as reveal:
                self.assertFalse(solver(logic))
                reveal.assert_not_called()

    def test_medium_stops_batch_after_loss(self):
        logic = fixture()
        hidden(logic,(0,0),(0,1),(0,2))
        logic.grid.get_cell(0,0).flag()
        logic.grid.get_cell(0,1).mine = True  # Incorrect player flag can make inference lose.
        logic.grid.get_cell(1,1).adjacent = 1
        ai.medium_solve(logic)
        self.assertTrue(logic.game_over)
        self.assertFalse(logic.grid.is_revealed(0,2))


class GameplayTests(unittest.TestCase):
    def test_first_click_safe_unique_mines_and_no_duplicate_placement(self):
        random.seed(11)
        logic = Logic(15)
        logic.reveal_cell(4,4)
        mines = {(r,c) for r in range(10) for c in range(10) if logic.grid.is_mine(r,c)}
        self.assertEqual(len(mines),15)
        self.assertTrue(logic.grid.is_revealed(4,4))
        self.assertFalse(logic.game_over)
        self.assertTrue(mines.isdisjoint({(r,c) for r in range(3,6) for c in range(3,6)}))
        logic.place_mines(9,9)
        self.assertEqual(mines,{(r,c) for r in range(10) for c in range(10) if logic.grid.is_mine(r,c)})

    def test_flagged_first_click_does_not_place_mines_or_start_timer(self):
        board = make_board()
        mouse(board,4,4,right=True)
        mouse(board,4,4)
        self.assertTrue(board.first_click)
        self.assertFalse(board.logic.mines_placed)
        self.assertEqual(board.timer.elapsed,0)
        mouse(board,4,4,right=True)
        self.assertFalse(board.logic.grid.is_flagged(4,4))
        mouse(board,4,4)
        self.assertFalse(board.first_click)
        self.assertFalse(board.logic.grid.is_mine(4,4))

    def test_flagging_revealed_cell_does_nothing(self):
        logic = fixture()
        logic.grid.get_cell(0,0).flag()
        self.assertFalse(logic.grid.is_flagged(0,0))

    def test_recursive_zero_reveal_respects_flag(self):
        logic = Logic(0,5)
        logic.grid.get_cell(4,4).flag()
        logic.reveal_cell(0,0)
        self.assertEqual(sum(c.revealed for row in logic.grid.cells for c in row),24)
        self.assertFalse(logic.grid.is_revealed(4,4))
        self.assertFalse(logic.check_win())
        logic.grid.get_cell(4,4).flag()
        logic.reveal_cell(4,4)
        self.assertTrue(logic.check_win())

    def test_ai_before_and_after_first_reveal_uses_same_board(self):
        for difficulty in ai.SOLVERS:
            with self.subTest(difficulty=difficulty):
                random.seed(31)
                board = make_board()
                board.ai_difficulty = difficulty
                grid = board.logic.grid
                grid.get_cell(0,0).flag()
                self.assertTrue(board.ai_move())
                self.assertIs(board.logic.grid,grid)
                self.assertTrue(board.logic.mines_placed)
                self.assertFalse(board.first_click)
                self.assertFalse(grid.is_revealed(0,0))
                self.assertFalse(board.logic.game_over)
                board.ai_move()
                self.assertIs(board.logic.grid,grid)
                self.assertFalse(grid.is_revealed(0,0))

    def test_keyboard_difficulty_and_ai_move(self):
        board = make_board()
        keys = board_module.rl.KeyboardKey
        with patch.object(board_module.rl,"is_key_pressed",side_effect=lambda k:k in (keys.KEY_THREE,keys.KEY_A)), patch.object(board,"ai_move",return_value=True) as move:
            board._handle_ai_input()
        self.assertEqual(board.ai_difficulty,"Hard")
        move.assert_called_once()

    def test_ai_button_and_difficulty_buttons(self):
        board = make_board()
        with patch.object(board_module,"button",side_effect=[False,True,False,True]), patch.object(board,"ai_move") as move:
            board._draw_ai_controls()
        self.assertEqual(board.ai_difficulty,"Medium")
        move.assert_called_once()

    def test_timer_start_freeze_win_loss_and_new_board(self):
        for win in (True,False):
            with self.subTest(win=win):
                now=[10.0]
                board = make_board(0)
                board.timer = GameTimer(lambda: now[0])
                if win:
                    mouse(board,0,0)
                    self.assertTrue(board.win)
                else:
                    board.logic.mines_placed=True
                    for row in board.logic.grid.cells:
                        for c in row: c.adjacent=1
                    mouse(board,0,0)
                    now[0]=15
                    board.logic.grid.get_cell(1,1).mine=True
                    mouse(board,1,1)
                    self.assertTrue(board.logic.game_over)
                    self.assertTrue(board.logic.grid.is_revealed(1,1))
                elapsed=board.timer.elapsed
                now[0]=100
                self.assertEqual(board.timer.elapsed,elapsed)
                self.assertFalse(board.ai_move())
                reset=make_board(0)
                self.assertEqual(reset.timer.elapsed,0)
                self.assertTrue(reset.first_click)

    def test_timer_running_and_reset(self):
        now=[0.0]; timer=GameTimer(lambda:now[0])
        self.assertEqual(timer.elapsed,0)
        timer.start(); now[0]=3; timer.start()
        self.assertEqual(timer.elapsed,3)
        timer.stop(); now[0]=8; timer.stop()
        self.assertEqual(timer.elapsed,3)
        timer.reset(); self.assertEqual(timer.elapsed,0)
        timer.start(); now[0]=10; self.assertEqual(timer.elapsed,2)

    def test_coordinate_labels_and_mouse_bounds_preserved(self):
        board=make_board()
        with patch.object(board_module.rl,"measure_text_ex",return_value=SimpleNamespace(x=10,y=18)), patch.object(board_module.rl,"draw_text_ex") as draw:
            board._draw_labels()
        self.assertEqual([c.args[1] for c in draw.call_args_list],list('ABCDEFGHIJ')+[str(n) for n in range(1,11)])
        self.assertIsNone(board._cell_at(board.origin_x-1,board.origin_y))
        self.assertIsNone(board._cell_at(board.origin_x,board.origin_y-1))
        self.assertEqual(board._cell_at(board.origin_x+319,board.origin_y+319),(9,9))
        self.assertIsNone(board._cell_at(board.origin_x+320,board.origin_y))

    def test_main_menu_board_loss_reset_return_and_new_game(self):
        # Run the actual main loop with only graphics/input replaced.
        rl=main_module.rl
        with patch.multiple(rl, set_config_flags=Mock(),init_window=Mock(),set_target_fps=Mock(),get_font_default=Mock(return_value=None),load_texture=Mock(return_value=None),window_should_close=Mock(side_effect=[False]*5+[True]),set_mouse_cursor=Mock(),begin_drawing=Mock(),end_drawing=Mock(),get_screen_width=Mock(return_value=640),get_screen_height=Mock(return_value=560),unload_texture=Mock(),unload_font=Mock(),close_window=Mock()), patch.object(main_module,"draw_background"), patch.object(main_module,"Menu") as menu, patch.object(main_module,"Board") as constructor, patch.object(main_module,"button",side_effect=[False,True,True,False,False,False]):
            menu.return_value.render.return_value=True
            menu.return_value.mines_slider.value=15
            boards=[Mock(),Mock(),Mock()]
            for b in boards:
                b.logic.game_over=True; b.ai_difficulty='Hard'
            constructor.side_effect=boards
            main_module.main()
            self.assertEqual(constructor.call_count,3)
            self.assertEqual(menu.return_value.render.call_count,2)
            self.assertEqual(boards[1].ai_difficulty,'Hard')
            rl.init_window.assert_called_once_with(640,560,'Minesweeper')
            rl.close_window.assert_called_once()


if __name__ == '__main__':
    unittest.main()
