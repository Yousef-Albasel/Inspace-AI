from langgraph.graph import StateGraph, END
from agent_state import AgentState
from screen_capture import ScreenCapture
from screen_parser import ScreenParser
from ai_reasoner import AIReasoner
from action_executor import ActionExecutor
from IPython.display import Image, display

class WorkflowManager:
    """Manages the workflow graph and orchestrates all components"""
    
    def __init__(self, omniparser_url: str = "http://127.0.0.1:8000", gemini_api_key: str = None):
        # Initialize all components
        self.screen_capture = ScreenCapture()
        self.screen_parser = ScreenParser(omniparser_url)
        self.ai_reasoner = AIReasoner(gemini_api_key)
        self.action_executor = ActionExecutor()
        
        # Build the workflow graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the workflow graph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("take_screenshot", self.screen_capture.take_screenshot)
        workflow.add_node("parse_screen", self.screen_parser.parse_screen)
        workflow.add_node("reason_and_plan", self.ai_reasoner.reason_and_plan)
        workflow.add_node("execute_action", self.action_executor.execute_action)
        workflow.add_node("check_completion", self._check_completion)
        
        # Add edges
        workflow.set_entry_point("take_screenshot")
        workflow.add_edge("take_screenshot", "parse_screen")
        workflow.add_edge("parse_screen", "reason_and_plan")
        workflow.add_edge("reason_and_plan", "execute_action")
        workflow.add_edge("execute_action", "check_completion")
        
        # Conditional edge: continue or end
        workflow.add_conditional_edges(
            "check_completion",
            self._should_continue,
            {
                "continue": "take_screenshot",  # Loop back to take new screenshot
                "end": END
            }
        )
        
        return workflow.compile()
    
    def _should_continue(self, state: AgentState) -> str:
        """Decide whether to continue or end the workflow"""
        if state["completed"]:
            return "end"
        if state["error"]:
            return "end"
        if state["step_count"] >= state["max_steps"]:
            print(f"Reached maximum steps ({state['max_steps']})")
            return "end"
        return "continue"
    
    def _check_completion(self, state: AgentState) -> AgentState:
        """Check if we should continue or if we're done"""
        state["step_count"] += 1
        
        print(f"Step {state['step_count']} completed")
        if state["steps_completed"]:
            print(f"Steps so far: {', '.join(state['steps_completed'])}")
        
        # Reset target element for next iteration
        state["target_element"] = {}
        
        return state
    
    def execute_workflow(self, initial_state: AgentState) -> AgentState:
        """Execute the complete workflow"""
        return self.graph.invoke(initial_state)

    def export_graph_image(self, filename: str = "workflow.png", show: bool = True) -> None:
        """Export the workflow graph as a PNG image and optionally display it inline"""
        g = self.graph.get_graph()
        
        # draw_mermaid_png returns bytes
        png_bytes = g.draw_mermaid_png()
        
        # Save to file
        with open(filename, "wb") as f:
            f.write(png_bytes)
        print(f"Graph image saved to {filename}")

        # Show inline in Jupyter/IPython
        if show:
            display(Image(png_bytes))