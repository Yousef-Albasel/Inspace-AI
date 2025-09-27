from typing import Dict, List, Any, TypedDict

class AgentState(TypedDict):
    task: str
    original_task: str 
    screenshot_base64: str
    parsed_content: List[str]
    parsed_elements: List[Dict]
    reasoning: str
    action_plan: str
    target_element: Dict[str, Any]
    completed: bool
    error: str
    step_count: int
    max_steps: int
    steps_completed: List[str]