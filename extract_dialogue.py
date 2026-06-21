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

def parse_action_string(action_string: str) -> list:
    if not action_string:
        return []
    
    parsed_data = json.loads(action_string)
    
    with open("test.json", "w", encoding="utf-8") as f:
        # We must dump the parsed_data (the list/dict), NOT the action_string!
        json.dump(parsed_data, f, ensure_ascii=False, indent=4)
    
    return parsed_data

def print_talk_flow(parsed_data: list):
    show_talks = [item for item in parsed_data if item.get("Name") == "ShowTalk"]
    if not show_talks:
        return
        
    for idx, show_talk in enumerate(show_talks):
        if idx > 0:
            print("==========")
            
        params = show_talk.get("Params", {})
        talk_items = {item["Id"]: item for item in params.get("TalkItems", [])}
        talk_sequence = params.get("TalkSequence", [])
        seq_transitions = params.get("SequenceTransitions", {})
        
        visited = set()
        
        def traverse(seq_idx, indent_level, stop_seqs):
            if seq_idx in visited or seq_idx >= len(talk_sequence) or seq_idx in stop_seqs:
                return
            visited.add(seq_idx)
            
            seq = talk_sequence[seq_idx]
            indent = "    " * indent_level
            
            transitions = seq_transitions.get(str(seq_idx), [])
            
            has_branching_options = False
            options_to_branch = []
            
            for talk_id in seq:
                item = talk_items.get(talk_id)
                if not item: continue
                
                tid_talk = item.get("TidTalk")
                if tid_talk:
                    print(f"{indent}{tid_talk}")
                    
                if item.get("Options"):
                    options = item.get("Options")
                    
                    # Check if these options trigger a branch in SequenceTransitions
                    branches = False
                    for opt in options:
                        opt_tid = opt.get("TidTalkOption")
                        for trans in transitions:
                            if trans.get("OptionTextKey") == opt.get("PlotLineKey") or trans.get("OptionTextKey") == opt_tid:
                                branches = True
                                break
                                
                    if branches:
                        has_branching_options = True
                        options_to_branch = options
                        break
                    else:
                        # Fake/inline options. Print them and continue the sequence.
                        for opt in options:
                            opt_tid = opt.get("TidTalkOption")
                            if opt_tid:
                                print(f"{indent}{opt_tid}")
            
            if has_branching_options:
                next_seqs = set()
                for opt in options_to_branch:
                    opt_tid = opt.get("TidTalkOption")
                    for trans in transitions:
                        if trans.get("OptionTextKey") == opt.get("PlotLineKey") or trans.get("OptionTextKey") == opt_tid:
                            branch_seq_idx = trans.get("NextSequenceIndex")
                            if branch_seq_idx is not None:
                                b_trans_list = seq_transitions.get(str(branch_seq_idx), [])
                                for bt in b_trans_list:
                                    if not bt.get("OptionTextKey"):
                                        next_seqs.add(bt.get("NextSequenceIndex"))
                            break
                            
                for opt in options_to_branch:
                    opt_tid = opt.get("TidTalkOption")
                    if opt_tid:
                        print(f"{indent}{opt_tid}")
                        
                    branch_seq_idx = None
                    for trans in transitions:
                        if trans.get("OptionTextKey") == opt.get("PlotLineKey") or trans.get("OptionTextKey") == opt_tid:
                            branch_seq_idx = trans.get("NextSequenceIndex")
                            break
                    
                    if branch_seq_idx is not None:
                        traverse(branch_seq_idx, indent_level + 1, stop_seqs.union(next_seqs))
                
                if len(next_seqs) == 1:
                    traverse(next_seqs.pop(), indent_level, stop_seqs)
                elif len(next_seqs) > 1:
                    for n_seq in sorted(next_seqs):
                        traverse(n_seq, indent_level, stop_seqs)
            else:
                if transitions:
                    for trans in transitions:
                        n_seq = trans.get("NextSequenceIndex")
                        if n_seq is not None:
                            traverse(n_seq, indent_level, stop_seqs)
                else:
                    # Proceed linearly if no transitions are defined
                    traverse(seq_idx + 1, indent_level, stop_seqs)

        traverse(0, 0, set())

# Example:
if __name__ == "__main__":
    # 1. Get States (StateKeys) from flow.json
    state_keys = get_states_for_id("flow.json", "剧情_3_3_拉海洛主线_下半_1")
    print(f"StateKeys found: {state_keys}")
    
    # 2. Get Actions for each StateKey from flowstate.json
    if state_keys:
        actions_dict = get_actions_for_state_keys("flowstate.json", state_keys)
        
        # 3. Parse one of the action strings into actual Python data
        for key in state_keys:
            if key == "剧情_3_3_拉海洛主线_下半_1_20":
                action_string = actions_dict.get(key)
            
                parsed_actions = parse_action_string(action_string)
                print_talk_flow(parsed_actions)
