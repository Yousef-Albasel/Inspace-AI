import pyautogui
from agent_state import AgentState

class ActionExecutor:
    """Handles execution of actions on screen elements"""
    
    def execute_action(self, state: AgentState) -> AgentState:
        """Execute the planned action using actual coordinates"""
        print("Executing action...")
        
        if not state["target_element"]:
            if state["completed"]:
                print("Task completed - no further action needed")
            else:
                print("No action to execute - moving to completion check")
            return state
        
        try:
            element = state["target_element"]
            
            # Check if bbox coordinates are available
            if "bbox" in element and element["bbox"]:
                bbox = element["bbox"]
                
                # bbox format appears to be normalized coordinates [x1, y1, x2, y2]
                if len(bbox) >= 4:
                    # Get screen dimensions
                    screen_width, screen_height = pyautogui.size()
                    
                    # Convert normalized coordinates to pixel coordinates
                    x1 = bbox[0] * screen_width
                    y1 = bbox[1] * screen_height
                    x2 = bbox[2] * screen_width
                    y2 = bbox[3] * screen_height
                    
                    # Calculate center point
                    click_x = int((x1 + x2) / 2)
                    click_y = int((y1 + y2) / 2)
                    
                    print(f"Clicking '{element.get('content', 'element')}' at ({click_x}, {click_y})")
                    pyautogui.click(click_x, click_y)
                    
                    # Record this step
                    step_desc = f"Clicked {element.get('content', 'element')}"
                    state["steps_completed"].append(step_desc)
                    
                else:
                    print("Insufficient bbox data")
                    
            else:
                print("No bbox coordinates available")
            
            print("Action executed successfully")
            
        except Exception as e:
            state["error"] = f"Failed to execute action: {str(e)}"
            print(f"Execution error: {e}")
        
        return state