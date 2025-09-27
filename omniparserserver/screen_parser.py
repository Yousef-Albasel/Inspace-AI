import requests
from agent_state import AgentState

class ScreenParser:
    """Handles communication with OmniParser server"""
    
    def __init__(self, omniparser_url: str = "http://127.0.0.1:8000"):
        self.omniparser_url = omniparser_url
    
    def parse_screen(self, state: AgentState) -> AgentState:
        """Send screenshot to OmniParser server"""
        print("Parsing screen content...")
        
        try:
            payload = {"base64_image": state["screenshot_base64"]}
            
            response = requests.post(
                f"{self.omniparser_url}/parse/",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "parsed_content_list" in result:
                    state["parsed_content"] = result["parsed_content_list"]
                    
                    # If the response includes full element data, use it
                    if isinstance(state["parsed_content"], list) and len(state["parsed_content"]) > 0:
                        if isinstance(state["parsed_content"][0], dict):
                            # Full element data is available
                            state["parsed_elements"] = []
                            for i, element_data in enumerate(state["parsed_content"]):
                                element = {"id": i}
                                element.update(element_data)  # Merge all element data including bbox
                                state["parsed_elements"].append(element)
                        else:
                            # Only content strings, try to get coordinates separately
                            state["parsed_elements"] = []
                            for i, content in enumerate(state["parsed_content"]):
                                element = {"id": i, "content": content}
                                
                                # Check if we have label_coordinates
                                if "label_coordinates" in result and str(i) in result["label_coordinates"]:
                                    element["bbox"] = result["label_coordinates"][str(i)]
                                
                                state["parsed_elements"].append(element)
                
                print(f"Found {len(state['parsed_content'])} elements on screen")
                    
            else:
                state["error"] = f"OmniParser error: {response.status_code}"
                
        except Exception as e:
            state["error"] = f"Failed to parse screen: {str(e)}"
            print(f"Parsing error: {e}")
        
        return state