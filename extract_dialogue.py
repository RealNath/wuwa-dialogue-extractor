from json import encoder
import json
from typing import List

def get_states_for_id(filepath: str, target_id: str) -> List[str]:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for item in data:
        if item.get("Id") == target_id:
            states = item.get("States", [])
            return [f"{target_id}_{state}" for state in states]
            
    return []

def get_actions_for_state_keys(filepath: str, state_keys: List[str]) -> dict:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    state_keys_set = set(state_keys)
    result = {}
    
    for item in data:
        state_key = item.get("StateKey")
        if state_key in state_keys_set:
            result[state_key] = item.get("Actions")
            
    return result

if __name__ == "__main__":
    # 1. Get States (StateKeys) from flow.json
    state_keys = get_states_for_id("flow.json", "剧情_中曲台地_NPC对话_19")
    print(f"StateKeys found: {state_keys}")
    
    # 2. Get Actions for each StateKey from flowstate.json
    if state_keys:
        actions_dict = get_actions_for_state_keys("flowstate.json", state_keys)
        print(actions_dict)
    pass
