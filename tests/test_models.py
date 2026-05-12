import pytest
from pydantic import ValidationError

from engine.models import Item, Location, Puzzle, WinCondition, WorldState


def _base_kwargs() -> dict:
    return dict(
        session_id="u",
        current_location_id="a",
        locations={
            "a": Location(id="a", name="A", description="Room A", item_ids=["i1"], connected_location_ids=["b"]),
            "b": Location(id="b", name="B", description="Room B", item_ids=[], connected_location_ids=["a"]),
        },
        items={
            "i1": Item(id="i1", name="Widget", description="A widget.", location_id="a", is_takeable=True),
        },
        puzzles={
            "p1": Puzzle(id="p1", location_id="a", description="A puzzle.", solution="abc"),
        },
        win_condition=WinCondition(description="Escape.", target_location_id="b"),
    )


def test_valid_construction():
    ws = WorldState(**_base_kwargs())
    assert ws.current_location_id == "a"
    assert ws.turn_count == 0
    assert ws.inventory == []


def test_invalid_current_location_id():
    kw = _base_kwargs()
    kw["current_location_id"] = "nonexistent"
    with pytest.raises(ValidationError, match="current_location_id"):
        WorldState(**kw)


def test_invalid_win_target_location():
    kw = _base_kwargs()
    kw["win_condition"] = WinCondition(description="x", target_location_id="missing")
    with pytest.raises(ValidationError, match="target_location_id"):
        WorldState(**kw)


def test_invalid_required_solved_puzzle():
    kw = _base_kwargs()
    kw["win_condition"] = WinCondition(
        description="x", target_location_id="b", required_solved_puzzle_ids=["ghost"]
    )
    with pytest.raises(ValidationError, match="required_solved_puzzle_ids"):
        WorldState(**kw)


def test_invalid_location_connected_ref():
    kw = _base_kwargs()
    kw["locations"]["a"] = Location(
        id="a", name="A", description="d", item_ids=["i1"], connected_location_ids=["nowhere"]
    )
    with pytest.raises(ValidationError, match="connected location"):
        WorldState(**kw)


def test_invalid_location_item_ref():
    kw = _base_kwargs()
    kw["locations"]["a"] = Location(
        id="a", name="A", description="d", item_ids=["ghost"], connected_location_ids=["b"]
    )
    with pytest.raises(ValidationError, match="unknown item"):
        WorldState(**kw)


def test_invalid_item_unlock_ref():
    kw = _base_kwargs()
    kw["items"]["i1"] = Item(
        id="i1", name="W", description="d", location_id="a",
        is_takeable=True, is_locked=True, unlock_item_id="ghost"
    )
    with pytest.raises(ValidationError, match="unlock_item_id"):
        WorldState(**kw)


def test_invalid_item_location_ref():
    kw = _base_kwargs()
    kw["items"]["i1"] = Item(
        id="i1", name="W", description="d", location_id="nowhere", is_takeable=True
    )
    with pytest.raises(ValidationError, match="location_id"):
        WorldState(**kw)


def test_invalid_puzzle_location_ref():
    kw = _base_kwargs()
    kw["puzzles"]["p1"] = Puzzle(id="p1", location_id="nowhere", description="x", solution="y")
    with pytest.raises(ValidationError, match="Puzzle"):
        WorldState(**kw)


def test_invalid_puzzle_reward_ref():
    kw = _base_kwargs()
    kw["puzzles"]["p1"] = Puzzle(id="p1", location_id="a", description="x", solution="y", reward_item_id="ghost")
    with pytest.raises(ValidationError, match="reward_item_id"):
        WorldState(**kw)


def test_invalid_inventory_ref():
    kw = _base_kwargs()
    kw["inventory"] = ["ghost"]
    with pytest.raises(ValidationError, match="Inventory"):
        WorldState(**kw)


def test_safe_context_strips_solutions():
    ws = WorldState(**_base_kwargs())
    ctx = ws.safe_context()
    for puzzle in ctx["puzzles"].values():
        assert "solution" not in puzzle


def test_safe_context_does_not_mutate():
    ws = WorldState(**_base_kwargs())
    ws.safe_context()
    assert ws.puzzles["p1"].solution == "abc"


def test_json_roundtrip():
    ws = WorldState(**_base_kwargs())
    json_str = ws.model_dump_json()
    ws2 = WorldState.model_validate_json(json_str)
    assert ws2.session_id == ws.session_id
    assert ws2.puzzles["p1"].solution == "abc"


def test_item_in_inventory_valid():
    kw = _base_kwargs()
    kw["items"]["i1"] = Item(id="i1", name="W", description="d", location_id="inventory", is_takeable=True)
    kw["inventory"] = ["i1"]
    ws = WorldState(**kw)
    assert "i1" in ws.inventory
