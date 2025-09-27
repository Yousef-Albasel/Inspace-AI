import os
from dotenv import load_dotenv
from computer_use_agent import ComputerUseAgent

load_dotenv()

def print_result(result):
    """Print formatted result"""
    print("\n" + "=" * 50)
    print("EXECUTION RESULT")
    print("=" * 50)
    print(f"Task: {result['task']}")
    print(f"Completed: {'Yes' if result['completed'] else 'No'}")
    print(f"Steps executed: {result['steps_executed']}")
    print(f"Elements found in last screen: {result['elements_found']}")
    print(f"Final reasoning: {result['reasoning']}")
    
    if result['steps_completed']:
        print("Steps completed:")
        for i, step in enumerate(result['steps_completed'], 1):
            print(f"  {i}. {step}")
    
    if result['error']:
        print(f"Error: {result['error']}")
    print("=" * 50)

def main():
    """Main function for Computer Use Agent"""
    print("Multi-Step Computer Use Agent with Gemini LLM")
    print("=" * 60)
    
    if not os.getenv('GEMINI_API_KEY'):
        print("Please set your GEMINI_API_KEY environment variable")
        print("Get a free API key at: https://makersuite.google.com/app/apikey")
        api_key = input("Or enter your Gemini API key: ").strip()
        if not api_key:
            print("API key is required to run the agent")
            return
        agent = ComputerUseAgent(gemini_api_key=api_key)
    else:
        agent = ComputerUseAgent()
    
    while True:
        print("\nChoose an option:")
        print("1. Enter custom task")
        print("q. Quit")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == '1':
            custom_task = input("Enter your multi-step task: ").strip()
            if custom_task:
                max_steps = int(input("Max steps (default 5): ") or "5")
                print(f"\nExecuting: {custom_task}")
                result = agent.execute_task(custom_task, max_steps)
                print_result(result)
            else:
                print("Task cannot be empty")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()