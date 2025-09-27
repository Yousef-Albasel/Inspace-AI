from typing import Dict, Any
from agent_state import AgentState
from workflow_manager import WorkflowManager

class ComputerUseAgent:
    """Main Computer Use Agent class"""
    
    def __init__(self, omniparser_url: str = "http://127.0.0.1:8000", gemini_api_key: str = None):
        self.workflow_manager = WorkflowManager(omniparser_url, gemini_api_key)
    
    def execute_task(self, task: str, max_steps: int = 5) -> Dict[str, Any]:
        """Execute a complete multi-step task"""
        print(f"Starting multi-step task: {task}")
        
        initial_state = AgentState(
            task=task,
            original_task=task,
            screenshot_base64="",
            parsed_content=[],
            parsed_elements=[],
            reasoning="",
            action_plan="",
            target_element={},
            completed=False,
            error="",
            step_count=0,
            max_steps=max_steps,
            steps_completed=[]
        )
        
        # Execute the workflow
        self.workflow_manager.export_graph_image("workflow.png")
        final_state = self.workflow_manager.execute_workflow(initial_state)
        
        # Return summary
        return {
            "task": task,
            "completed": final_state.get("completed", False),
            "reasoning": final_state.get("reasoning", ""),
            "error": final_state.get("error", ""),
            "elements_found": len(final_state.get("parsed_content", [])),
            "steps_executed": final_state.get("step_count", 0),
            "steps_completed": final_state.get("steps_completed", [])
        }