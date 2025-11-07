# Test script for Sanction Letter Generator

import os
import sys
import json
from datetime import datetime
from typing import Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import SanctionLetterGenerator
from implementation.sanction_letter_generator import SanctionLetterGenerator
from implementation.master_agent import ConversationState

def main():
    # Initialize SanctionLetterGenerator
    print("Initializing SanctionLetterGenerator...")
    sanction_letter_generator = SanctionLetterGenerator()
    
    # Create a conversation state for testing
    print("Creating test conversation state...")
    state = ConversationState()
    
    # Set up state for an approved loan
    state.loan_details = {
        "loan_amount": 300000,
        "loan_tenure": 36,
        "interest_rate": 10.5,
        "purpose": "Home Renovation"
    }
    
    state.customer_details = {
        "customer_id": "TC001",
        "name": "Rahul Sharma",
        "address": "123 Main Street, Mumbai - 400001",
        "pre_approved_limit": 500000
    }
    
    state.underwriting_status = {
        "status": "approved",
        "decision": "APPROVED",
        "reason": "Amount within pre-approved limit",
        "interest_rate": 10.5,
        "calculated_emi": 9735.76,
        "underwriting_complete": True
    }
    
    # Process the state to generate sanction letter
    print("Generating sanction letter...")
    updated_state = sanction_letter_generator.process(state)
    
    # Print the documentation status
    print("\nDocumentation Status:")
    print(json.dumps(updated_state.documentation_status, indent=2))
    
    # Check if document was generated
    if updated_state.documentation_status.get("status") == "completed":
        doc_path = updated_state.documentation_status.get("document_path")
        print(f"\nSanction letter generated successfully at: {doc_path}")
        print(f"File exists: {os.path.exists(doc_path)}")
    else:
        print("\nFailed to generate sanction letter:")
        print(updated_state.documentation_status.get("reason"))

if __name__ == "__main__":
    main()