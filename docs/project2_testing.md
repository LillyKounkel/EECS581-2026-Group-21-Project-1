# Project 2 regression record

Author: Han Zheng. Date: 2026-10-11.
Purpose: reproducible checks and remaining submission items.
Inputs: current source, fixed board/clock fixtures and scripted UI input.
Outputs: unittest results, syntax checks and actual Raylib framebuffer captures.
External source: OpenAI Codex assisted test design, execution and documentation.

## Environment and commands

Tested locally on Windows with Python 3.12 and the repository's unchanged
`requirements.txt` (`raylib==6.0.1.0`). Created `.venv`, installed requirements,
and launched the documented `python src/main.py`; the real window, OpenGL,
font and existing title image initialized successfully.

From the repository root, with that environment activated:

```sh
python -m unittest discover -s tests -v
python -m compileall -q src tests
python tests/ui_smoke.py
git -c core.whitespace=cr-at-eol diff --check
```

The whitespace check allows inherited Windows CRLF line endings without
reformatting unrelated source. The GUI smoke test needs a desktop with OpenGL.
It runs the real main loop/renderer and game handlers with scripted input,
seeded mine placement, a safe-choice oracle for GUI progression, and a zero-mine
victory fixture. These fixtures are test-only; production Easy still chooses
randomly without looking at hidden mines. It does not send desktop input events.

## Results

- **25 unittest methods passed**, including parameterized orientations/edges.
- **Syntax/compile checks passed** for all `src/` and `tests/` Python files.
- **Real GUI smoke passed**, exported 13 actual Raylib screenshots and closed
  cleanly. Menu, playing board, loss and victory captures were visually inspected;
  status, timer, AI controls, labels and reset/menu controls fit the window.
- **Whitespace/diff inspection passed** with inherited CRLF respected.

| Required behavior | Verification |
|---|---|
| Menu/board launches and resource loading | Real normal launch and GUI smoke |
| Correct unique mine count; safe first valid click/3x3 area | Seeded logic test and real GUI first-AI assertion |
| Flagged first click does not consume safe placement or start time | Board mouse-handler test and real GUI assertions |
| Duplicate mine placement does not occur | Same-game second placement leaves exact mine locations unchanged |
| Flag/unflag; no flagging revealed cells | Mouse-handler and Cell tests, real GUI flag/unflag |
| Recursive zero reveal; flags remain covered | Logic test, zero-mine GUI victory fixture |
| Win/loss; reveal mines on loss; ended game rejects AI | Board tests and real GUI victory/loss captures |
| Reset; return to menu; new game; preserve AI level on Reset | Actual main-loop test and real GUI assertions |
| Easy legal random selection/no legal move | Patched random-choice assertion, exact one-cell test |
| Medium Rules 1/2, zero clue and Easy fallback | Fixed visible-state tests; preserves flags/stops on loss |
| Hard horizontal/vertical, both sides, all four edges | Fixed 1-2-1 tests and parameterized subtests |
| Hard rejects open-sided/flagged-center/exterior patterns | Fallback assertions, no flag toggling |
| Hard falls back to Medium | Actual Medium flag inference test |
| No out-of-bounds crashes | Sizes 1/2/3/5 and edge-pattern tests |
| No flagged-cell reveals, current board before/after first reveal | All-difficulty Board tests and real GUI same-board assertion |
| Buttons and 1/2/3/A controls | Handler tests and real GUI scripted actions |
| Timer idle/start/running/freeze/reset | Injected-clock tests and real GUI freeze/reset assertions |
| Existing A-J / 1-10 labels preserved | Exact label-render arguments and visual inspection |

Screenshots are local verification output under ignored `artifacts/ui-smoke/`,
not substitutes for the automated assertions. Tests do not claim that the AI
always wins; fallback guesses or wrong player flags can lose normally.

## Submission status

The [Project 2 actual person-hours log](project2_hours_log.md) and
[task-based Project 2 estimate](project2_hours_estimate.md) are now included.
The actual log is transcribed from the authoritative supplied PDF; the estimate
uses the user-specified work items and totals 13.0 person-hours. Inherited
Project 1 hours files remain unchanged.

The audited changes in PR #2 were merged into `project2`. The `project2` branch
is the final submission branch, and no further code changes are planned before
submission.
