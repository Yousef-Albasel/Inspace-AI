import pyautogui
import base64
import time
import io
from agent_state import AgentState

class ScreenCapture:
    """Handles screenshot capture and conversion to base64"""
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 1.0
    
    def take_screenshot(self, state: AgentState) -> AgentState:
        """Take a screenshot and convert to base64"""
        print(f"Taking screenshot (Step {state['step_count'] + 1}/{state['max_steps']})...")
        
        try:
            time.sleep(1)
            screenshot = pyautogui.screenshot()
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            screenshot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            state["screenshot_base64"] = screenshot_base64
            print("Screenshot captured successfully")
            
        except Exception as e:
            state["error"] = f"Failed to take screenshot: {str(e)}"
            print(f"Screenshot error: {e}")
        
        return state