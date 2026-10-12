"""Author: Han Zheng, 2026-10-11; OpenAI Codex assisted implementation.
Purpose: regression of the real main loop, renderer, AI controls and game endings.
Inputs: scripted input, seeded placement, safe-choice/zero-mine test fixtures.
Outputs: assertions and actual Raylib framebuffer screenshots in artifacts/ui-smoke.
No production changes or desktop mouse/keyboard events are made by this harness.
"""
import sys
import time
import random
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts' / 'ui-smoke'
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / 'src'))
import main
from board import Board

rl = main.rl
frame = 0
current = None
seen = []
click = None
keys = set()
snapshots = {}
frozen = None
original_end = rl.end_drawing


def make_board(*args):
    global current
    current = Board(*args)
    seen.append(current)
    return current


def cell_position(row, col):
    return (current.origin_x + col * 32 + 5,
            current.origin_y + row * 32 + 5)


def should_close():
    global frame, click, keys, frozen
    frame += 1
    click = None
    keys = set()
    left = rl.MouseButton.MOUSE_BUTTON_LEFT
    right = rl.MouseButton.MOUSE_BUTTON_RIGHT
    if frame == 2:
        click = (480, 174, left)
    elif frame == 4:
        click = (*cell_position(4, 4), right)
    elif frame == 5:
        click = (*cell_position(4, 4), left)
    elif frame == 6:
        assert current.first_click and not current.logic.mines_placed
        assert current.timer.elapsed == 0
        click = (*cell_position(4, 4), right)
    elif frame == 7:
        click = (250, 76, left)  # Hard button.
    elif frame == 8:
        click = (390, 76, left)  # AI Move button, before any human reveal.
    elif frame == 9:
        assert current.ai_difficulty == 'Hard'
        assert current.logic.mines_placed and not current.first_click
        assert sum(c.mine for row in current.logic.grid.cells for c in row) == 15
        assert not current.logic.game_over
    elif frame in (12, 14, 16):
        level = {12: rl.KeyboardKey.KEY_ONE, 14: rl.KeyboardKey.KEY_TWO,
                 16: rl.KeyboardKey.KEY_THREE}[frame]
        keys = {level, rl.KeyboardKey.KEY_A}
    elif frame == 18:
        # Manual input after AI: choose a covered safe cell as a test oracle.
        safe = [(r, c) for r in range(10) for c in range(10)
                if not current.logic.grid.is_mine(r, c)
                and not current.logic.grid.is_revealed(r, c)]
        if safe:
            click = (*cell_position(*safe[0]), left)
    elif frame == 20:
        assert len(seen) == 1  # Every AI difficulty used the same board.
        mine = next((r, c) for r in range(10) for c in range(10)
                    if current.logic.grid.is_mine(r, c))
        current.logic.grid.get_cell(*mine).flagged = False
        click = (*cell_position(*mine), left)
    elif frame == 21:
        assert current.logic.game_over and not current.win
        frozen = current.timer.elapsed
    elif frame == 24:
        assert current.timer.elapsed == frozen
        click = (480, 530, left)  # Reset after loss.
    elif frame == 25:
        assert len(seen) == 2 and current.first_click
        assert current.timer.elapsed == 0 and current.ai_difficulty == 'Hard'
        # Deterministic zero-mine fixture exercises the actual victory renderer.
        current.logic.mine_count = current.mine_count = 0
        click = (*cell_position(4, 4), left)
    elif frame == 26:
        assert current.win and current.logic.game_over
        frozen = current.timer.elapsed
    elif frame == 29:
        assert current.timer.elapsed == frozen
        click = (155, 530, left)  # Return to menu after victory.
    elif frame == 31:
        click = (480, 174, left)
    elif frame == 32:
        assert len(seen) == 3 and current.first_click
        assert current.mine_count == 15 and current.timer.elapsed == 0
    return frame > 33


def end_drawing():
    original_end()
    names = {1: 'menu', 3: 'new-board', 5: 'flagged-first-click',
             10: 'hard-first-ai', 13: 'easy-ai', 15: 'medium-ai',
             21: 'loss', 23: 'loss-frozen', 24: 'reset', 26: 'victory',
             28: 'victory-frozen', 30: 'return-menu', 33: 'new-game'}
    if frame in names:
        path = OUT / (names[frame] + '.png')
        rl.take_screenshot("artifacts/ui-smoke/" + path.name)
        snapshots[names[frame]] = str(path)
    time.sleep(0.1)


def safe_choice(options):
    # Fixed oracle for GUI smoke only; production Easy remains random.
    safe = [p for p in options if not current.logic.grid.is_mine(*p)]
    return safe[len(safe) // 2]


random.seed(581)
with patch.object(main, 'Board', side_effect=make_board), \
        patch.object(rl, 'window_should_close', side_effect=should_close), \
        patch.object(rl, 'get_mouse_position', side_effect=lambda: rl.Vector2(*(click[:2] if click else (-10, -10)))), \
        patch.object(rl, 'is_mouse_button_pressed', side_effect=lambda button: bool(click and click[2] == button)), \
        patch.object(rl, 'is_mouse_button_up', return_value=True), \
        patch.object(rl, 'is_key_pressed', side_effect=lambda key: key in keys), \
        patch.object(rl, 'end_drawing', side_effect=end_drawing), \
        patch.object(random, 'choice', side_effect=safe_choice):
    main.main()
print('REAL RENDER SMOKE PASS:', len(snapshots), 'screens; menu, manual flags, three AI levels, loss, victory, timer freeze, reset, return and new game.')
