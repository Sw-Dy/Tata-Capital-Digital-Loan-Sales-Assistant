import os
import sys
import time
import json
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from implementation.state_manager import StateManager
from implementation.conversation_state import ConversationState, Stage, Decision

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_test_state():
    """Create a test conversation state with required fields"""
    state = ConversationState()
    
    # Set customer details
    state.customer_details = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "address": "123 Main St, City, Country",
        "id_proof": "ABCDE1234F",
        "employment_type": "Salaried"
    }
    
    # Set loan details
    state.loan_details = {
        "loan_amount": 500000,
        "loan_term": 60,
        "loan_purpose": "Home Renovation",
        "interest_rate": 8.5,
        "emi": 10250
    }
    
    # Set extracted info
    state.extracted_info = {
        "monthly_income": 75000,
        "existing_emi": 15000,
        "credit_score": 750
    }
    
    # Set verification status
    state.verification_status = {
        "id_verified": True,
        "address_verified": True,
        "income_proof_verified": False,
        "income_proof_confidence": 0.0
    }
    
    # Set underwriting status
    state.underwriting_status = {
        "status": "pending",
        "decision": None,
        "remarks": None
    }
    
    # Set documentation status
    state.documentation_status = {
        "status": "pending",
        "document_path": None
    }
    
    # Initialize document uploads
    state.document_uploads = {}
    
    # Add some messages
    state.messages = [
        {"role": "system", "content": "You are a helpful loan assistant."},
        {"role": "user", "content": "I need a home renovation loan."},
        {"role": "assistant", "content": "I'll help you with your home renovation loan application."}
    ]
    
    # Set conversation stage
    state.conversation_stage = "document_collection"
    
    return state

def simulate_document_upload(state_manager):
    """Simulate uploading an income proof document"""
    # Load current state
    state = state_manager.load_state()
    
    # Create a document upload
    doc_id = f"doc_{int(time.time())}"
    state.document_uploads[doc_id] = {
        "type": "income_proof",
        "filename": "salary_slip.pdf",
        "upload_time": datetime.now().isoformat(),
        "status": "uploaded",
        "verified": False
    }
    
    # Add a message about the upload
    if hasattr(state, 'add_message'):
        state.add_message("user", "I've uploaded my salary slip as income proof.")
    else:
        state.messages.append({"role": "user", "content": "I've uploaded my salary slip as income proof."})
    
    # Save the updated state
    state_manager.save_state(state)
    logger.info(f"Simulated document upload with ID: {doc_id}")
    
    return doc_id

def main():
    """Main test function"""
    # Initialize state manager with a test file
    state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_conversation_state.json")
    state_manager = StateManager(state_file)
    
    # Create and save initial test state
    initial_state = setup_test_state()
    state_manager.save_state(initial_state)
    logger.info(f"Initial test state saved to {state_file}")
    
    # Simulate document upload
    doc_id = simulate_document_upload(state_manager)
    
    # Start parallel processes
    logger.info("Starting document verification process...")
    os.system(f"start python {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'document_verification.py')} --state_file={state_file}")
    
    logger.info("Starting sanction letter trigger process...")
    os.system(f"start python {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sanction_letter_trigger.py')} --state_file={state_file}")
    
    # Monitor state changes
    logger.info("Monitoring state changes...")
    for _ in range(30):  # Check for 30 seconds
        time.sleep(1)
        current_state = state_manager.load_state()
        
        # Check for document verification
        if hasattr(current_state, 'verification_status') and current_state.verification_status.get('income_proof_verified'):
            confidence = current_state.verification_status.get('income_proof_confidence', 0)
            logger.info(f"Document verified with confidence score: {confidence}")
        
        # Check for sanction letter
        if hasattr(current_state, 'sanction_letter_id') and current_state.sanction_letter_id:
            logger.info(f"Sanction letter generated with ID: {current_state.sanction_letter_id}")
            break
    
    # Final state check
    final_state = state_manager.load_state()
    logger.info("Final state summary:")
    logger.info(f"Document verification status: {final_state.verification_status if hasattr(final_state, 'verification_status') else 'N/A'}")
    logger.info(f"Sanction letter ID: {final_state.sanction_letter_id if hasattr(final_state, 'sanction_letter_id') else 'N/A'}")
    
    # Print messages
    logger.info("Conversation messages:")
    for msg in final_state.messages[-5:]:  # Show last 5 messages
        logger.info(f"{msg['role']}: {msg['content']}")

if __name__ == "__main__":
    main()