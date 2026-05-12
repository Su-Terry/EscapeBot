"""Integration tests for scenario_generator.generate().

Skipped automatically when GEMINI_API_KEY is not set.
Run with: GEMINI_API_KEY=... pytest -m integration tests/test_scenario_generator.py
"""
import os

import pytest
import pytest_asyncio

from engine.models import WorldState
from engine.scenario_generator import generate

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def require_api_key():
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set")


@pytest.mark.asyncio
async def test_generate_returns_world_state():
    ws = await generate("integration_test_user")
    assert isinstance(ws, WorldState)


@pytest.mark.asyncio
async def test_generate_session_id_set():
    ws = await generate("alice")
    assert ws.session_id == "alice"


@pytest.mark.asyncio
async def test_generate_minimum_locations():
    ws = await generate("integration_test_user")
    assert len(ws.locations) >= 3


@pytest.mark.asyncio
async def test_generate_minimum_items():
    ws = await generate("integration_test_user")
    assert len(ws.items) >= 4


@pytest.mark.asyncio
async def test_generate_minimum_puzzles():
    ws = await generate("integration_test_user")
    assert len(ws.puzzles) >= 2


@pytest.mark.asyncio
async def test_generate_has_opening_narration():
    ws = await generate("integration_test_user")
    assert len(ws.history) >= 1
    assert ws.history[0]["narration"]


@pytest.mark.asyncio
async def test_generate_start_location_valid():
    ws = await generate("integration_test_user")
    assert ws.current_location_id in ws.locations


@pytest.mark.asyncio
async def test_generate_win_target_valid():
    ws = await generate("integration_test_user")
    assert ws.win_condition.target_location_id in ws.locations


@pytest.mark.asyncio
async def test_generate_inventory_empty():
    ws = await generate("integration_test_user")
    assert ws.inventory == []


@pytest.mark.asyncio
async def test_generate_referential_integrity():
    # The model_validator runs automatically on construction;
    # if this returns without raising, integrity is confirmed.
    ws = await generate("integration_test_user")
    _ = ws.model_dump()  # triggers __dict__ access on all nested models
