# Verification Agent for Tata Capital Digital Loan Sales Assistant

import json
import os
import sys
import pandas as pd
import logging
from typing import Dict, List, Optional, Any, Union

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logger = logging.getLogger(__name__)

class VerificationAgent:
    """Verification Agent responsible for KYC validation and customer detail verification"""
    
    def __init__(self, crm_data_df=None):
        """Initialize the Verification Agent with required data
        
        Args:
            crm_data_df: DataFrame containing CRM data with customer contact information
        """
        self.crm_data_df = crm_data_df
        
        # Load data from CSV if not provided
        if self.crm_data_df is None:
            try:
                self.crm_data_df = pd.read_csv(os.path.join('data', 'crm_data.csv'))
                logger.info("Loaded CRM data from CSV")
            except Exception as e:
                logger.error(f"Error loading CRM data: {e}")
                self.crm_data_df = pd.DataFrame()
        
        # System prompt for the Verification Agent
        self.system_prompt = """
        You are a diligent Verification Agent for Tata Capital, a leading NBFC in India.
        Your role is to verify customer details, validate KYC information, and ensure compliance with regulatory requirements.
        
        Follow these guidelines:
        1. Be thorough and meticulous in verifying customer information
        2. Cross-check details against CRM records
        3. Flag any inconsistencies or discrepancies
        4. Maintain strict compliance with KYC regulations
        5. Protect customer privacy and data security
        6. Be clear and concise in your communication
        7. Provide accurate verification status updates
        8. Always collect bank account details (account number, IFSC code, bank name)
        9. Always request proof of income documents (salary slips, bank statements, ITR)
        
        Your goal is to ensure the integrity of customer data while maintaining a smooth verification process.
        """
    
    def process(self, state) -> Dict:
        """Process the current conversation state and verify customer details
        
        Args:
            state: The conversation state object from the Master Agent
            
        Returns:
            Updated state object with verification information
        """
        logger.info("Verification Agent processing conversation state")
        
        # Extract customer details from state
        customer_details = state.customer_details or {}
        extracted_info = state.extracted_info or {}
        
        # Check if we have a customer ID
        customer_id = customer_details.get("customer_id")
        
        # If we don't have a customer ID but have a PAN, try to find the customer
        if not customer_id and extracted_info.get("pan"):
            customer_id = self._find_customer_by_pan(extracted_info.get("pan"))
            if customer_id:
                customer_details["customer_id"] = customer_id
                logger.info(f"Found customer ID {customer_id} using PAN")
        
        # If we have a customer ID, verify phone and address
        if customer_id:
            # Get customer data from CRM
            crm_data = self._get_customer_crm_data(customer_id)
            
            if crm_data:
                # Update customer details with CRM data
                if "phone" in crm_data:
                    customer_details["phone"] = crm_data["phone"]
                if "address" in crm_data:
                    customer_details["address"] = crm_data["address"]
                
                # Check for bank account details
                account_details_verified = False
                if "account_number" in customer_details and "ifsc_code" in customer_details and "bank_name" in customer_details:
                    account_details_verified = True
                    logger.info(f"Bank account details already verified for customer {customer_id}")
                
                # Check for income proof
                income_proof_verified = False
                if "income_proof" in customer_details and customer_details["income_proof"] == True:
                    income_proof_verified = True
                    logger.info(f"Income proof already verified for customer {customer_id}")
                
                # Set verification status
                state.verification_status = {
                    "customer_verified": True,
                    "phone_verified": True,
                    "address_verified": True,
                    "account_details_verified": account_details_verified,
                    "income_proof_verified": income_proof_verified,
                    "verified": account_details_verified and income_proof_verified
                }
                
                # Generate response based on verification status
                if not account_details_verified:
                    state.add_message("assistant", "I need to collect your bank account details for loan disbursement. Please provide your account number, IFSC code, and bank name.")
                
                if not income_proof_verified:
                    state.add_message("assistant", "To proceed with your loan application, I need you to upload proof of income. This could be your recent salary slips, bank statements, or Income Tax Returns (ITR).")
                
                logger.info(f"Customer {customer_id} verification status: {state.verification_status}")
            else:
                # Customer not found in CRM
                state.verification_status = {
                    "customer_verified": False,
                    "error": "Customer not found in CRM"
                }
                
                logger.warning(f"Customer {customer_id} not found in CRM")
        else:
            # Try to verify with provided information
            phone_verified = False
            address_verified = False
            
            # Check if phone number is provided and verify it
            if extracted_info.get("phone"):
                phone = extracted_info.get("phone")
                # Find customer by phone
                found_customer = self._find_customer_by_phone(phone)
                
                if found_customer:
                    customer_id = found_customer.get("customer_id")
                    customer_details["customer_id"] = customer_id
                    customer_details["phone"] = phone
                    phone_verified = True
                    
                    logger.info(f"Verified phone number {phone} for customer {customer_id}")
            
            # Check if address is provided and verify it
            if extracted_info.get("address") or extracted_info.get("city"):
                address = extracted_info.get("address", "")
                city = extracted_info.get("city", "")
                
                # If we have a customer ID, verify address against CRM
                if customer_id:
                    crm_data = self._get_customer_crm_data(customer_id)
                    
                    if crm_data and "address" in crm_data:
                        # Simple address verification (check if city is in address)
                        if city.lower() in crm_data["address"].lower():
                            customer_details["address"] = crm_data["address"]
                            address_verified = True
                            
                            logger.info(f"Verified address for customer {customer_id}")
            
            # Check for bank account details in extracted info
            account_details_verified = False
            if extracted_info.get("account_number") and extracted_info.get("ifsc_code") and extracted_info.get("bank_name"):
                customer_details["account_number"] = extracted_info.get("account_number")
                customer_details["ifsc_code"] = extracted_info.get("ifsc_code")
                customer_details["bank_name"] = extracted_info.get("bank_name")
                account_details_verified = True
                logger.info(f"Bank account details extracted for customer")
            
            # Check for income proof in extracted info
            income_proof_verified = False
            if extracted_info.get("income_proof") == True:
                customer_details["income_proof"] = True
                income_proof_verified = True
                logger.info(f"Income proof verified")
            
            # Update verification status
            state.verification_status = {
                "customer_verified": customer_id is not None,
                "phone_verified": phone_verified,
                "address_verified": address_verified,
                "account_details_verified": account_details_verified,
                "income_proof_verified": income_proof_verified,
                "verified": customer_id is not None and phone_verified and address_verified and account_details_verified and income_proof_verified
            }
            
            # Generate response based on verification status
            if not account_details_verified:
                state.add_message("assistant", "I need to collect your bank account details for loan disbursement. Please provide your account number, IFSC code, and bank name.")
            
            if not income_proof_verified:
                state.add_message("assistant", "To proceed with your loan application, I need you to upload proof of income. This could be your recent salary slips, bank statements, or Income Tax Returns (ITR).")
        
        # Update customer details in state
        state.customer_details = customer_details
        
        return state
    
    def _get_customer_crm_data(self, customer_id: str) -> Dict:
        """Get customer data from CRM
        
        Args:
            customer_id: The customer ID to look up
            
        Returns:
            Dictionary with customer CRM data or None if not found
        """
        try:
            # Find customer in CRM data
            if not self.crm_data_df.empty:
                customer_data = self.crm_data_df[self.crm_data_df['customer_id'] == customer_id]
                
                if not customer_data.empty:
                    # Convert first row to dictionary
                    return customer_data.iloc[0].to_dict()
            
            return None
        except Exception as e:
            logger.error(f"Error getting customer CRM data: {e}")
            return None
    
    def _find_customer_by_phone(self, phone: str) -> Dict:
        """Find customer by phone number
        
        Args:
            phone: The phone number to search for
            
        Returns:
            Dictionary with customer data or None if not found
        """
        try:
            # Find customer in CRM data by phone
            if not self.crm_data_df.empty:
                customer_data = self.crm_data_df[self.crm_data_df['phone'] == phone]
                
                if not customer_data.empty:
                    # Convert first row to dictionary
                    return customer_data.iloc[0].to_dict()
            
            return None
        except Exception as e:
            logger.error(f"Error finding customer by phone: {e}")
            return None
    
    def _find_customer_by_pan(self, pan: str) -> str:
        """Find customer ID by PAN
        
        Args:
            pan: The PAN to search for
            
        Returns:
            Customer ID or None if not found
        """
        # This is a mock implementation since we don't have PAN in our CSV
        # In a real implementation, we would search for the PAN in a database
        # For now, we'll just return a hardcoded customer ID based on the first character of the PAN
        try:
            if pan and len(pan) >= 5:
                first_char = pan[0].upper()
                if first_char in "ABCDE":
                    return "C001"
                elif first_char in "FGHIJ":
                    return "C002"
                elif first_char in "KLMNO":
                    return "C003"
                elif first_char in "PQRST":
                    return "C004"
                elif first_char in "UVWXYZ":
                    return "C005"
            
            return None
        except Exception as e:
            logger.error(f"Error finding customer by PAN: {e}")
            return None
        """Handle the initial verification stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the verification results and next action
        """
        try:
            # Get customer details from CRM API
            crm_details = self.crm_api.get_customer_by_id(customer_id)
            
            # Check if we got valid customer details
            if "error" in crm_details:
                # Handle API error
                return {
                    "customer_response": "I'm having trouble retrieving your details from our system. Could you please confirm your customer ID or registered phone number?",
                    "internal_data": {
                        "verification_stage": "initial_verification",
                        "api_error": crm_details["error"],
                        "confidence": 0.5
                    },
                    "next_action": "retry_verification"
                }
            
            # Initialize verification status
            verification_status = {
                "customer_found": True,
                "kyc_validated": False,
                "address_verified": False,
                "contact_verified": False,
                "verification_complete": False
            }
            
            # Check if KYC is already completed in CRM
            if crm_details.get("kyc_status") == "COMPLETED":
                verification_status["kyc_validated"] = True
            
            # Store customer details and verification status
            customer_details = {
                "customer_id": customer_id,
                "name": crm_details.get("name"),
                "phone": crm_details.get("phone"),
                "email": crm_details.get("email"),
                "address": crm_details.get("address"),
                "pan": crm_details.get("pan"),
                "aadhaar": crm_details.get("aadhaar"),
                "date_of_birth": crm_details.get("date_of_birth"),
                "kyc_status": crm_details.get("kyc_status")
            }
            
            # Generate appropriate response based on KYC status
            if verification_status["kyc_validated"]:
                response = f"Thank you, {customer_details['name']}. I can see that your KYC verification is already complete in our system. Let me quickly verify your contact details."
                next_stage = "contact_verification"
            else:
                response = f"Thank you, {customer_details['name']}. I need to verify your KYC details. Could you please confirm your PAN number and date of birth for verification?"
                next_stage = "kyc_validation"
            
            return {
                "customer_response": response,
                "internal_data": {
                    "verification_stage": next_stage,
                    "customer_details": customer_details,
                    "verification_status": verification_status,
                    "confidence": 0.9
                },
                "next_action": "continue_verification"
            }
            
        except Exception as e:
            # Handle unexpected errors
            return {
                "customer_response": "I'm experiencing some technical difficulties with our verification system. Please bear with me while I resolve this issue.",
                "internal_data": {
                    "verification_stage": "initial_verification",
                    "error": str(e),
                    "confidence": 0.4
                },
                "next_action": "retry_verification"
            }
    
    def _handle_kyc_validation(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the KYC validation stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the verification results and next action
        """
        # Extract relevant information
        customer_message = conversation_state.get("last_customer_message", "")
        customer_details = conversation_state.get("customer_details", {})
        verification_status = conversation_state.get("verification_status", {})
        
        # Extract PAN and DOB from customer message if provided
        provided_pan = self._extract_pan(customer_message)
        provided_dob = self._extract_dob(customer_message)
        
        # If customer didn't provide both PAN and DOB, ask again
        if not provided_pan and not provided_dob:
            return {
                "customer_response": "I need both your PAN number and date of birth for verification. Could you please provide these details?",
                "internal_data": {
                    "verification_stage": "kyc_validation",
                    "customer_details": customer_details,
                    "verification_status": verification_status,
                    "confidence": 0.7
                },
                "next_action": "continue_verification"
            }
        
        # Verify provided details against CRM records
        kyc_verified = True
        verification_issues = []
        
        if provided_pan and provided_pan != customer_details.get("pan"):
            kyc_verified = False
            verification_issues.append("PAN number mismatch")
        
        if provided_dob and provided_dob != customer_details.get("date_of_birth"):
            kyc_verified = False
            verification_issues.append("Date of birth mismatch")
        
        # Update verification status
        verification_status["kyc_validated"] = kyc_verified
        
        # Generate appropriate response based on verification result
        if kyc_verified:
            response = "Thank you for confirming your KYC details. Your PAN and date of birth have been verified. Now, let me verify your address details."
            next_stage = "address_verification"
        else:
            issues_text = ", ".join(verification_issues)
            response = f"I'm having trouble verifying your KYC details due to {issues_text}. Could you please check and provide the correct information?"
            next_stage = "kyc_validation"
        
        return {
            "customer_response": response,
            "internal_data": {
                "verification_stage": next_stage,
                "customer_details": customer_details,
                "verification_status": verification_status,
                "verification_issues": verification_issues if not kyc_verified else [],
                "confidence": 0.9 if kyc_verified else 0.6
            },
            "next_action": "continue_verification"
        }
    
    def _handle_address_verification(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the address verification stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the verification results and next action
        """
        # Extract relevant information
        customer_message = conversation_state.get("last_customer_message", "")
        customer_details = conversation_state.get("customer_details", {})
        verification_status = conversation_state.get("verification_status", {})
        
        # For simplicity, we'll assume the address is verified if the customer confirms it
        # In a real system, this would involve more sophisticated verification
        
        # Check if this is the first time in address verification
        if not conversation_state.get("address_verification_started"):
            # Ask customer to confirm their address
            address = customer_details.get("address", "Not available")
            return {
                "customer_response": f"I need to verify your address. Our records show your address as: {address}. Is this correct?",
                "internal_data": {
                    "verification_stage": "address_verification",
                    "customer_details": customer_details,
                    "verification_status": verification_status,
                    "address_verification_started": True,
                    "confidence": 0.8
                },
                "next_action": "continue_verification"
            }
        
        # Check if customer confirmed the address
        if self._is_confirmation(customer_message):
            # Address confirmed, update verification status
            verification_status["address_verified"] = True
            response = "Thank you for confirming your address. Now, let me verify your contact details."
            next_stage = "contact_verification"
        else:
            # Address not confirmed, ask for the correct address
            response = "I understand that your address has changed. Please provide your current address for our records."
            next_stage = "address_verification"
        
        return {
            "customer_response": response,
            "internal_data": {
                "verification_stage": next_stage,
                "customer_details": customer_details,
                "verification_status": verification_status,
                "confidence": 0.9 if verification_status["address_verified"] else 0.7
            },
            "next_action": "continue_verification"
        }
    
    def _handle_contact_verification(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the contact verification stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the verification results and next action
        """
        # Extract relevant information
        customer_message = conversation_state.get("last_customer_message", "")
        customer_details = conversation_state.get("customer_details", {})
        verification_status = conversation_state.get("verification_status", {})
        
        # For simplicity, we'll assume the contact details are verified if the customer confirms them
        # In a real system, this would involve more sophisticated verification like OTP
        
        # Check if this is the first time in contact verification
        if not conversation_state.get("contact_verification_started"):
            # Ask customer to confirm their contact details
            phone = customer_details.get("phone", "Not available")
            email = customer_details.get("email", "Not available")
            return {
                "customer_response": f"Finally, I need to verify your contact details. Our records show your phone number as {phone} and email as {email}. Are these correct?",
                "internal_data": {
                    "verification_stage": "contact_verification",
                    "customer_details": customer_details,
                    "verification_status": verification_status,
                    "contact_verification_started": True,
                    "confidence": 0.8
                },
                "next_action": "continue_verification"
            }
        
        # Check if customer confirmed the contact details
        if self._is_confirmation(customer_message):
            # Contact details confirmed, update verification status
            verification_status["contact_verified"] = True
            verification_status["verification_complete"] = True
            
            response = "Thank you for confirming your contact details. All your information has been successfully verified. I'll now proceed with your loan application to the underwriting stage."
            next_stage = "completed"
        else:
            # Contact details not confirmed, ask for the correct details
            response = "I understand that your contact details have changed. Please provide your current phone number and email address for our records."
            next_stage = "contact_verification"
        
        return {
            "customer_response": response,
            "internal_data": {
                "verification_stage": next_stage,
                "customer_details": customer_details,
                "verification_status": verification_status,
                "confidence": 1.0 if verification_status["verification_complete"] else 0.7
            },
            "next_action": "proceed_to_underwriting" if verification_status.get("verification_complete") else "continue_verification"
        }
    
    # Helper methods for extracting and validating information
    
    def _extract_pan(self, message: str) -> Optional[str]:
        """Extract PAN number from customer message
        
        Args:
            message: The customer's message
            
        Returns:
            String representing the PAN number, or None if not found
        """
        # In a real implementation, this would use regex or NLP to extract PAN
        # For this mock, we'll use a simple approach
        
        import re
        
        # PAN format: 5 alphabets, 4 numbers, 1 alphabet
        pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
        
        matches = re.search(pan_pattern, message.upper())
        if matches:
            return matches.group(0)
        
        return None
    
    def _extract_dob(self, message: str) -> Optional[str]:
        """Extract date of birth from customer message
        
        Args:
            message: The customer's message
            
        Returns:
            String representing the date of birth, or None if not found
        """
        # In a real implementation, this would use regex or NLP to extract DOB
        # For this mock, we'll use a simple approach
        
        import re
        
        # Common date formats
        date_patterns = [
            r'(\d{2}[/-]\d{2}[/-]\d{4})', # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{4}[/-]\d{2}[/-]\d{2})', # YYYY/MM/DD or YYYY-MM-DD
            r'(\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})' # DD MMM YYYY
        ]
        
        for pattern in date_patterns:
            matches = re.search(pattern, message, re.IGNORECASE)
            if matches:
                return matches.group(1)
        
        return None
    
    def _is_confirmation(self, message: str) -> bool:
        """Check if the message is a confirmation
        
        Args:
            message: The customer's message
            
        Returns:
            Boolean indicating if the message is a confirmation
        """
        # Keywords indicating confirmation
        positive_keywords = ["yes", "correct", "right", "sure", "confirm", "confirmed", "that's right", "that is correct"]
        
        message_lower = message.lower()
        
        for keyword in positive_keywords:
            if keyword in message_lower:
                return True
        
        return False

# Example usage
if __name__ == "__main__":
    # Test the Verification Agent
    verification_agent = VerificationAgent()
    
    # Simulate a conversation
    conversation_state = {
        "conversation_history": [],
        "last_customer_message": "I've completed the sales process and ready for verification."
    }
    
    # Initial verification
    response = verification_agent.process("TC001", conversation_state)
    print(f"Verification Agent: {response['customer_response']}")
    
    # Update conversation state with customer response
    conversation_state["conversation_history"].append({
        "role": "agent",
        "message": response["customer_response"]
    })
    conversation_state.update(response["internal_data"])
    conversation_state["last_customer_message"] = "My PAN is ABCDE1234F and my date of birth is 15/05/1985."
    
    # Process KYC validation
    response = verification_agent.process("TC001", conversation_state)
    print(f"\nCustomer: {conversation_state['last_customer_message']}")
    print(f"Verification Agent: {response['customer_response']}")
    
    # Update conversation state with address verification
    conversation_state["conversation_history"].append({
        "role": "customer",
        "message": conversation_state["last_customer_message"]
    })
    conversation_state["conversation_history"].append({
        "role": "agent",
        "message": response["customer_response"]
    })
    conversation_state.update(response["internal_data"])
    conversation_state["last_customer_message"] = "Yes, that's my correct address."
    
    # Process address verification
    response = verification_agent.process("TC001", conversation_state)
    print(f"\nCustomer: {conversation_state['last_customer_message']}")
    print(f"Verification Agent: {response['customer_response']}")
    
    # Update conversation state with contact verification
    conversation_state["conversation_history"].append({
        "role": "customer",
        "message": conversation_state["last_customer_message"]
    })
    conversation_state["conversation_history"].append({
        "role": "agent",
        "message": response["customer_response"]
    })
    conversation_state.update(response["internal_data"])
    conversation_state["last_customer_message"] = "Yes, those are my correct contact details."
    
    # Process contact verification
    response = verification_agent.process("TC001", conversation_state)
    print(f"\nCustomer: {conversation_state['last_customer_message']}")
    print(f"Verification Agent: {response['customer_response']}")
    
    # Print next action
    print(f"\nNext action: {response['next_action']}")