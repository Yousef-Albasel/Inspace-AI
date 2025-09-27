import json
import google.generativeai as genai
import os
from agent_state import AgentState

class AIReasoner:
    """Handles AI reasoning using Gemini LLM"""
    
    def __init__(self, gemini_api_key: str = None):
        api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass it as parameter.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def reason_and_plan(self, state: AgentState) -> AgentState:
        """Use Gemini LLM to analyze screen content and decide on action"""
        print("Analyzing screen and planning action with Gemini LLM...")
        
        try:
            # Prepare the prompt for the LLM
            screen_elements = "\n".join([
                f"Element {elem['id']}: {elem['content']}" 
                for elem in state["parsed_elements"]
            ])
            
            # Include context about what has been done so far
            progress_info = ""
            if state["steps_completed"]:
                progress_info = f"\nSteps already completed: {', '.join(state['steps_completed'])}"
            
            prompt = f"""
You are a computer use agent helping a user complete a multi-step task. Analyze the current screen and decide the NEXT action needed.

ORIGINAL TASK: {state['original_task']}
CURRENT STEP: {state['step_count'] + 1}/{state['max_steps']}{progress_info}

CURRENT SCREEN ELEMENTS:
{screen_elements}

Instructions:
1. Consider the original task and what steps have already been completed
2. Identify what the NEXT logical step should be
3. Find the element (by ID) that helps accomplish this next step
4. If the task appears to be completely finished, set completed to true
5. If no suitable element exists for the next step, set target_element_id to null

Respond in this JSON format:
{{
    "target_element_id": <number or null>,
    "reasoning": "<your reasoning about what step to take next>",
    "action": "<click/type/etc>",
    "step_description": "<brief description of this step>",
    "completed": <true/false - true if the entire original task is now complete>,
    "confidence": "<high/medium/low>"
}}

Example response:
{{
    "target_element_id": 15,
    "reasoning": "New tab has been opened. Now I need to navigate to google.com. I can see the address bar at element 15.",
    "action": "click",
    "step_description": "Click address bar to search google.com",
    "completed": false,
    "confidence": "high"
}}

Only respond with the JSON object, nothing else.
"""

            # Generate response using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=400,
                )
            )
            
            llm_response = response.text.strip()
            print(f"Gemini Response: {llm_response}")
            
            # Try to parse JSON response
            try:
                # Clean the response in case it has markdown formatting
                json_text = llm_response
                if "```json" in json_text:
                    json_text = json_text.split("```json")[1].split("```")[0].strip()
                elif "```" in json_text:
                    json_text = json_text.split("```")[1].strip()
                
                decision = json.loads(json_text)
                
                # Check if task will be completed after this action
                will_be_completed = decision.get("completed", False)
                if will_be_completed:
                    print("Task will be completed after this action!")
                
                if decision.get("target_element_id") is not None:
                    element_id = decision["target_element_id"]
                    # Find the element with this ID
                    target_element = next(
                        (elem for elem in state["parsed_elements"] if elem["id"] == element_id),
                        None
                    )
                    
                    if target_element:
                        state["target_element"] = target_element
                        state["reasoning"] = decision.get("reasoning", "Gemini analysis completed")
                        
                        # Mark as completed AFTER we set up the action
                        if will_be_completed:
                            state["completed"] = True
                        
                        # Store step description
                        step_desc = decision.get("step_description", f"Interact with {target_element.get('content', 'element')}")
                        print(f"Next step: {step_desc}")
                        print(f"Target: {target_element.get('content', 'Unknown element')}")
                    else:
                        state["reasoning"] = f"Element ID {element_id} not found"
                        if will_be_completed:
                            state["completed"] = True
                else:
                    state["reasoning"] = decision.get("reasoning", "No suitable element identified by Gemini")
                    if will_be_completed:
                        state["completed"] = True
                    
            except json.JSONDecodeError as e:
                # If JSON parsing fails, extract reasoning from text
                state["reasoning"] = f"Gemini response (JSON parsing failed): {llm_response}"
                print(f"JSON parsing error: {e}")
                
        except Exception as e:
            state["error"] = f"Gemini reasoning failed: {str(e)}"
            print(f"Gemini error: {e}")
            
        print(f"Reasoning: {state['reasoning']}")
        return state