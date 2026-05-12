"""Integration tests for turn_handler.handle_turn().

Skipped automatically when GEMINI_API_KEY is not set.
Run with: GEMINI_API_KEY=... pytest -m integration tests/test_turn_handler.py
"""
import os

import pytest

from engine.models import TurnResult
from engine.turn_handler import handle_turn

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def require_api_key():
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set")


@pytest.mark.asyncio
async def test_handle_turn_returns_turn_result(minimal_world):
    result = await handle_turn(minimal_world, "look around")
    assert isinstance(result, TurnResult)


@pytest.mark.asyncio
async def test_handle_turn_has_narration(minimal_world):
    result = await handle_turn(minimal_world, "look around")
    assert len(result.narration) > 0


@pytest.mark.asyncio
async def test_handle_turn_is_won_always_false(minimal_world):
    # Engine determines win, not LLM; handle_turn always returns False
    result = await handle_turn(minimal_world, "look around")
    assert result.is_won is False


@pytest.mark.asyncio
async def test_handle_turn_move_action(minimal_world):
    result = await handle_turn(minimal_world, "go to the exit")
    types = [sc.type for sc in result.state_changes]
    # May or may not produce move_player; if it does, to_location must be valid
    for sc in result.state_changes:
        if sc.type == "move_player":
            assert sc.to_location in minimal_world.locations


@pytest.mark.asyncio
async def test_handle_turn_nonsense_action(minimal_world):
    result = await handle_turn(minimal_world, "flap my arms and fly to the moon")
    # Should return narration but likely empty state_changes
    assert result.narration


@pytest.mark.asyncio
async def test_handle_turn_with_correction(minimal_world):
    corrections = ["move_player: 'nowhere' is not connected to 'start'"]
    result = await handle_turn(minimal_world, "go somewhere", correction=corrections)
    assert isinstance(result, TurnResult)
