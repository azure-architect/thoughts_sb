# main.py
import os
import sys
import yaml
import argparse
from typing import Dict, Any, Optional, List

# Add the project root to the Python path if needed
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from dotenv import load_dotenv
except ImportError:
    print("Warning: python-dotenv is not installed. Environment variables from .env file won't be loaded.")
    print("Install with: pip install python-dotenv")
    def load_dotenv(*args, **kwargs):
        pass

from adapters import create_adapter

def load_env_vars(env_path: str = None):
    """Load environment variables from .env file."""
    if env_path is None:
        # Try to find .env in the project root
        env_path = os.path.join(project_root, '.env')
    
    # Load environment variables from .env file
    load_dotenv(env_path)
    
    # Check for OLLAMA_BASE_URL
    if not os.getenv("OLLAMA_BASE_URL"):
        os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {config_path}: {e}")
        return {}

def load_configs(agents_path: str = "config/agents.yaml", 
                llm_path: str = "config/llm_configs.yaml") -> Dict[str, Any]:
    """Load and merge multiple configuration files."""
    agents_config = load_config(agents_path)
    llm_configs = load_config(llm_path)
    
    # Create a merged config
    merged_config = {
        "agents": agents_config.get("agents", {}),
        "folders": agents_config.get("folders", {}),
        "llm_configs": llm_configs
    }
    
    return merged_config

def get_llm_config(config: Dict[str, Any], llm_name: str) -> Dict[str, Any]:
    """Get LLM configuration by name."""
    llm_configs = config.get("llm_configs", {})
    llm_config = llm_configs.get(llm_name, llm_configs.get("default", {}))
    
    if not llm_config:
        print(f"Warning: LLM config '{llm_name}' not found, using default config")
        
    return llm_config

def process_thought(thought_content: str, agent_name: str, config: Dict[str, Any]) -> str:
    """Process a thought using the specified agent and its LLM configuration."""
    # Get agent config
    agents_config = config.get("agents", {})
    agent_config = agents_config.get(agent_name, {})
    
    if not agent_config:
        return f"Error: Agent '{agent_name}' not found in configuration."
    
    # Get LLM config for this agent
    llm_name = agent_config.get("llm", "default")
    llm_config = get_llm_config(config, llm_name)
    
    # Create adapter from LLM config
    adapter_type = llm_config.get("adapter", "ollama")
    adapter = create_adapter(adapter_type)
    adapter.initialize(llm_config)
    
    try:
        # Get the agent's prompt template and format it with the thought content
        prompt_template = agent_config.get("prompt_template", "")
        prompt = prompt_template.format(thought_content=thought_content)
        
        is_verbose = agent_config.get("verbose", False)
        if is_verbose:
            print(f"\nPrompt for {agent_name}:")
            print("-" * 50)
            print(prompt)
            print("-" * 50)
        
        # Generate response using the adapter
        response = adapter.generate(
            prompt=prompt,
            temperature=llm_config.get("temperature", 0.7),
            max_tokens=llm_config.get("max_tokens", 1000)
        )
        
        return response
    except Exception as e:
        print(f"Error processing thought with {agent_name} agent: {str(e)}")
        return f"Error: {str(e)}"
    finally:
        adapter.close()

def process_thought_pipeline(initial_thought: str, config: Dict[str, Any], 
                           agents: Optional[List[str]] = None) -> Dict[str, str]:
    """Process a thought through multiple agents and return results."""
    if agents is None:
        agents = ["capture", "contextualize", "clarify", "categorize", "crystallize", "connect"]
    
    results = {}
    current_thought = initial_thought
    
    for agent_name in agents:
        print(f"\n== Processing with {agent_name.upper()} agent ==")
        result = process_thought(current_thought, agent_name, config)
        results[agent_name] = result
        
        print(f"Result from {agent_name}:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        # Use this result as input to the next agent
        current_thought = result
    
    return results

def interactive_mode(config: Dict[str, Any]):
    """Run in interactive mode, allowing the user to enter thoughts."""
    print("\n=== Thought Processing System (Interactive Mode) ===")
    print("Enter your thoughts, or type 'exit' to quit.")
    
    while True:
        thought = input("\nEnter a thought: ")
        if thought.lower() in ('exit', 'quit', 'q'):
            break
        
        process_thought_pipeline(thought, config)

def main():
    parser = argparse.ArgumentParser(description="Thought Processing System")
    parser.add_argument("--thought", type=str, help="Thought to process")
    parser.add_argument("--agents", type=str, help="Comma-separated list of agents to use")
    parser.add_argument("--agents-config", type=str, default="config/agents.yaml", 
                        help="Path to agents configuration file")
    parser.add_argument("--llm-config", type=str, default="config/llm_configs.yaml",
                        help="Path to LLM configuration file")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--env", type=str, help="Path to .env file")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_env_vars(args.env)
    
    # Load configuration
    config = load_configs(args.agents_config, args.llm_config)
    
    if args.interactive:
        interactive_mode(config)
    elif args.thought:
        agents = args.agents.split(",") if args.agents else None
        process_thought_pipeline(args.thought, config, agents)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()