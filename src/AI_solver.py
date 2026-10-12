"""Visible-state Minesweeper AI. Original authors: Mason (Easy), Sione
(Medium/neighbors), Austin (Hard). Modifier: Han Zheng, 2026-10-11.
Input: active Logic. Output: True if a move was made, otherwise False.
External source: OpenAI Codex assisted with maintenance and tests.
"""
import random


def get_neighbors(row, col, size):
    return [(r, c) for r in range(max(0, row - 1), min(size, row + 2))
            for c in range(max(0, col - 1), min(size, col + 2))
            if (r, c) != (row, col)]


def easy_solve(logic):
    """Randomly reveal one covered, unflagged cell on this board."""
    if logic.game_over:
        return False
    available = [(r, c) for r in range(logic.grid.size)
                 for c in range(logic.grid.size)
                 if not logic.grid.is_revealed(r, c)
                 and not logic.grid.is_flagged(r, c)]
    if not available:
        return False
    logic.reveal_cell(*random.choice(available))
    return True


def medium_solve(logic):
    """Apply one local deduction (possibly several cells), otherwise Easy."""
    if logic.game_over:
        return False
    grid = logic.grid
    for row in range(grid.size):
        for col in range(grid.size):
            cell = grid.get_cell(row, col)
            if not cell.revealed or cell.mine:
                continue
            hidden = [p for p in get_neighbors(row, col, grid.size)
                      if not grid.is_revealed(*p)]
            flagged = [p for p in hidden if grid.is_flagged(*p)]
            unflagged = [p for p in hidden if not grid.is_flagged(*p)]
            if unflagged and len(hidden) == cell.adjacent:
                for p in unflagged:
                    grid.get_cell(*p).flag()
                return True
            if unflagged and len(flagged) == cell.adjacent:
                for p in unflagged:
                    if logic.game_over:
                        break
                    logic.reveal_cell(*p)
                return True
    return easy_solve(logic)


def hard_solve(logic):
    """Apply a bounded horizontal/vertical 1-2-1, otherwise Medium.

    The middle clue must see exactly the three covered cells on one side.
    End clues may also see the next cell along that same covered strip,
    but no other hidden cells. This closes the opposite side and avoids
    unsound inference from an open-sided 1-2-1. Existing flags never toggle.
    """
    if logic.game_over:
        return False
    grid = logic.grid

    def inside(p):
        return 0 <= p[0] < grid.size and 0 <= p[1] < grid.size

    for row in range(grid.size):
        for col in range(grid.size):
            for dr, dc in ((0, 1), (1, 0)):
                clues = [(row - dr, col - dc), (row, col),
                         (row + dr, col + dc)]
                if not all(inside(p) for p in clues):
                    continue
                if not all(grid.is_revealed(*p) and not grid.is_mine(*p)
                           and grid.adjacent_mines(*p) == n
                           for p, n in zip(clues, (1, 2, 1))):
                    continue
                for sign in (-1, 1):
                    sr, sc = sign * dc, sign * dr
                    targets = [(r + sr, c + sc) for r, c in clues]
                    if not all(inside(p) and not grid.is_revealed(*p)
                               for p in targets):
                        continue
                    first, middle, last = targets
                    if grid.is_flagged(*middle):
                        continue
                    before = (first[0] - dr, first[1] - dc)
                    after = (last[0] + dr, last[1] + dc)
                    hidden = [{p for p in get_neighbors(*clue, grid.size)
                               if not grid.is_revealed(*p)} for clue in clues]
                    if (hidden[1] != set(targets) or
                            not hidden[0] <= {before, first, middle} or
                            not hidden[2] <= {middle, last, after}):
                        continue
                    exterior = (hidden[0] | hidden[2]) - set(targets)
                    if any(grid.is_flagged(*p) for p in exterior):
                        continue
                    for p in (first, last):
                        if not grid.is_flagged(*p):
                            grid.get_cell(*p).flag()
                    logic.reveal_cell(*middle)
                    return True
    return medium_solve(logic)


SOLVERS = {"Easy": easy_solve, "Medium": medium_solve, "Hard": hard_solve}
