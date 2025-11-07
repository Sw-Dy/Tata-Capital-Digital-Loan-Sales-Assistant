#!/usr/bin/env python

import os
import sys
import time
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run the parallel processes test"""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the state file path
    state_file = os.path.join(current_dir, "test_conversation_state.json")
    
    # Create a clean state file
    logger.info("Creating a clean state file...")
    subprocess.run([sys.executable, os.path.join(current_dir, "test_parallel_processing.py")])
    
    # Start parallel processes
    logger.info("Starting parallel processes...")
    doc_verification_process = subprocess.Popen(
        [sys.executable, os.path.join(current_dir, "document_verification.py"), "--state_file", state_file]
    )
    
    sanction_letter_process = subprocess.Popen(
        [sys.executable, os.path.join(current_dir, "sanction_letter_trigger.py"), "--state_file", state_file]
    )
    
    # Wait a moment for processes to start
    time.sleep(2)
    
    # Simulate document upload
    logger.info("Simulating document upload...")
    subprocess.run(
        [sys.executable, os.path.join(current_dir, "simulate_document_upload.py"), "--state_file", state_file]
    )
    
    # Wait for processes to complete their work
    logger.info("Test complete. Waiting for 5 seconds before terminating processes...")
    time.sleep(5)
    
    # Terminate processes
    doc_verification_process.terminate()
    sanction_letter_process.terminate()
    
    logger.info("All processes terminated. Check the logs for results.")

if __name__ == "__main__":
    main()