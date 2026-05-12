import pytest

from engine import rule_enforcer
from engine.models import StateChange, TurnResult


# ── helpers ────────────────────────────────────────────────────────────────

def _turn(changes: list[StateChange], narration: str = "ok") -> TurnResult:
    return TurnResult(narration=narration, state_changes=changes)


def _sc(**kw) -> StateChange:
    return StateChange(**kw)


# ── move_player ─────────────────────────────────────────────────────────────

def test_move_player_valid(minimal_world):
    tr = _turn([_sc(type="move_player", to_location="exit")])
    assert rule_enforcer.validate(minimal_world, tr) == []


def test_move_player_unconnected(minimal_world):
    # add a third isolated room
    from engine.models import Location
    minimal_world.locations["island"] = Location(id="island", name="I", description="d")
    tr = _turn([_sc(type="move_player", to_location="island")])
    v = rule_enforcer.validate(minimal_world, tr)
    assert v and "not connected" in v[0]


def test_move_player_unknown_location(minimal_world):
    tr = _turn([_sc(type="move_player", to_location="nowhere")])
    v = rule_enforcer.validate(minimal_world, tr)
    assert v and "unknown location" in v[0]


def test_move_player_missing_to(minimal_world):
    tr = _turn([_sc(type="move_player")])
    v = rule_enforcer.validate(minimal_world, tr)
    assert v and "missing" in v[0]


# ── take_item ───────────────────────────────────────────────────────────────

def test_take_item_valid(minimal_world):
    tr = _turn([_sc(type="take_item", item_id="notebook")])
    assert rule_enforcer.validate(minimal_world, tr) == []


def test_take_item_not_in_location(minimal_world):
    # notebook is in start; move player to exit first
    minimal_world.current_location_id = "exit"
    tr = _turn([_sc(type="take_item", item_id="notebook")])
    v = rule_enforcer.validate(minimal_world, tr)
    assert v and "not in current location" in v[0]


def test_take_item_not_takeable(minimal_world):
    minimal_world.items["notebook"].is_takeable = False
    tr = _turn([_sc(type="take_item", item_id="notebook")])
    v = rule_enforcer.validate(minimal_world, tr)
    assert v and "not takeable" in v[0]


def test_take_item_already_in_inventory(minimal_world):
    minimal_world.inventory.append("notebook")
    tr = _turn([_sc(type="take_item", item_id="notebook")])
    v = rule_enforcer.validate(minimal_world, tr)
    assert v and "already in inventory" in v[0]


def test_take_locked_item_without_key(minimal_world):
    # key requires notebook; notebook not in inventory
    tr = _turn([_sc(type="take_item", item_id="key")])
    v = rule_enforcer.validate(minimal_world, tr)
    assert v and "locked" in v[0]


def test_take_locked_item_with_key(minimal_world):
    minimal_world.inventory.append("notebook")
    tr = _turn([_sc(type="take_item", item_id="key")])
    assert rule_enforcer.validate(minimal_world, tr) == []


def test_take_item_unknown(minimal_world):
    tr = _turn([_sc(type="take_item", item_id="ghost")])
    v = rule_enforcer.validate(minimal_world, tr)
    assert v and "unknown item" in v[0]


# ── use_item ────────────────────────────────────────────────────────────────

def test_use_item_valid(minimal_world):
    minimal_world.inventory.append("notebook")
    tr = _turn([_sc(type="use_item", item_id="notebook")])
    assert rule_enforcer.validate(minimal_world, tr) == []


def test_use_item_not_in_inventory(minimal_world):
    tr = _turn([_sc(type="use_item", item_id="notebook")])
    v = rule_enforcer.validate(minimal_world, tr)
    assert v and "not in inventory" in v[0]


# ── move_item ───────────────────────────────────────────────────────────────

def test_move_item_valid(minimal_world):
    tr = _turn([_sc(type="move_item", item_id="notebook", to_location="exit")])
    assert rule_enforcer.validate(minimal_world, tr) == []


def test_move_item_invalid_dest(minimal_world):
    tr = _turn([_sc(type="move_item", item_id="notebook", to_location="void")])
    v = rule_enforcer.validate(minimal_world, tr)
    assert v and "invalid to_location" in v[0]


def test_move_item_not_in_current_location(minimal_world):
    minimal_world.current_location_id = "exit"
    tr = _turn([_sc(type="move_item", item_id="notebook", to_location="start")])
    v = rule_enforcer.validate(minimal_world, tr)
    assert v and "not in current location" in v[0]


# ── solve_puzzle ─────────────────────────────────────────────────────────────

def test_solve_puzzle_correct(minimal_world):
    tr = _turn([_sc(type="solve_puzzle", puzzle_id="code-lock", attempted_solution="1234")])
    assert rule_enforcer.validate(minimal_world, tr) == []


def test_solve_puzzle_case_insensitive(minimal_world):
    minimal_world.puzzles["code-lock"].solution = "OPEN"
    tr = _turn([_sc(type="solve_puzzle", puzzle_id="code-lock", attempted_solution="open")])
    assert rule_enforcer.validate(minimal_world, tr) == []


