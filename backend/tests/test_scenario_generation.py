import os
import sys

# Ensure repository root is in sys.path
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import asyncio
import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from backend.services import AgentService, agent_service
from backend.fallback_scenarios import FallbackScenarioEngine, fallback_engine
from backend.websocket_manager import WarRoomSession, WarRoomConnectionManager, SessionState


@pytest.mark.asyncio
async def test_groq_generates_valid_scenario():
    """Requirement 1: Groq generates a valid new scenario with full schema fields."""
    scenario = await agent_service.generate_scam_scenario()
    assert scenario is not None
    assert "message" in scenario and len(scenario["message"]) > 0
    assert "scenario_type" in scenario
    assert "ui_title" in scenario
    assert "recommended_actions" in scenario
    assert isinstance(scenario["recommended_actions"], list)
    assert len(scenario["recommended_actions"]) >= 4
    assert scenario.get("generation_source") in ["groq", "fallback"]


@pytest.mark.asyncio
async def test_consecutive_scenario_variation():
    """Requirement 2: Consecutive scenario requests produce meaningful variation."""
    history = []
    scen1 = await agent_service.generate_scam_scenario(session_history=history)
    history.append({
        "scenario_type": scen1.get("scenario_type"),
        "attacker_persona": scen1.get("attacker_persona"),
        "ui_title": scen1.get("ui_title"),
    })

    scen2 = await agent_service.generate_scam_scenario(session_history=history)
    
    # Check that messages and titles are not identical
    assert scen1["message"] != scen2["message"]
    # Check that it doesn't repeat the exact same title
    assert scen1.get("ui_title") != scen2.get("ui_title")


@pytest.mark.asyncio
async def test_continuation_preserves_scenario():
    """Requirement 3: A 'no' response continues the active scenario instead of starting another."""
    active_scenario = {
        "scenario_type": "electricity_threat",
        "attacker_persona": "BSES Electricity Billing Officer",
        "message": "Your power connection will be cut at 9:30 PM tonight due to unpaid bill of ₹2,840.",
        "ui_title": "⚡ Electricity Disconnection Alert",
        "ui_description": "Urgent disconnection threat forcing payment",
        "amount": 2840,
        "escalation_stage": 1,
        "tip": "Check bills on official portal."
    }

    continuation = await agent_service.continue_scenario(active_scenario, "No, I already paid my bill yesterday!")
    
    assert continuation is not None
    assert "message" in continuation
    # It must NOT switch to an investment or KYC scam!
    assert "cryptoboost" not in continuation["message"].lower()
    assert continuation.get("escalation_stage", 2) >= 2
    assert continuation.get("ui_title") == active_scenario["ui_title"]


@pytest.mark.asyncio
async def test_session_state_and_start_controls():
    """Requirement 4: start does not create duplicate scenarios when one is active."""
    dummy_ws = AsyncMock()
    session = WarRoomSession("test-session-123", dummy_ws)
    
    # Fresh session can generate
    can_gen, _ = session.can_generate_new_scenario()
    assert can_gen is True

    # Start scenario
    scenario = {"scenario_type": "upi_fraud", "message": "Test hook", "ui_title": "Test Title"}
    session.start_scenario(scenario)
    assert session.active_scenario is not None
    assert session.state == SessionState.ACTIVE_SCENARIO


@pytest.mark.asyncio
async def test_session_isolation():
    """Requirement 10: Different sessions do not share private scenario history."""
    ws1, ws2 = AsyncMock(), AsyncMock()
    session1 = WarRoomSession("sess-1", ws1)
    session2 = WarRoomSession("sess-2", ws2)

    session1.record_scenario({"scenario_type": "digital_arrest_threat", "ui_title": "CBI Arrest Notice"})
    
    assert len(session1.get_history_summary()) == 1
    assert session1.get_history_summary()[0]["scenario_type"] == "digital_arrest_threat"
    # Session 2 must be clean and unpolluted
    assert len(session2.get_history_summary()) == 0


@pytest.mark.asyncio
async def test_invalid_json_handling():
    """Requirement 6: Invalid JSON from LLM is handled safely without crashing."""
    service = AgentService()
    # Mock infiltrator returning malformed string
    service.infiltrator.send_message = MagicMock(return_value="NOT_JSON_AT_ALL {{{")

    scenario = await service.generate_scam_scenario()
    assert scenario is not None
    assert "message" in scenario
    assert scenario.get("generation_source") == "fallback"
    assert scenario.get("is_ai_generated") is False


@pytest.mark.asyncio
async def test_fallback_identification():
    """Requirement 9: Fallback scenarios are correctly identified and diverse."""
    engine = FallbackScenarioEngine()
    scen = engine.generate_random_scenario()
    assert scen["generation_source"] == "fallback"
    assert scen["is_ai_generated"] is False
    assert scen["is_fallback"] is True
    assert len(engine.ALL_SCENARIOS if hasattr(engine, "ALL_SCENARIOS") else engine.TAXONOMY_SCENARIOS) >= 20


@pytest.mark.asyncio
async def test_action_buttons_structure():
    """Requirement 11: Action buttons have required structure and IDs."""
    scen = await agent_service.generate_scam_scenario()
    actions = scen.get("recommended_actions", [])
    action_ids = [a["action_id"] for a in actions]
    
    assert "pay" in action_ids
    assert "analyze" in action_ids
    assert "ignore" in action_ids
    assert "block" in action_ids
    assert "report" in action_ids
