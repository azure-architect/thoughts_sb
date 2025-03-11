import os
import json
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CaptureHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        
    def on_created(self, event):
        # Skip directories and metadata files
        if event.is_directory or os.path.basename(event.src_path).startswith("meta_"):
            return
            
        # Process the file
        print(f"New file detected: {event.src_path}")
        content = read_file(event.src_path)
        if content:
            self.callback(content)

def watch_folder(folder_path, callback):
    """
    Watch a folder for new files and call the callback function when a new file is detected.
    
    Args:
        folder_path (str): Path to the folder to watch
        callback (function): Function to call when a new file is detected
    """
    event_handler = CaptureHandler(callback)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    
    print(f"Watching folder: {folder_path}")
    return observer

def read_file(file_path):
    """
    Read a file and create a dictionary object from its contents.
    
    Args:
        file_path (str): Path to the file to read
        
    Returns:
        dict: Dictionary containing the file content and metadata
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Create a dictionary with the content and basic metadata
    timestamp = datetime.now().isoformat()
    file_id = f"thought_{int(time.time())}"
    file_name = os.path.basename(file_path)
    
    thought_object = {
        "id": file_id,
        "timestamp": timestamp,
        "original_filename": file_name,
        "original_path": file_path,
        "content": content,
        "processing_stage": "capture",
        "processing_history": []
    }
    
    print(f"Read file: {file_name}")
    return thought_object

def process_with_agent(thought_object, agent, agent_name):
    """
    Process a thought object with an agent.
    
    Args:
        thought_object (dict): The thought object to process
        agent: The agent to process the thought object
        agent_name (str): The name of the agent (for logging)
        
    Returns:
        dict: The processed thought object
    """
    # Record the current stage in history
    thought_object["processing_history"].append({
        "stage": thought_object["processing_stage"],
        "timestamp": datetime.now().isoformat()
    })
    
    # Update the current processing stage
    thought_object["processing_stage"] = agent_name.lower()
    
    # Here you would typically use the agent to process the thought
    # For now, we'll just add a placeholder
    thought_object[f"{agent_name.lower()}_results"] = f"Processed by {agent_name}"
    
    print(f"Processed thought with {agent_name} agent")
    return thought_object

def pass_to_next_agent(thought_object, next_agent, next_agent_name):
    """
    Pass a thought object to the next agent.
    
    Args:
        thought_object (dict): The thought object to pass
        next_agent: The next agent to process the thought object
        next_agent_name (str): The name of the next agent (for logging)
        
    Returns:
        dict: The thought object (for chaining)
    """
    print(f"Passing thought to {next_agent_name} agent")
    return process_with_agent(thought_object, next_agent, next_agent_name)

def write_result(thought_object, output_folder):
    """
    Write the processed thought object to a file in the output folder.
    
    Args:
        thought_object (dict): The processed thought object
        output_folder (str): The folder to write the result to
        
    Returns:
        str: Path to the output file
    """
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Create a filename based on the thought ID
    output_filename = f"processed_{thought_object['id']}.json"
    output_path = os.path.join(output_folder, output_filename)
    
    # Write the thought object to a JSON file
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(thought_object, file, indent=2)
    
    print(f"Wrote result to: {output_path}")
    return output_path