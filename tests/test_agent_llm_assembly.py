# test_agent_llm_assembly.py
import os
import sys
import yaml
import logging
from pprint import pprint

# Add the project root to the Python path so 'tools' can be imported
# This assumes the test script is in a 'tests' directory at the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Go up one level to the project root
sys.path.append(project_root)

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock the LLM handler to capture which model is used
class MockLLMHandler:
    def __init__(self):
        self.called_configs = []
    
    def communicate_with_llm(self, prompt, llm_config_name):
        self.called_configs.append(llm_config_name)
        logger.info(f"LLM call made with config: {llm_config_name}")
        return f"Response from {llm_config_name} model"

# Load agent and LLM configurations
def load_configurations():
    with open(os.path.join(project_root, 'config/agents.yaml'), 'r') as f:
        agents_config = yaml.safe_load(f)
    
    with open(os.path.join(project_root, 'config/llms.yaml'), 'r') as f:
        llms_config = yaml.safe_load(f)
    
    with open(os.path.join(project_root, 'config/prompts.yaml'), 'r') as f:
        prompts_config = yaml.safe_load(f)
    
    return agents_config, llms_config.get('llm_configs', {}), prompts_config

class Agent:
    def __init__(self, agent_id, config):
        self.id = agent_id
        self.name = config.get('role', f"{agent_id.capitalize()} Agent")
        self.llm_config = config.get('llm_config')
        self.verbose = config.get('verbose', False)

def test_agent_llm_selection():
    """Test that each agent uses its specified LLM model"""
    logger.info("Loading configurations...")
    agents_config, llm_configs, prompts_config = load_configurations()
    
    # Initialize agents
    agents = {}
    for agent_id, config in agents_config['agents'].items():
        agents[agent_id] = Agent(agent_id, config)
    
    # Extract prompt templates
    prompt_keys = {
        'capture': 'capture_prompt_template',
        'contextualize': 'contextualize_prompt_template',
        'clarify': 'clarify_prompt_template',
        'categorize': 'categorize_prompt_template',
        'crystallize': 'crystallize_prompt_template',
        'connect': 'connect_prompt_template'
    }
    
    prompt_templates = {}
    for agent_id, template_key in prompt_keys.items():
        if template_key in prompts_config:
            prompt_templates[agent_id] = prompts_config[template_key]
    
    # Create a mock LLM handler
    mock_handler = MockLLMHandler()
    
    # Create a simple test thought
    test_thought = {
        "id": "test-thought-001",
        "content": "This is a test thought to verify agent-specific LLM selection.",
        "processing_stage": "init",
        "processing_history": []
    }
    
    # Import the real document processor but mock the LLM handler
    try:
        from tools.document_processor import process_with_agent
        import tools.llm_handler
        
        # Save original communicate function if it exists
        if hasattr(tools.llm_handler, 'communicate_with_llm'):
            original_communicate = tools.llm_handler.communicate_with_llm
            tools.llm_handler.communicate_with_llm = mock_handler.communicate_with_llm
        else:
            # If the function doesn't exist yet, just add our mock
            tools.llm_handler.communicate_with_llm = mock_handler.communicate_with_llm
            original_communicate = None
        
        # Process the thought with each agent
        logger.info("=== Testing Agent-Specific LLM Selection ===")
        
        for agent_id, agent in agents.items():
            logger.info(f"Testing {agent_id} agent with LLM config: {agent.llm_config}")
            
            # Process the thought with this agent if we have a template
            if agent_id in prompt_templates:
                process_with_agent(
                    test_thought.copy(),
                    agent,
                    agent.name,
                    agent_id,
                    prompt_templates
                )
            else:
                logger.warning(f"Skipping {agent_id} - no prompt template found")
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error(f"Current sys.path: {sys.path}")
        logger.error(f"Looking for module in: {os.path.join(project_root, 'tools')}")
        # List files in the tools directory to help debug
        tools_dir = os.path.join(project_root, 'tools')
        if os.path.exists(tools_dir):
            logger.info(f"Files in tools directory: {os.listdir(tools_dir)}")
        else:
            logger.error(f"Tools directory not found: {tools_dir}")
        return
    finally:
        # Restore the original function if we replaced it
        if 'tools.llm_handler' in sys.modules and original_communicate:
            tools.llm_handler.communicate_with_llm = original_communicate
    
    # Verify results
    logger.info("=== Test Results ===")
    for i, (agent_id, agent) in enumerate(agents.items()):
        if i < len(mock_handler.called_configs):
            logger.info(f"Agent: {agent_id} - Expected: {agent.llm_config} - Used: {mock_handler.called_configs[i]}")
            assert agent.llm_config == mock_handler.called_configs[i], f"Agent {agent_id} used incorrect LLM config"
        else:
            logger.error(f"No LLM call detected for agent: {agent_id}")
    
    logger.info("All agents used their correct LLM configurations!" if len(mock_handler.called_configs) == len(agents) else "Some agents did not use their correct LLM configurations!")

if __name__ == "__main__":
    test_agent_llm_selection()