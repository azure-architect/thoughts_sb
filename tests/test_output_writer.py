# tests/test_output_writer.py
import os
import json
import pytest
import tempfile  # Added this missing import
from tools.output_writer import write_result

def test_output_writing():
    """Test that processed thoughts can be written to files."""
    # Create a test thought
    thought = {
        "id": "test_thought_1",
        "timestamp": "2025-03-13T12:00:00",
        "original_filename": "test_thought.txt",
        "original_path": "/test/path/test_thought.txt",
        "content": "This is a test thought.",
        "processing_stage": "connect",
        "processing_history": [
            {"stage": "input", "timestamp": "2025-03-13T12:00:00"},
            {"stage": "capture", "timestamp": "2025-03-13T12:00:01"},
            {"stage": "contextualize", "timestamp": "2025-03-13T12:00:02"},
            {"stage": "clarify", "timestamp": "2025-03-13T12:00:03"},
            {"stage": "categorize", "timestamp": "2025-03-13T12:00:04"},
            {"stage": "crystallize", "timestamp": "2025-03-13T12:00:05"}
        ],
        "capture_results": "I have captured your thought.",
        "contextualize_results": "Domain: Test, Urgency: Low, Tone: Neutral",
        "clarify_results": "Your thought has been clarified.",
        "categorize_results": "This belongs to the test category.",
        "crystallize_results": "Action: Test this system.",
        "connect_results": "This connects to your testing framework."
    }
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write the thought to a file
        output_path = write_result(thought, temp_dir)
        
        # Check that the file was created
        assert os.path.exists(output_path)
        
        # Read the file and check its contents
        with open(output_path, 'r') as f:
            saved_thought = json.load(f)
        
        # Check that the saved thought matches the original
        assert saved_thought["id"] == thought["id"]
        assert saved_thought["content"] == thought["content"]
        assert saved_thought["processing_stage"] == thought["processing_stage"]
        assert len(saved_thought["processing_history"]) == len(thought["processing_history"])
        assert "capture_results" in saved_thought
        assert "connect_results" in saved_thought