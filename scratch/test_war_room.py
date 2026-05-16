import asyncio
import json
import os
import sys

# Add root to path so we can import backend
sys.path.append(os.getcwd())

from backend.services import agent_service

async def test_war_room_simulation():
    print("STARTING WAR ROOM SIMULATION TEST\n")
    
    # 1. Generate Initial Scenario (THE HOOK)
    print("--- TURN 1: THE HOOK ---")
    scenario = await agent_service.generate_scam_scenario()
    print(f"Scammer: {scenario['message'].encode('ascii', 'replace').decode()}")
    print(f"Personality: {scenario.get('scammer_personality')}")
    print(f"Strategy: {scenario.get('emotional_strategy')}")
    print(f"Stage: {scenario.get('escalation_stage')}\n")
    
    # 2. User Responds (Skeptical but engaging)
    print("--- TURN 2: USER RESPONDS ---")
    user_reply = "Who is this? Why are you calling me?"
    print(f"User: {user_reply}")
    
    scenario = await agent_service.continue_scenario(scenario, user_reply)
    print(f"Scammer: {scenario['message'].encode('ascii', 'replace').decode()}")
    print(f"Stage: {scenario.get('escalation_stage')}\n")
    
    # 3. User Responds (Following along)
    print("--- TURN 3: THE PIVOT ---")
    user_reply = "Okay, what do I need to do? I don't want my account blocked."
    print(f"User: {user_reply}")
    
    scenario = await agent_service.continue_scenario(scenario, user_reply)
    print(f"Scammer: {scenario['message'].encode('ascii', 'replace').decode()}")
    print(f"Stage: {scenario.get('escalation_stage')}\n")
    
    # 4. User Responds (Asking for proof)
    print("--- TURN 4: THE PRESSURE ---")
    user_reply = "Can you send me some proof? How do I know you are from the bank?"
    print(f"User: {user_reply}")
    
    scenario = await agent_service.continue_scenario(scenario, user_reply)
    print(f"Scammer: {scenario['message'].encode('ascii', 'replace').decode()}")
    print(f"Stage: {scenario.get('escalation_stage')}\n")

    print("TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(test_war_room_simulation())
