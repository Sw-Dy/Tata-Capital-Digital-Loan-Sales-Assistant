import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run parallel processes for loan application system')
    parser.add_argument('--state_file', type=str, default='conversation_state.json',
                        help='Path to the conversation state JSON file')
    return parser.parse_args()

def start_processes(state_file):
    """Start all parallel processes
    
    Args:
        state_file: Path to the conversation state JSON file
    """
    # Get the implementation directory
    implementation_dir = Path(__file__).parent.absolute()
    
    # Start document verification process
    logger.info("Starting document verification process...")
    doc_verification_cmd = f"python {implementation_dir / 'document_verification.py'} --state_file={state_file}"
    doc_verification_process = subprocess.Popen(doc_verification_cmd, shell=True)
    
    # Start sanction letter trigger process
    logger.info("Starting sanction letter trigger process...")
    sanction_letter_cmd = f"python {implementation_dir / 'sanction_letter_trigger.py'} --state_file={state_file}"
    sanction_letter_process = subprocess.Popen(sanction_letter_cmd, shell=True)
    
    logger.info("All parallel processes started successfully")
    logger.info(f"Document verification process ID: {doc_verification_process.pid}")
    logger.info(f"Sanction letter trigger process ID: {sanction_letter_process.pid}")
    
    return doc_verification_process, sanction_letter_process

def main():
    """Main function"""
    args = parse_arguments()
    
    # Ensure state file path is absolute
    state_file = os.path.abspath(args.state_file)
    logger.info(f"Using state file: {state_file}")
    
    # Start processes
    processes = start_processes(state_file)
    
    try:
        logger.info("Processes are running in the background. Press Ctrl+C to stop.")
        # Keep the main process running
        while True:
            pass
    except KeyboardInterrupt:
        logger.info("Stopping processes...")
        for process in processes:
            if process.poll() is None:  # If process is still running
                process.terminate()
                logger.info(f"Process {process.pid} terminated")

if __name__ == "__main__":
    main()