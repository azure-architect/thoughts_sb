import importlib
import inspect
import pkgutil
import sys
import os

def explore_module(module_name):
    try:
        module = importlib.import_module(module_name)
        print(f"\nExploring module: {module_name}")
        
        # List all attributes
        attrs = [attr for attr in dir(module) if not attr.startswith('_')]
        
        # Separate classes, functions and variables
        classes = []
        functions = []
        variables = []
        
        for attr in attrs:
            try:
                value = getattr(module, attr)
                if inspect.isclass(value):
                    classes.append(attr)
                elif inspect.isfunction(value):
                    functions.append(attr)
                else:
                    variables.append(attr)
            except Exception as e:
                print(f"Error examining {attr}: {e}")
        
        if classes:
            print("Classes:")
            for cls in classes:
                print(f"  - {cls}")
        
        if functions:
            print("Functions:")
            for func in functions:
                print(f"  - {func}")
        
        if variables:
            print("Variables/imports:")
            for var in variables:
                print(f"  - {var}")
        
        # If no attributes found
        if not attrs:
            print("No public attributes found.")
        
        # Check for submodules
        if hasattr(module, '__path__'):
            print("\nSubmodules:")
            for _, submodule_name, ispkg in pkgutil.iter_modules(module.__path__, module.__name__ + '.'):
                print(f"  - {submodule_name}")
                
    except ImportError as e:
        print(f"Error importing {module_name}: {e}")
    except Exception as e:
        print(f"Error exploring {module_name}: {e}")

def main():
    # Start with crewai
    print("Exploring CrewAI package")
    
    # Try importing crewai to see what's available
    try:
        import crewai
        
        # Get initial variables
        print("Available in crewai:")
        for name in dir(crewai):
            if not name.startswith('_'):
                print(f"  - {name}")
        
        # Explore base modules
        modules_to_check = [
            "crewai",
            "crewai.agents", 
            "crewai.tasks",
            "crewai.tools",
            "crewai.crew"
        ]
        
        # Additional modules that might contain LLM functionality
        additional_modules = [
            "crewai.llms",
            "crewai.models",
            "crewai.utilities",
            "crewai.core"
        ]
        
        # Check main modules first
        for module_name in modules_to_check:
            explore_module(module_name)
        
        # Try additional modules
        for module_name in additional_modules:
            try:
                explore_module(module_name)
            except ImportError:
                # Skip if not found
                pass
                
        # Specifically check for Ollama
        print("\nSearching for Ollama class...")
        for finder, name, ispkg in pkgutil.iter_modules():
            if "crewai" in name:
                try:
                    module = importlib.import_module(name)
                    if hasattr(module, "Ollama"):
                        print(f"Found Ollama in {name}")
                        print(f"Import with: from {name} import Ollama")
                except ImportError:
                    pass
        
    except ImportError:
        print("CrewAI package not found. Please make sure it's installed.")
    
    # Check for langchain integration - CrewAI might use langchain for LLM support
    try:
        import langchain
        print("\nLangchain is installed. CrewAI might use Langchain for LLM integration.")
        
        try:
            from langchain.llms import Ollama
            print("You can use Langchain's Ollama integration: from langchain.llms import Ollama")
        except ImportError:
            pass
    except ImportError:
        print("\nLangchain is not installed.")

if __name__ == "__main__":
    main()