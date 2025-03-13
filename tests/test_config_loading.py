# tests/test_config_loading.py
import os
import tempfile
import pytest
import yaml
from utils.env_loader import load_env_vars

# tests/test_config_loading.py - modified test
# tests/test_config_loading.py - modified test
def test_env_variable_loading(monkeypatch):
    """Test that environment variables are properly loaded."""
    # Use pytest's monkeypatch to ensure clean environment
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    
    # Create a temporary .env file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_env:
        temp_env.write("OLLAMA_BASE_URL=http://test-ollama:11434\n")
        temp_env.write("GEMINI_API_KEY=test-api-key\n")
        temp_env_path = temp_env.name
    
    try:
        # Load the environment variables
        load_env_vars(temp_env_path)
        
        # Check that variables were loaded correctly
        assert os.environ.get("OLLAMA_BASE_URL") == "http://test-ollama:11434"
        assert os.environ.get("GEMINI_API_KEY") == "test-api-key"
    finally:
        # Clean up the temporary file
        os.unlink(temp_env_path)

def test_yaml_config_loading():
    """Test that YAML configurations are properly loaded."""
    from main import load_config
    
    # Create a temporary YAML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_yaml:
        yaml_content = {
            "agents": {
                "test_agent": {
                    "role": "Test Agent",
                    "goal": "Testing",
                    "backstory": "Created for testing"
                }
            }
        }
        yaml.dump(yaml_content, temp_yaml)
        temp_yaml_path = temp_yaml.name
    
    try:
        # Load the configuration
        config = load_config(temp_yaml_path)
        
        # Check that configuration was loaded correctly
        assert "agents" in config
        assert "test_agent" in config["agents"]
        assert config["agents"]["test_agent"]["role"] == "Test Agent"
    finally:
        # Clean up the temporary file
        os.unlink(temp_yaml_path)

def test_merged_config_loading():
    """Test that multiple configurations are properly merged."""
    from main import load_configs
    
    # Create temporary YAML files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create agents config
        agents_path = os.path.join(temp_dir, "agents.yaml")
        with open(agents_path, 'w') as f:
            yaml.dump({"agents": {"test_agent": {"role": "Test Agent"}}}, f)
        
        # Create LLMs config
        llms_path = os.path.join(temp_dir, "llms.yaml")
        with open(llms_path, 'w') as f:
            yaml.dump({"llm_configs": {"test_llm": {"model": "test-model"}}}, f)
        
        # Create prompts config
        prompts_path = os.path.join(temp_dir, "prompts.yaml")
        with open(prompts_path, 'w') as f:
            yaml.dump({"capture_prompt_template": "Test template"}, f)
        
        # Create system config
        system_path = os.path.join(temp_dir, "system.yaml")
        with open(system_path, 'w') as f:
            yaml.dump({"folders": {"base": "/test/path"}}, f)
        
        # Load and merge configurations
        config = load_configs(agents_path, llms_path, prompts_path, system_path)
        
        # Check that configurations were merged correctly
        assert "agents" in config
        assert "llm_configs" in config
        assert "prompts" in config
        assert "folders" in config
        assert config["folders"]["base"] == "/test/path"