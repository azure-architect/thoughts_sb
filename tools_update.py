import os
import re

# Define the target directory for the new files
TOOLS_DIR = "tools"
CURRENT_TOOLS_PATH = os.path.join(TOOLS_DIR, "tools.py")

# Ensure the tools directory exists
os.makedirs(TOOLS_DIR, exist_ok=True)

# Define mapping of functions to their respective files
tool_files = {
    "file_watcher.py": [
        "CaptureHandler", 
        "process_existing_files", 
        "watch_folder", 
        "read_file"
    ],
    "llm_handler.py": [
        "communicate_with_llm"
    ],
    "document_processor.py": [
        "process_with_agent",
        "pass_to_next_agent"
    ],
    "output_writer.py": [
        "write_result"
    ]
}

# Check if the tools.py file exists
if not os.path.exists(CURRENT_TOOLS_PATH):
    print(f"Error: Could not find {CURRENT_TOOLS_PATH}")
    print("Make sure you're running this script from the project root directory")
    exit(1)

# Read the original tools.py file
with open(CURRENT_TOOLS_PATH, "r") as f:
    source_code = f.read()

# Extract imports
import_pattern = r"^import.*$|^from.*$"
imports = re.findall(import_pattern, source_code, re.MULTILINE)
imports_text = "\n".join(imports)

# Function to extract a function/class definition from the source code
def extract_definition(name):
    # Match class or function definition
    if name.startswith("class "):
        class_name = name.replace("class ", "")
        pattern = rf"class {class_name}.*?(?=^class|\Z)"
    else:
        pattern = rf"def {name}\(.*?(?=^def|\Z)"
    
    match = re.search(pattern, source_code, re.DOTALL | re.MULTILINE)
    if match:
        return match.group(0)
    return None

# Create __init__.py to expose all functions
init_content = imports_text + "\n\n"
init_content += "# Re-export all tools\n"
init_exports = []

# Process each file and its functions
for file_name, functions in tool_files.items():
    file_path = os.path.join(TOOLS_DIR, file_name)
    
    # Start with imports
    file_content = imports_text + "\n\n"
    
    # Add each function to the file
    for func_name in functions:
        definition = extract_definition(func_name)
        if definition:
            file_content += definition + "\n\n"
            init_exports.append(func_name)
        else:
            print(f"Warning: Could not find definition for {func_name}")
    
    # Write the file
    with open(file_path, "w") as f:
        f.write(file_content)
    print(f"Created {file_path}")

# Create the __init__.py file
init_content += "from .file_watcher import CaptureHandler, process_existing_files, watch_folder, read_file\n"
init_content += "from .llm_handler import communicate_with_llm\n"
init_content += "from .document_processor import process_with_agent, pass_to_next_agent\n"
init_content += "from .output_writer import write_result\n\n"
init_content += "__all__ = [\n    "
init_content += ",\n    ".join([f"'{func}'" for func in init_exports])
init_content += "\n]\n"

init_path = os.path.join(TOOLS_DIR, "__init__.py")
with open(init_path, "w") as f:
    f.write(init_content)
print(f"Created {init_path}")

print("Finished extracting tools to separate files")