def test_solve_puzzle_wrong_solution(minimal_world):
    tr = _turn([_sc(type="solve_puzzle", puzzle_id="code-lock", attempted_solution="9999")])
    v = rule_enforcer.validate(minimal_world, tr)
    assert v and "wrong solution" in v[0]


def test_solve_puzzle_already_solved(minimal_world):
    minimal_world.puzzles["code-lock"].is_solved = True
    tr = _turn([_sc(type="solve_puzzle", puzzle_id="code-lock", attempted_solution="1234")])
    v = rule_enforcer.validate(minimal_world, tr)
    assert v and "already solved" in v[0]


def test_solve_puzzle_wrong_location(minimal_world):
    minimal_world.current_location_id = "exit"
    tr = _turn([_sc(type="solve_puzzle", puzzle_id="code-lock", attempted_solution="1234")])
    v = rule_enforcer.validate(minimal_world, tr)
    assert v and "not in current location" in v[0]


def test_solve_puzzle_unknown(minimal_world):
    tr = _turn([_sc(type="solve_puzzle", puzzle_id="ghost", attempted_solution="x")])
    v = rule_enforcer.validate(minimal_world, tr)
    assert v and "unknown puzzle" in v[0]


# ── apply ─────────────────────────────────────────────────────────────────

def test_apply_move_player(minimal_world):
    tr = _turn([_sc(type="move_player", to_location="exit")])
    ws = rule_enforcer.apply(minimal_world, tr)
    assert ws.current_location_id == "exit"
    assert minimal_world.current_location_id == "start"  # original unchanged


def test_apply_take_item(minimal_world):
    tr = _turn([_sc(type="take_item", item_id="notebook")])
    ws = rule_enforcer.apply(minimal_world, tr)
    assert "notebook" in ws.inventory
    assert "notebook" not in ws.locations["start"].item_ids
    assert ws.items["notebook"].location_id == "inventory"


def test_apply_solve_puzzle_marks_solved(minimal_world):
    tr = _turn([_sc(type="solve_puzzle", puzzle_id="code-lock", attempted_solution="1234")])
    ws = rule_enforcer.apply(minimal_world, tr)
    assert ws.puzzles["code-lock"].is_solved is True


def test_apply_increments_turn_count(minimal_world):
    tr = _turn([_sc(type="move_player", to_location="exit")])
    ws = rule_enforcer.apply(minimal_world, tr)
    assert ws.turn_count == 1


def test_apply_appends_history(minimal_world):
    tr = _turn([], narration="You look around.")
    ws = rule_enforcer.apply(minimal_world, tr)
    assert ws.history[-1]["narration"] == "You look around."


# ── win condition ─────────────────────────────────────────────────────────

def test_win_requires_both_location_and_puzzle(minimal_world):
    # puzzle not solved → no win even at exit location
    tr = _turn([_sc(type="move_player", to_location="exit")])
    ws = rule_enforcer.apply(minimal_world, tr)
    assert ws.is_won is False


def test_win_with_puzzle_solved_and_at_exit(minimal_world):
    minimal_world.puzzles["code-lock"].is_solved = True
    tr = _turn([_sc(type="move_player", to_location="exit")])
    ws = rule_enforcer.apply(minimal_world, tr)
    assert ws.is_won is True


def test_win_puzzle_solved_but_wrong_location(minimal_world):
    minimal_world.puzzles["code-lock"].is_solved = True
    tr = _turn([])  # stay in start
    ws = rule_enforcer.apply(minimal_world, tr)
    assert ws.is_won is False


def test_win_no_required_puzzles(minimal_world):
    minimal_world.win_condition.required_solved_puzzle_ids = []
    tr = _turn([_sc(type="move_player", to_location="exit")])
    ws = rule_enforcer.apply(minimal_world, tr)
    assert ws.is_won is True


# ── apply_fallback ────────────────────────────────────────────────────────

def test_apply_fallback_records_nothing_happens(minimal_world):
    ws = rule_enforcer.apply_fallback(minimal_world, "flap arms")
    assert ws.history[-1]["narration"] == "Nothing happens."
    assert ws.history[-1]["action"] == "flap arms"


def test_apply_fallback_increments_turn_count(minimal_world):
    ws = rule_enforcer.apply_fallback(minimal_world, "x")
    assert ws.turn_count == 1


def test_apply_fallback_does_not_mutate(minimal_world):
    rule_enforcer.apply_fallback(minimal_world, "x")
    assert minimal_world.turn_count == 0


# ── history cap ──────────────────────────────────────────────────────────

def test_history_capped_at_max(minimal_world):
    from engine.rule_enforcer import MAX_HISTORY
    ws = minimal_world
    for i in range(MAX_HISTORY + 5):
        tr = _turn([], narration=f"turn {i}")
        ws = rule_enforcer.apply(ws, tr)
    assert len(ws.history) == MAX_HISTORY
