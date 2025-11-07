# State Manager for Tata Capital Digital Loan Sales Assistant

import os
import sys
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('output', 'state_manager.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('state_manager')

class StateManager:
    """Manages the conversation state persistence between the main agent and parallel processes"""
    
    def __init__(self, state_file_path="conversation_state.json"):
        """Initialize the State Manager
        
        Args:
            state_file_path: Path to the conversation state JSON file
        """
        self.state_file_path = state_file_path
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(self.state_file_path)) if os.path.dirname(self.state_file_path) else '.', exist_ok=True)
    
    def save_state(self, state):
        """Save the conversation state to a JSON file
        
        Args:
            state: The conversation state object from the Master Agent
        """
        try:
            # Convert state object to dictionary
            state_dict = self._state_to_dict(state)
            
            # Add timestamp for tracking updates
            state_dict['last_updated'] = datetime.now().isoformat()
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.state_file_path), exist_ok=True)
            
            # Save state to file
            with open(self.state_file_path, 'w') as f:
                json.dump(state_dict, f, indent=2)
            
            logger.info(f"Saved conversation state to {self.state_file_path}")
        
        except Exception as e:
            logger.error(f"Error saving conversation state: {e}")
            traceback.print_exc()
    
    def load_state(self, state=None):
        """Load the conversation state from a JSON file and update the state object
        
        Args:
            state: The conversation state object to update
            
        Returns:
            Updated conversation state object
        """
        try:
            # Check if state file exists
            if not os.path.exists(self.state_file_path):
                logger.warning(f"State file {self.state_file_path} does not exist, using current state")
                return state
            
            # Load state from file
            with open(self.state_file_path, 'r') as f:
                state_dict = json.load(f)
            
            # Update state object with loaded data
            if state is None:
                # Import here to avoid circular imports
                from conversation_state import ConversationState
                state = ConversationState()
                
            self._update_state_from_dict(state, state_dict)
            
            logger.info(f"Loaded conversation state from {self.state_file_path}")
            
            return state
        
        except Exception as e:
            logger.error(f"Error loading conversation state: {e}")
            traceback.print_exc()
            return state
    
    def _state_to_dict(self, state):
        """Convert a conversation state object to a dictionary
        
        Args:
            state: The conversation state object
            
        Returns:
            Dictionary representation of the state
        """
        state_dict = {
            "customer_details": state.customer_details,
            "loan_details": state.loan_details,
            "extracted_info": state.extracted_info,
            "messages": state.messages,
            "conversation_stage": state.conversation_stage,
            "decision": state.decision
        }
        
        # Add verification status if it exists
        if hasattr(state, 'verification_status') and state.verification_status:
            state_dict["verification_status"] = state.verification_status
        
        # Add underwriting result if it exists
        if hasattr(state, 'underwriting_result') and state.underwriting_result:
            state_dict["underwriting_result"] = state.underwriting_result
        
        # Add documentation status if it exists
        if hasattr(state, 'documentation_status') and state.documentation_status:
            state_dict["documentation_status"] = state.documentation_status
        
        # Add sanction letter ID if it exists
        if hasattr(state, 'sanction_letter_id') and state.sanction_letter_id:
            state_dict["sanction_letter_id"] = state.sanction_letter_id
            
        # Add document uploads if it exists
        if hasattr(state, 'document_uploads') and state.document_uploads:
            state_dict["document_uploads"] = state.document_uploads
            
        # Add income proof verification if it exists
        if hasattr(state, 'income_proof_verification') and state.income_proof_verification:
            state_dict["income_proof_verification"] = state.income_proof_verification
        
        return state_dict
    
    def _update_state_from_dict(self, state, state_dict):
        """Update a conversation state object from a dictionary
        
        Args:
            state: The conversation state object to update
            state_dict: Dictionary containing state data
        """
        # Special handling for document uploads
        if "document_uploads" in state_dict and hasattr(state, 'document_uploads'):
            # Merge document uploads
            if state.document_uploads is None:
                state.document_uploads = {}
                
            for doc_id, doc_info in state_dict["document_uploads"].items():
                state.document_uploads[doc_id] = doc_info
        
        # Special handling for income proof verification
        if "income_proof_verification" in state_dict:
            setattr(state, 'income_proof_verification', state_dict["income_proof_verification"])
            
            # Update verification status if it exists
            if hasattr(state, 'verification_status'):
                if state.verification_status is None:
                    state.verification_status = {}
                    
                state.verification_status['income_proof_verified'] = \
                    state_dict['income_proof_verification'].get('status') == 'verified'
                    
                state.verification_status['income_proof_confidence'] = \
                    state_dict['income_proof_verification'].get('confidence_score', 0.0)
        
        # Update basic fields
        if "customer_details" in state_dict:
            state.customer_details = state_dict["customer_details"]
        
        if "loan_details" in state_dict:
            state.loan_details = state_dict["loan_details"]
        
        if "extracted_info" in state_dict:
            state.extracted_info = state_dict["extracted_info"]
        
        # Special handling for messages
        if "messages" in state_dict and hasattr(state, 'messages'):
            # Get the number of messages in current state
            current_msg_count = len(state.messages) if state.messages else 0
            
            # If there are more messages in the state dict, add the new ones
            if len(state_dict["messages"]) > current_msg_count:
                if not hasattr(state, 'add_message'):
                    state.messages = state_dict["messages"]
                else:
                    for i in range(current_msg_count, len(state_dict["messages"])):
                        msg = state_dict["messages"][i]
                        state.add_message(msg['role'], msg['content'])
            else:
                state.messages = state_dict["messages"]
        
        if "conversation_stage" in state_dict:
            state.conversation_stage = state_dict["conversation_stage"]
        
        if "decision" in state_dict:
            state.decision = state_dict["decision"]
        
        # Update verification status if it exists
        if "verification_status" in state_dict:
            state.verification_status = state_dict["verification_status"]
        
        # Update underwriting result if it exists
        if "underwriting_result" in state_dict:
            state.underwriting_result = state_dict["underwriting_result"]
        
        # Update documentation status if it exists
        if "documentation_status" in state_dict:
            state.documentation_status = state_dict["documentation_status"]
        
        # Update sanction letter ID if it exists
        if "sanction_letter_id" in state_dict:
            state.sanction_letter_id = state_dict["sanction_letter_id"]
            
            # Update documentation status if it exists
            if hasattr(state, 'documentation_status'):
                if state.documentation_status is None:
                    state.documentation_status = {}
                    
                state.documentation_status['status'] = 'completed'
                state.documentation_status['document_path'] = state_dict['sanction_letter_id']
                
        # Update last_updated timestamp if it exists
        if "last_updated" in state_dict:
            state.last_updated = state_dict["last_updated"]