"""Unit tests for engine.gemini_utils and scenario_generator normalization helpers."""
import pytest

from engine.gemini_utils import to_gemini_schema
from engine.models import TurnResult, WorldState
from engine.scenario_generator import _normalize_world_state_dict


def _has_key_recursive(obj, key: str) -> bool:
    if isinstance(obj, dict):
        if key in obj:
            return True
        return any(_has_key_recursive(v, key) for v in obj.values())
    elif isinstance(obj, list):
        return any(_has_key_recursive(item, key) for item in obj)
    return False


def test_no_additional_properties_world_state():
    schema = to_gemini_schema(WorldState)
    assert not _has_key_recursive(schema, "additionalProperties")


def test_no_additional_properties_turn_result():
    schema = to_gemini_schema(TurnResult)
    assert not _has_key_recursive(schema, "additionalProperties")


def test_no_defs_world_state():
    schema = to_gemini_schema(WorldState)
    assert "$defs" not in schema
    assert not _has_key_recursive(schema, "$defs")


def test_no_refs_world_state():
    schema = to_gemini_schema(WorldState)
    assert not _has_key_recursive(schema, "$ref")


def test_no_schema_keyword():
    schema = to_gemini_schema(WorldState)
    assert not _has_key_recursive(schema, "$schema")


def test_result_is_dict():
    schema = to_gemini_schema(WorldState)
    assert isinstance(schema, dict)


def test_turn_result_has_narration_property():
    schema = to_gemini_schema(TurnResult)
    assert "narration" in schema.get("properties", {})


def test_turn_result_has_state_changes_property():
    schema = to_gemini_schema(TurnResult)
    assert "state_changes" in schema.get("properties", {})


def test_world_state_has_locations_property():
    schema = to_gemini_schema(WorldState)
    assert "locations" in schema.get("properties", {})


def test_normalize_rekeys_by_id():
    data = {
        "locations": {
            "Cryo Bay": {"id": "cryo-bay", "name": "Cryo Bay"},
            "Command Center": {"id": "command-center", "name": "Command Center"},
        },
        "items": {
            "Old Key": {"id": "old-key", "name": "Old Key"},
        },
        "puzzles": {
            "Puzzle One": {"id": "puzzle-one", "description": "A puzzle"},
        },
    }
    result = _normalize_world_state_dict(data)
    assert "cryo-bay" in result["locations"]
    assert "Cryo Bay" not in result["locations"]
    assert "command-center" in result["locations"]
    assert "old-key" in result["items"]
    assert "Old Key" not in result["items"]
    assert "puzzle-one" in result["puzzles"]


def test_normalize_noop_when_keys_already_correct():
    data = {
        "locations": {"cryo-bay": {"id": "cryo-bay"}},
        "items": {},
        "puzzles": {},
    }
    result = _normalize_world_state_dict(data)
    assert result["locations"] == {"cryo-bay": {"id": "cryo-bay"}}


def test_normalize_skips_non_dict_field():
    data = {"locations": None, "items": {}, "puzzles": {}}
    result = _normalize_world_state_dict(data)
    assert result["locations"] is None


def test_normalize_preserves_other_fields():
    data = {
        "session_id": "alice",
        "locations": {"Room One": {"id": "room-one"}},
        "items": {},
        "puzzles": {},
    }
    result = _normalize_world_state_dict(data)
    assert result["session_id"] == "alice"


def test_nullable_fields_flattened():
    schema = to_gemini_schema(TurnResult)
    # state_changes items have nullable fields like item_id, to_location, etc.
    # After flattening, no anyOf with null branch should remain
    # (they become {type: X, nullable: true})
    def find_anyof_with_null(obj) -> bool:
        if isinstance(obj, dict):
            if "anyOf" in obj:
                branches = obj["anyOf"]
                if isinstance(branches, list):
                    has_null = any(b == {"type": "null"} for b in branches)
                    if has_null:
                        return True
            return any(find_anyof_with_null(v) for v in obj.values())
        elif isinstance(obj, list):
            return any(find_anyof_with_null(item) for item in obj)
        return False

    assert not find_anyof_with_null(schema)
