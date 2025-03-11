import importlib
import os
import pkgutil
import sys
import inspect
from pathlib import Path

def get_installed_package_location(package_name):
    """Find the installation location of a pip package."""
    try:
        package = importlib.import_module(package_name)
        package_path = os.path.dirname(inspect.getfile(package))
        return package_path
    except (ImportError, AttributeError) as e:
        print(f"Error: Package '{package_name}' not found or not properly installed. {e}")
        return None

def search_for_llm_classes(package_path):
    """Search for LLM-related classes in the package."""
    results = []
    excluded_dirs = {'__pycache__', 'tests', 'examples', 'docs', 'test'}
    search_terms = ["class LLM", "class Ollama"]
    
    for root, dirs, files in os.walk(package_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    for term in search_terms:
                        if term in content:
                            # Calculate relative path for import statement
                            rel_path = os.path.relpath(file_path, os.path.dirname(package_path))
                            module_path = rel_path.replace(os.sep, '.').replace('.py', '')
                            
                            # Extract the class definition for context
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if term in line:
                                    # Get context (5 lines before and after)
                                    start = max(0, i-5)
                                    end = min(len(lines), i+6)
                                    context = '\n'.join(lines[start:end])
                                    
                                    results.append({
                                        'file_path': file_path,
                                        'module_path': module_path,
                                        'class_name': term.split(' ')[1],
                                        'context': context
                                    })
                                    break
                                    
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return results

def find_possible_import_paths(crewai_path, class_name):
    """Try importing different modules to find the class."""
    import_paths = []
    
    # Common patterns for LLM-related modules
    patterns = [
        "llms",
        "llm",
        "agents",
        "models",
        "providers"
    ]
    
    for pattern in patterns:
        # Try direct import
        try:
            module_name = f"crewai.{pattern}"
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                import_paths.append(f"from {module_name} import {class_name}")
        except ImportError:
            pass
        
        # Try subdirectories
        pattern_path = os.path.join(crewai_path, pattern)
        if os.path.isdir(pattern_path):
            for root, dirs, files in os.walk(pattern_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, os.path.dirname(crewai_path))
                        module_path = rel_path.replace(os.sep, '.').replace('.py', '')
                        
                        try:
                            module = importlib.import_module(module_path)
                            if hasattr(module, class_name):
                                import_paths.append(f"from {module_path} import {class_name}")
                        except ImportError:
                            pass
    
    return import_paths

def check_crewai_version(package_path):
    """Try to determine the CrewAI version."""
    version_file = os.path.join(package_path, "__version__.py")
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    
    # Check in __init__.py
    init_file = os.path.join(package_path, "__init__.py")
    if os.path.exists(init_file):
        with open(init_file, 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    
    return "Unknown"

def main():
    # Find CrewAI package
    package_name = "crewai"
    package_path = get_installed_package_location(package_name)
    
    if not package_path:
        print("CrewAI package not found. Please make sure it's installed.")
        return
    
    print(f"Found CrewAI package at: {package_path}")
    version = check_crewai_version(package_path)
    print(f"CrewAI version: {version}")
    
    # Search for LLM-related classes
    print("\nSearching for LLM-related classes...")
    results = search_for_llm_classes(package_path)
    
    if not results:
        print("No LLM-related classes found. Trying alternative approach...")
        
        # Try importing specific modules directly
        print("\nTrying possible import paths:")
        import_paths = find_possible_import_paths(package_path, "LLM")
        import_paths.extend(find_possible_import_paths(package_path, "Ollama"))
        
        for path in import_paths:
            print(f"✓ Possible import: {path}")
        
        if not import_paths:
            print("Could not find any valid import paths for LLM or Ollama classes.")
            
            # Last resort: search for files with 'llm' in the name
            print("\nFiles containing 'llm' in their name:")
            for root, _, files in os.walk(package_path):
                for file in files:
                    if 'llm' in file.lower() and file.endswith('.py'):
                        rel_path = os.path.relpath(os.path.join(root, file), package_path)
                        print(f"- {rel_path}")
    else:
        print(f"\nFound {len(results)} LLM-related classes:")
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Class: {result['class_name']}")
            print(f"   File: {result['file_path']}")
            print(f"   Import path: from {result['module_path']} import {result['class_name']}")
            print(f"   Context:")
            print("   " + "\n   ".join(result['context'].split('\n')))
    
    # Provide examples for common patterns
    print("\nBased on common patterns in other libraries, try the following import paths:")
    print("1. from crewai.llms import LLM")
    print("2. from crewai.llms import Ollama")
    print("3. from crewai.core.llm import LLM")
    print("4. import crewai as crew\n   llm = crew.llms.LLM(...)")

if __name__ == "__main__":
    main()