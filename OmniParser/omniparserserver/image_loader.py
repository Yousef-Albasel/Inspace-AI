import requests
import base64
import json
import sys
import os
from pathlib import Path

def image_to_base64(image_path):
    """Convert image file to base64 string"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: Image file '{image_path}' not found")
        return None
    except Exception as e:
        print(f"Error reading image: {e}")
        return None

def send_to_omniparser(image_path, server_url="http://127.0.0.1:8000"):
    """Send image to OmniParser server and get response"""
    
    # Check if server is running
    try:
        probe_response = requests.get(f"{server_url}/probe/")
        if probe_response.status_code != 200:
            print("Server is not responding properly")
            return None
    except requests.exceptions.ConnectionError:
        print(f"Cannot connect to server at {server_url}")
        print("Make sure the OmniParser server is running")
        return None
    
    # Convert image to base64
    base64_image = image_to_base64(image_path)
    if not base64_image:
        return None
    
    # Prepare request
    payload = {"base64_image": base64_image}
    
    print(f"Sending image '{image_path}' to OmniParser...")
    
    try:
        # Send POST request
        response = requests.post(
            f"{server_url}/parse/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"Server error: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def save_annotated_image(base64_image, output_path):
    """Save the annotated image from base64 string"""
    try:
        image_data = base64.b64decode(base64_image)
        with open(output_path, "wb") as f:
            f.write(image_data)
        print(f"Annotated image saved to: {output_path}")
    except Exception as e:
        print(f"Error saving image: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <image_path> [server_url]")
        print("Example: python script.py C:\\Users\\ASUS\\Desktop\\screenshot.png")
        return
    
    image_path = sys.argv[1]
    server_url = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8000"
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Image file '{image_path}' does not exist")
        return
    
    # Send to OmniParser
    result = send_to_omniparser(image_path, server_url)
    
    if result:
        print(f"\n✓ Processing completed in {result['latency']:.2f} seconds")
        print(f"\n📋 Parsed Content:")
        print("=" * 50)
        
        # Print parsed content
        content_list = result['parsed_content_list']
        if isinstance(content_list, list):
            for item in content_list:
                print(item)
        else:
            # If it's a string with newlines
            print(content_list)
        
        # Save annotated image
        image_name = Path(image_path).stem
        output_path = f"{image_name}_annotated.png"
        save_annotated_image(result['som_image_base64'], output_path)
        
        # Optionally save full response as JSON
        json_output_path = f"{image_name}_result.json"
        with open(json_output_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Full response saved to: {json_output_path}")

if __name__ == "__main__":
    main()