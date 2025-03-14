# tests/test_file_watching.py
import os
import pytest
import time
import tempfile
from tools.file_watcher import watch_folder, read_file

def test_file_reading():
    """Test that files can be read correctly."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write("This is a test thought.")
        temp_file_path = temp_file.name
    
    try:
        # Read the file
        thought_object = read_file(temp_file_path)
        
        # Check that the thought object is created correctly
        assert thought_object is not None
        assert thought_object["content"] == "This is a test thought."
        assert "timestamp" in thought_object
        assert "id" in thought_object
        assert thought_object["processing_stage"] == "capture"
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

def test_file_watcher_setup():
    """Test that file watcher is correctly set up."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a callback function that sets a flag when called
        callback_called = {"value": False}
        def callback(content):
            callback_called["value"] = True
        
        # Set up the file watcher
        observer = watch_folder(temp_dir, callback)
        
        try:
            # Give the observer time to start
            time.sleep(0.1)
            
            # Create a file in the watched directory
            with open(os.path.join(temp_dir, "test_thought.txt"), 'w') as f:
                f.write("This is a test thought.")
            
            # Give the observer time to process the file
            time.sleep(0.5)
            
            # Check that the callback was called
            assert callback_called["value"] == True
        finally:
            # Stop the observer
            observer.stop()
            observer.join()