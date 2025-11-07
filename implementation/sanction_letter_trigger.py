# Sanction Letter Trigger Script for Tata Capital Digital Loan Sales Assistant

import os
import sys
import json
import time
import logging
import argparse
from typing import Dict, List, Optional, Any, Union
import pandas as pd
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import sanction letter generator
from implementation.sanction_letter_generator import SanctionLetterGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('output', 'sanction_letter_trigger.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('sanction_letter_trigger')

class SanctionLetterTrigger:
    """Trigger for sanction letter generation based on complete verification and underwriting"""
    
    def __init__(self, state_file_path="conversation_state.json"):
        """Initialize the Sanction Letter Trigger
        
        Args:
            state_file_path: Path to the conversation state JSON file
        """
        self.state_file_path = state_file_path
        self.sanction_letter_generator = SanctionLetterGenerator()
        
        # Required fields for sanction letter generation
        self.required_customer_fields = [
            "customer_id", "name", "phone", "address", "pan", 
            "account_number", "ifsc_code", "bank_name"
        ]
        
        self.required_loan_fields = [
            "amount", "tenure", "purpose", "interest_rate", "emi"
        ]
        
        logger.info(f"Sanction Letter Trigger initialized with state file: {state_file_path}")
    
    def monitor_for_trigger(self, polling_interval=5):
        """Monitor for conditions to trigger sanction letter generation
        
        Args:
            polling_interval: Time in seconds between checks
        """
        logger.info("Starting sanction letter trigger monitoring")
        
        while True:
            try:
                # Check if state file exists
                if os.path.exists(self.state_file_path):
                    # Load conversation state
                    with open(self.state_file_path, 'r') as f:
                        state_data = json.load(f)
                    
                    # Check if conditions are met for sanction letter generation
                    if self._should_generate_sanction_letter(state_data):
                        logger.info("Conditions met for sanction letter generation, triggering...")
                        self._generate_sanction_letter(state_data)
                
                # Wait before checking again
                time.sleep(polling_interval)
            
            except KeyboardInterrupt:
                logger.info("Sanction letter trigger monitoring stopped")
                break
            except Exception as e:
                logger.error(f"Error in sanction letter trigger monitoring: {e}")
                time.sleep(polling_interval)
    
    def _should_generate_sanction_letter(self, state_data):
        """Check if conditions are met for sanction letter generation
        
        Args:
            state_data: The conversation state data
            
        Returns:
            Boolean indicating if sanction letter should be generated
        """
        # Check if sanction letter has already been generated
        if state_data.get("sanction_letter_id"):
            return False
        
        # Check verification status
        verification_status = state_data.get("verification_status", {})
        if not verification_status.get("verified", False):
            logger.info("Verification not complete, cannot generate sanction letter")
            return False
            
        # Check if income proof has been verified with confidence score >= 0.5
        if not verification_status.get("income_proof_verified", False) or \
           verification_status.get("income_proof_confidence", 0) < 0.5:
            logger.info(f"Income proof verification failed or confidence score too low: {verification_status.get('income_proof_confidence', 0)}")
            return False
        
        # Check income proof confidence score
        if verification_status.get("income_proof_confidence", 0.0) < 0.5:
            logger.info("Income proof confidence score below threshold, cannot generate sanction letter")
            return False
        
        # Check underwriting result
        underwriting_result = state_data.get("underwriting_result", {})
        if not underwriting_result.get("decision") in ["approved", "conditionally_approved"]:
            logger.info("Loan not approved, cannot generate sanction letter")
            return False
        
        # Check for required customer details
        customer_details = state_data.get("customer_details", {})
        for field in self.required_customer_fields:
            if not customer_details.get(field):
                logger.info(f"Missing required customer field: {field}, cannot generate sanction letter")
                return False
        
        # Check for required loan details
        loan_details = state_data.get("loan_details", {})
        for field in self.required_loan_fields:
            if not loan_details.get(field):
                logger.info(f"Missing required loan field: {field}, cannot generate sanction letter")
                return False
        
        # All conditions met
        logger.info("All conditions met for sanction letter generation")
        return True
    
    def _generate_sanction_letter(self, state_data):
        """Generate sanction letter using the SanctionLetterGenerator
        
        Args:
            state_data: The conversation state data
        """
        try:
            # Create a state object that matches the expected format for SanctionLetterGenerator
            from types import SimpleNamespace
            
            class ConversationState:
                def __init__(self, state_data):
                    self.customer_details = state_data.get("customer_details", {})
                    self.loan_details = state_data.get("loan_details", {})
                    self.underwriting_result = state_data.get("underwriting_result", {})
                    self.verification_status = state_data.get("verification_status", {})
                    self.documentation_status = {}
                    self.sanction_letter_id = None
                
                def add_message(self, role, content):
                    # Mock method to match expected interface
                    pass
            
            # Create state object
            state = ConversationState(state_data)
            
            # Generate sanction letter
            result_state = self.sanction_letter_generator.process(state)
            
            # Extract sanction letter ID and update state
            if result_state.documentation_status.get("document_path"):
                sanction_letter_id = result_state.documentation_status.get("document_path")
                state_data["sanction_letter_id"] = sanction_letter_id
                state_data["documentation_status"] = result_state.documentation_status
                
                logger.info(f"Sanction letter generated successfully: {sanction_letter_id}")
                
                # Save updated state
                with open(self.state_file_path, 'w') as f:
                    json.dump(state_data, f, indent=2)
            else:
                logger.error("Failed to generate sanction letter, no document path returned")
        
        except Exception as e:
            logger.error(f"Error generating sanction letter: {e}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Sanction Letter Trigger')
    parser.add_argument('--state_file', type=str, default='conversation_state.json',
                        help='Path to the conversation state JSON file')
    return parser.parse_args()

# Main execution
if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Create sanction letter trigger
    trigger = SanctionLetterTrigger(args.state_file)
    
    # Start monitoring for trigger conditions
    trigger.monitor_for_trigger()