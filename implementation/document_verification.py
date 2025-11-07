# Document Verification Script for Tata Capital Digital Loan Sales Assistant

import os
import sys
import json
import time
import random
import logging
import traceback
import argparse
from typing import Dict, List, Optional, Any, Union
import pandas as pd
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('output', 'document_verification.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('document_verification')

class DocumentVerificationAgent:
    """Document Verification Agent responsible for validating uploaded income proof documents"""
    
    def __init__(self, state_file_path="conversation_state.json"):
        """Initialize the Document Verification Agent
        
        Args:
            state_file_path: Path to the conversation state JSON file
        """
        self.state_file_path = state_file_path
        self.document_types = [
            "salary_slip",
            "bank_statement",
            "income_tax_return",
            "form_16",
            "business_financial_statement"
        ]
        
        # System prompt for the Document Verification Agent
        self.system_prompt = """
        You are a specialized Document Verification Agent for Tata Capital, a leading NBFC in India.
        Your role is to verify income proof documents uploaded by loan applicants and assign confidence scores.
        
        Follow these guidelines:
        1. Analyze uploaded documents for authenticity and completeness
        2. Verify income details match information provided in the application
        3. Assign confidence scores between 0.0 and 1.0 to each document
        4. Reject documents with confidence scores below 0.5
        5. Maintain strict compliance with regulatory requirements
        6. Protect customer privacy and data security
        7. Provide clear verification status updates
        
        Your goal is to ensure the integrity of income proof documentation while maintaining a smooth verification process.
        """
    
    def monitor_for_documents(self, polling_interval=5):
        """Monitor for new document uploads and process them
        
        Args:
            polling_interval: Time in seconds between checks for new documents
        """
        logger.info("Starting document verification monitoring")
        
        while True:
            try:
                # Check if state file exists
                if os.path.exists(self.state_file_path):
                    # Load conversation state
                    with open(self.state_file_path, 'r') as f:
                        state_data = json.load(f)
                    
                    # Check if there are documents to verify
                    if self._has_unverified_documents(state_data):
                        logger.info("Found unverified documents, processing...")
                        self._process_documents(state_data)
                    
                    # Check if verification is complete and update main state
                    self._update_verification_status(state_data)
                
                # Wait before checking again
                time.sleep(polling_interval)
            
            except KeyboardInterrupt:
                logger.info("Document verification monitoring stopped")
                break
            except Exception as e:
                logger.error(f"Error in document verification monitoring: {e}")
                time.sleep(polling_interval)
    
    def _has_unverified_documents(self, state_data):
        """Check if there are unverified documents in the state
        
        Args:
            state_data: The conversation state data
            
        Returns:
            Boolean indicating if there are unverified documents
        """
        # Check if documents exist in the state
        if "customer_details" not in state_data:
            return False
        
        customer_details = state_data.get("customer_details", {})
        
        # Check for uploaded documents without verification
        for doc_type in self.document_types:
            doc_key = f"{doc_type}_uploaded"
            verified_key = f"{doc_type}_verified"
            
            if customer_details.get(doc_key, False) and not customer_details.get(verified_key, False):
                return True
        
        return False
    
    def _process_documents(self, state_data):
        """Process unverified documents and assign confidence scores
        
        Args:
            state_data: The conversation state data
        """
        modified = False
        customer_details = state_data.get("customer_details", {})
        verification_results = {}
        overall_confidence = 0.0
        documents_processed = 0
        
        # Process each document type
        for doc_type in self.document_types:
            doc_key = f"{doc_type}_uploaded"
            verified_key = f"{doc_type}_verified"
            confidence_key = f"{doc_type}_confidence"
            
            if customer_details.get(doc_key, False) and not customer_details.get(verified_key, False):
                # Simulate document analysis with a random confidence score
                # In a real implementation, this would use OCR and ML to analyze the document
                confidence_score = self._analyze_document(doc_type, customer_details)
                
                # Update verification status
                verification_results[verified_key] = confidence_score >= 0.5
                verification_results[confidence_key] = confidence_score
                verification_results[f"{doc_type}_verification_time"] = datetime.now().isoformat()
                
                if confidence_score >= 0.5:
                    verification_results[f"{doc_type}_status"] = "approved"
                    logger.info(f"Document {doc_type} verified with confidence score: {confidence_score:.2f}")
                else:
                    verification_results[f"{doc_type}_status"] = "rejected"
                    logger.info(f"Document {doc_type} rejected with low confidence score: {confidence_score:.2f}")
                
                overall_confidence += confidence_score
                documents_processed += 1
                modified = True
        
        # Calculate overall confidence score
        if documents_processed > 0:
            overall_confidence = overall_confidence / documents_processed
            verification_results["income_proof_confidence"] = overall_confidence
            verification_results["income_proof"] = overall_confidence >= 0.5
            verification_results["income_proof_verification_time"] = datetime.now().isoformat()
            
            # Add a message to the conversation about verification result
            if "messages" not in state_data:
                state_data["messages"] = []
                
            if overall_confidence >= 0.5:
                state_data["messages"].append({
                    "role": "assistant",
                    "content": f"Your income proof documents have been verified successfully with an overall confidence score of {overall_confidence:.2f}."
                })
            else:
                state_data["messages"].append({
                    "role": "assistant",
                    "content": f"Your income proof documents could not be verified (confidence score: {overall_confidence:.2f}). Please upload clearer documents or different proofs of income."
                })
            
            logger.info(f"Overall income proof confidence: {overall_confidence:.2f}")
        
        # Update the state with verification results
        customer_details.update(verification_results)
        state_data["customer_details"] = customer_details
        
        # Save updated state if modified
        if modified:
            with open(self.state_file_path, 'w') as f:
                json.dump(state_data, f, indent=2)
            
        return modified
    
    def _analyze_document(self, doc_type, customer_details):
        """Analyze a document and return a confidence score
        
        Args:
            doc_type: The type of document being analyzed
            customer_details: Customer details from the conversation state
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # In a real implementation, this would use OCR and ML to analyze the document
        # For this simulation, we'll use a weighted random score based on document type
        
        # Base confidence is random between 0.4 and 0.9
        base_confidence = random.uniform(0.4, 0.9)
        
        # Adjust confidence based on document type (some documents are more reliable)
        if doc_type == "income_tax_return":
            # ITR is highly reliable
            confidence_modifier = random.uniform(0.1, 0.2)
        elif doc_type == "salary_slip":
            # Salary slips are quite reliable
            confidence_modifier = random.uniform(0.05, 0.15)
        elif doc_type == "bank_statement":
            # Bank statements are reliable but need more verification
            confidence_modifier = random.uniform(0.0, 0.1)
        elif doc_type == "form_16":
            # Form 16 is highly reliable
            confidence_modifier = random.uniform(0.1, 0.2)
        else:
            # Other documents may be less reliable
            confidence_modifier = random.uniform(-0.1, 0.1)
        
        # Calculate final confidence score (capped between 0.0 and 1.0)
        confidence_score = min(max(base_confidence + confidence_modifier, 0.0), 1.0)
        
        # Log the analysis
        logger.info(f"Analyzed {doc_type} with confidence score: {confidence_score:.2f}")
        
        return confidence_score
    
    def _update_verification_status(self, state_data):
        """Update the overall verification status in the state
        
        Args:
            state_data: The conversation state data
        """
        customer_details = state_data.get("customer_details", {})
        verification_status = state_data.get("verification_status", {})
        modified = False
        
        # Check if income proof has been verified
        if customer_details.get("income_proof") is True:
            verification_status["income_proof_verified"] = True
            verification_status["income_proof_confidence"] = customer_details.get("income_proof_confidence", 0.0)
            verification_status["income_proof_verification_time"] = customer_details.get("income_proof_verification_time")
            modified = True
            
            # Update overall verification status if all required verifications are complete
            if verification_status.get("customer_verified", False) and \
               verification_status.get("phone_verified", False) and \
               verification_status.get("address_verified", False) and \
               verification_status.get("account_details_verified", False):
                verification_status["verified"] = True
                verification_status["status"] = "completed"
                verification_status["completion_time"] = datetime.now().isoformat()
                logger.info("All verification steps completed successfully")
        
        # Update state with new verification status
        state_data["verification_status"] = verification_status
        
        # Save updated state if modified
        if modified:
            with open(self.state_file_path, 'w') as f:
                json.dump(state_data, f, indent=2)
            
        return modified

# Main execution
def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Document Verification Agent')
    parser.add_argument('--state_file', type=str, default='conversation_state.json',
                        help='Path to the conversation state JSON file')
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Create document verification agent
    doc_agent = DocumentVerificationAgent(args.state_file)
    
    # Start monitoring for documents
    doc_agent.monitor_for_documents()