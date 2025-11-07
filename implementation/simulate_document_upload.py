import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from implementation.state_manager import StateManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Simulate document upload')
    parser.add_argument('--state_file', type=str, default='implementation/conversation_state.json',
                        help='Path to the conversation state JSON file')
    parser.add_argument('--document_type', type=str, default='income_proof',
                        help='Type of document to upload')
    parser.add_argument('--filename', type=str, default='salary_slip.pdf',
                        help='Filename of the document')
    return parser.parse_args()

def simulate_document_upload(state_file, document_type, filename):
    """Simulate uploading a document
    
    Args:
        state_file: Path to the conversation state JSON file
        document_type: Type of document to upload
        filename: Filename of the document
    """
    # Initialize state manager
    state_manager = StateManager(state_file)
    
    # Load current state
    state = state_manager.load_state()
    
    # Initialize document_uploads if it doesn't exist
    if not hasattr(state, 'document_uploads') or state.document_uploads is None:
        state.document_uploads = {}
    
    # Create a document upload
    doc_id = f"doc_{int(time.time())}"
    state.document_uploads[doc_id] = {
        "type": document_type,
        "filename": filename,
        "upload_time": datetime.now().isoformat(),
        "status": "uploaded",
        "verified": False
    }
    
    # Add a message about the upload
    message = f"I've uploaded my {filename} as {document_type}."
    if hasattr(state, 'add_message'):
        state.add_message("user", message)
    elif hasattr(state, 'messages'):
        if state.messages is None:
            state.messages = []
        state.messages.append({"role": "user", "content": message})
    
    # Save the updated state
    state_manager.save_state(state)
    logger.info(f"Simulated document upload with ID: {doc_id}")
    
    return doc_id

def main():
    """Main function"""
    args = parse_arguments()
    
    # Ensure state file path is absolute
    state_file = os.path.abspath(args.state_file)
    logger.info(f"Using state file: {state_file}")
    
    # Simulate document upload
    doc_id = simulate_document_upload(state_file, args.document_type, args.filename)
    logger.info(f"Document uploaded with ID: {doc_id}")
    
    # Monitor state changes
    logger.info("Monitoring state changes...")
    state_manager = StateManager(state_file)
    
    for _ in range(30):  # Check for 30 seconds
        time.sleep(1)
        current_state = state_manager.load_state()
        
        # Check for document verification
        if hasattr(current_state, 'verification_status') and current_state.verification_status.get('income_proof_verified') is not None:
            verified = current_state.verification_status.get('income_proof_verified')
            confidence = current_state.verification_status.get('income_proof_confidence', 0)
            status = "verified" if verified else "rejected"
            logger.info(f"Document {status} with confidence score: {confidence}")
            
            # Check for sanction letter if document is verified
            if verified and hasattr(current_state, 'sanction_letter_id') and current_state.sanction_letter_id:
                logger.info(f"Sanction letter generated with ID: {current_state.sanction_letter_id}")
                break
            elif verified:
                logger.info("Document verified, waiting for sanction letter...")
            else:
                logger.info("Document rejected, no sanction letter will be generated.")
                break

if __name__ == "__main__":
    main()