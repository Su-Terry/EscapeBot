import pytest
from engine.models import Item, Location, Puzzle, WinCondition, WorldState


@pytest.fixture
def minimal_world() -> WorldState:
    """Minimal valid WorldState: 2 locations, 2 items, 1 puzzle."""
    return WorldState(
        session_id="testuser",
        current_location_id="start",
        locations={
            "start": Location(
                id="start",
                name="Starting Room",
                description="A plain room.",
                item_ids=["notebook", "key"],
                connected_location_ids=["exit"],
            ),
            "exit": Location(
                id="exit",
                name="Exit",
                description="The way out.",
                item_ids=[],
                connected_location_ids=["start"],
            ),
        },
        items={
            "notebook": Item(
                id="notebook",
                name="Notebook",
                description="Has numbers on it.",
                location_id="start",
                is_takeable=True,
            ),
            "key": Item(
                id="key",
                name="Key",
                description="Opens the locked box.",
                location_id="start",
                is_takeable=True,
                is_locked=True,
                unlock_item_id="notebook",
            ),
        },
        puzzles={
            "code-lock": Puzzle(
                id="code-lock",
                location_id="start",
                description="A combination lock.",
                solution="1234",
                reward_item_id=None,
            )
        },
        win_condition=WinCondition(
            description="Reach the exit.",
            target_location_id="exit",
            required_solved_puzzle_ids=["code-lock"],
        ),
    )
