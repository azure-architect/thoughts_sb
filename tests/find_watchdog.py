#!/usr/bin/env python3
import os
import sys
import importlib
import inspect
import pkgutil
from types import ModuleType

def find_class_in_module(module, class_name, visited=None):
    """Recursively search for a class in a module and its submodules."""
    if visited is None:
        visited = set()
    
    if module.__name__ in visited:
        return None
    
    visited.add(module.__name__)
    
    # Check if the class exists directly in this module
    if hasattr(module, class_name):
        cls = getattr(module, class_name)
        if inspect.isclass(cls):
            return module.__name__, cls
    
    # Search in submodules if the module is a package
    if hasattr(module, '__path__'):
        for _, name, ispkg in pkgutil.iter_modules(module.__path__, module.__name__ + '.'):
            try:
                submodule = importlib.import_module(name)
                result = find_class_in_module(submodule, class_name, visited)
                if result:
                    return result
            except ImportError as e:
                print(f"Could not import {name}: {e}")
            except Exception as e:
                print(f"Error processing {name}: {e}")
    
    return None

def search_files_for_llm_class(directory):
    """Search .py files directly for LLM class definition."""
    results = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "class LLM" in content or "class Ollama" in content:
                            rel_path = os.path.relpath(filepath, directory)
                            results.append((filepath, rel_path))
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    return results

def find_crewai_llm_class():
    """Main function to find the LLM class in crewai package."""
    env_path = None
    
    # Try to find site-packages in the current environment
    for path in sys.path:
        if 'site-packages' in path and os.path.exists(path):
            env_path = path
            break
    
    if not env_path:
        print("Could not find site-packages directory")
        return
    
    print(f"Using site-packages at: {env_path}")
    
    # Find crewai package
    crewai_path = None
    for root, dirs, files in os.walk(env_path):
        if os.path.basename(root) == "crewai" and "__init__.py" in files:
            crewai_path = root
            break
    
    if not crewai_path:
        print("Could not find crewai package in the environment")
        return
    
    print(f"Found crewai package at: {crewai_path}")
    
    # First try to look for the file directly
    print("\nSearching for LLM class in .py files...")
    file_results = search_files_for_llm_class(crewai_path)
    
    if file_results:
        print(f"Found {len(file_results)} potential files containing LLM class:")
        for filepath, rel_path in file_results:
            print(f"\nExamining: {rel_path}")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract import lines
                import_lines = [line.strip() for line in content.split('\n') 
                              if line.strip().startswith(('import ', 'from ')) and not line.strip().startswith('#')]
                
                print("Imports in this file:")
                for imp in import_lines:
                    print(f"  {imp}")
                
                # Look for class definitions
                if "class LLM" in content:
                    print("\nFound 'class LLM' definition in this file")
                    
                    # Try to determine the module path from the file path
                    rel_path = rel_path.replace('/', '.').replace('\\', '.')
                    if rel_path.endswith('.py'):
                        rel_path = rel_path[:-3]
                    module_path = f"crewai.{rel_path}"
                    
                    print(f"Likely import path: from {module_path} import LLM")
                
                if "class Ollama" in content:
                    print("\nFound 'class Ollama' definition in this file")
                    
                    # Try to determine the module path from the file path
                    rel_path = rel_path.replace('/', '.').replace('\\', '.')
                    if rel_path.endswith('.py'):
                        rel_path = rel_path[:-3]
                    module_path = f"crewai.{rel_path}"
                    
                    print(f"Likely import path: from {module_path} import Ollama")
            except Exception as e:
                print(f"Error processing file content: {e}")
    else:
        print("No files found containing LLM class definition")
    
    # Try to import crewai package to examine it
    print("\nTrying to import crewai module to examine it...")
    sys.path.insert(0, os.path.dirname(crewai_path))
    try:
        crewai = importlib.import_module("crewai")
        print(f"Successfully imported crewai")
        
        # Check specific submodules where LLM might live
        likely_modules = [
            "crewai.llms", 
            "crewai.agents.llm", 
            "crewai.tools.llm",
            "crewai.utilities"
        ]
        
        for module_name in likely_modules:
            try:
                module = importlib.import_module(module_name)
                print(f"Checking module: {module_name}")
                
                # Check for LLM class
                if hasattr(module, "LLM"):
                    print(f"✓ Found LLM class in {module_name}")
                    print(f"Import with: from {module_name} import LLM")
                
                # Check for Ollama class
                if hasattr(module, "Ollama"):
                    print(f"✓ Found Ollama class in {module_name}")
                    print(f"Import with: from {module_name} import Ollama")
                    
                # List all exported classes
                classes = [name for name, obj in inspect.getmembers(module, inspect.isclass) 
                          if obj.__module__ == module.__name__]
                if classes:
                    print(f"Classes in {module_name}:")
                    for cls in classes:
                        print(f"  {cls}")
            except ImportError:
                print(f"Could not import {module_name}")
            except Exception as e:
                print(f"Error checking {module_name}: {e}")
                
    except ImportError as e:
        print(f"Error importing crewai: {e}")
        
if __name__ == "__main__":
    find_crewai_llm_class()