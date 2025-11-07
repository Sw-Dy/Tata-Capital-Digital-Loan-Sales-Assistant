# Underwriting Agent for Tata Capital Digital Loan Sales Assistant

import json
import os
import sys
import logging
import pandas as pd
from typing import Dict, List, Optional, Any, Union

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import mock APIs
from implementation.mock_apis import CreditBureauApi, DocumentStorage

# Configure logging
logger = logging.getLogger(__name__)

class UnderwritingAgent:
    """Underwriting Agent responsible for credit evaluation and loan eligibility determination"""
    
    def __init__(self, customers_df=None, credit_bureau_df=None):
        """Initialize the Underwriting Agent with required APIs and data
        
        Args:
            customers_df: DataFrame containing customer information
            credit_bureau_df: DataFrame containing credit bureau information
        """
        self.credit_bureau_api = CreditBureauApi()
        self.document_storage = DocumentStorage()
        
        # Load CSV data if not provided
        try:
            self.customers_df = customers_df if customers_df is not None else pd.read_csv(os.path.join('data', 'customers.csv'))
            self.credit_bureau_df = credit_bureau_df if credit_bureau_df is not None else pd.read_csv(os.path.join('data', 'credit_bureau.csv'))
            logger.info("Underwriting Agent initialized with CSV data")
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            # Initialize empty DataFrames as fallback
            self.customers_df = pd.DataFrame()
            self.credit_bureau_df = pd.DataFrame()
        
        # System prompt for the Underwriting Agent
        self.system_prompt = """
        You are a precise and analytical Underwriting Agent for Tata Capital, a leading NBFC in India.
        Your role is to evaluate loan applications, assess credit risk, and determine eligibility based on established criteria.
        
        Follow these guidelines:
        1. Apply eligibility rules consistently and fairly
        2. Analyze credit scores and financial data objectively
        3. Evaluate income and existing obligations accurately
        4. Make clear decisions based on established criteria
        5. Explain approval or rejection reasons transparently
        6. Maintain compliance with lending regulations
        7. Protect customer financial data and privacy
        
        Your goal is to make sound lending decisions that balance risk management with customer needs.
        """
    
    def process(self, state) -> Dict:
        """Process the current conversation state and determine loan eligibility
        
        Args:
            state: The conversation state object from the Master Agent
            
        Returns:
            Updated state object with underwriting information
        """
        logger.info("Underwriting Agent processing conversation state")
        
        # Extract relevant information from state
        loan_details = state.loan_details or {}
        customer_details = state.customer_details or {}
        verification_status = state.verification_status or {}
        
        # Check if we have a customer ID
        customer_id = customer_details.get("customer_id")
        
        if not customer_id:
            logger.warning("No customer ID found in state")
            state.underwriting_status = {
                "status": "rejected",
                "reason": "Customer ID not found"
            }
            return state
        
        # Check if verification is complete
        if not verification_status.get("customer_verified"):
            logger.warning("Customer verification incomplete")
            state.underwriting_status = {
                "status": "pending",
                "reason": "Customer verification incomplete"
            }
            return state
        
        # Check if loan details are available
        if not loan_details.get("loan_amount") or not loan_details.get("loan_tenure"):
            logger.warning("Loan details incomplete")
            state.underwriting_status = {
                "status": "pending",
                "reason": "Loan details incomplete"
            }
            return state
        
        # Get credit score
        credit_score = self._get_credit_score(customer_id)
        if credit_score is None:
            logger.warning(f"Credit score not found for customer {customer_id}")
            state.underwriting_status = {
                "status": "pending",
                "reason": "Credit score not available"
            }
            return state
        
        # Get customer details
        customer_info = self._get_customer_info(customer_id)
        if not customer_info:
            logger.warning(f"Customer information not found for customer {customer_id}")
            state.underwriting_status = {
                "status": "rejected",
                "reason": "Customer information not found"
            }
            return state
        
        # Update customer details with credit score
        customer_details["credit_score"] = credit_score
        
        # Get pre-approved limit
        pre_approved_limit = customer_info.get("pre_approved_limit", 0)
        customer_details["pre_approved_limit"] = pre_approved_limit
        
        # Assess loan eligibility
        loan_amount = float(loan_details.get("loan_amount", 0))
        loan_assessment = self._assess_loan_application(credit_score, loan_amount, pre_approved_limit)
        
        # Update state with assessment results
        state.underwriting_status = loan_assessment
        state.customer_details = customer_details
        
        logger.info(f"Loan assessment completed for customer {customer_id}: {loan_assessment['status']}")
        
        return state
    
    def _get_credit_score(self, customer_id: str) -> Optional[int]:
        """Get credit score for a customer
        
        Args:
            customer_id: The customer ID to look up
            
        Returns:
            Credit score as an integer or None if not found
        """
        try:
            # Find customer in credit bureau data
            if not self.credit_bureau_df.empty:
                customer_data = self.credit_bureau_df[self.credit_bureau_df['customer_id'] == customer_id]
                
                if not customer_data.empty:
                    # Get credit score from first row
                    return int(customer_data.iloc[0]['credit_score'])
            
            # Fallback to API if not found in DataFrame
            credit_data = self.credit_bureau_api.get_credit_score(customer_id)
            if credit_data and 'credit_score' in credit_data:
                return int(credit_data['credit_score'])
            
            return None
        except Exception as e:
            logger.error(f"Error getting credit score: {e}")
            return None
    
    def _get_customer_info(self, customer_id: str) -> Dict:
        """Get customer information
        
        Args:
            customer_id: The customer ID to look up
            
        Returns:
            Dictionary with customer information or empty dict if not found
        """
        try:
            # Find customer in customers data
            if not self.customers_df.empty:
                customer_data = self.customers_df[self.customers_df['customer_id'] == customer_id]
                
                if not customer_data.empty:
                    # Convert first row to dictionary
                    return customer_data.iloc[0].to_dict()
            
            return {}
        except Exception as e:
            logger.error(f"Error getting customer information: {e}")
            return {}
    
    def _assess_loan_application(self, credit_score: int, loan_amount: float, pre_approved_limit: float) -> Dict:
        """Assess loan application based on credit score and loan amount
        
        Args:
            credit_score: The customer's credit score
            loan_amount: The requested loan amount
            pre_approved_limit: The pre-approved loan limit for the customer
            
        Returns:
            Dictionary with assessment results
        """
        # Define credit score thresholds
        excellent_threshold = 750
        good_threshold = 700
        fair_threshold = 650
        poor_threshold = 600
        
        # Check if loan amount exceeds pre-approved limit
        if loan_amount > pre_approved_limit:
            return {
                "status": "rejected",
                "reason": "Loan amount exceeds pre-approved limit",
                "credit_score": credit_score,
                "pre_approved_limit": pre_approved_limit
            }
        
        # Assess based on credit score
        if credit_score >= excellent_threshold:
            return {
                "status": "approved",
                "interest_rate": 8.5,  # Lower interest rate for excellent credit
                "credit_score": credit_score,
                "pre_approved_limit": pre_approved_limit
            }
        elif credit_score >= good_threshold:
            return {
                "status": "approved",
                "interest_rate": 10.0,  # Standard interest rate for good credit
                "credit_score": credit_score,
                "pre_approved_limit": pre_approved_limit
            }
        elif credit_score >= fair_threshold:
            return {
                "status": "approved",
                "interest_rate": 12.5,  # Higher interest rate for fair credit
                "credit_score": credit_score,
                "pre_approved_limit": pre_approved_limit
            }
        elif credit_score >= poor_threshold:
            return {
                "status": "conditional_approval",
                "interest_rate": 15.0,  # High interest rate for poor credit
                "conditions": ["Additional documentation required", "Collateral may be required"],
                "credit_score": credit_score,
                "pre_approved_limit": pre_approved_limit
            }
        else:
            return {
                "status": "rejected",
                "reason": "Credit score below minimum threshold",
                "credit_score": credit_score,
                "pre_approved_limit": pre_approved_limit
            }
    
    def _handle_initial_assessment(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the initial assessment stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the assessment results and next action
        """
        # Extract relevant information
        loan_details = conversation_state.get("loan_details", {})
        customer_details = conversation_state.get("customer_details", {})
        
        # Initialize underwriting status
        underwriting_status = {
            "started": True,
            "credit_checked": False,
            "salary_verification_needed": False,
            "salary_verified": False,
            "decision": None,
            "reason": None,
            "underwriting_complete": False
        }
        
        # Generate appropriate response
        response = "I'll now evaluate your loan application. First, I need to check your credit score and history. This will only take a moment."
        
        return {
            "customer_response": response,
            "internal_data": {
                "underwriting_stage": "credit_check",
                "underwriting_status": underwriting_status,
                "confidence": 0.9
            },
            "next_action": "continue_underwriting"
        }
    
    def _handle_credit_check(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the credit check stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the credit check results and next action
        """
        try:
            # Extract relevant information
            loan_details = conversation_state.get("loan_details", {})
            customer_details = conversation_state.get("customer_details", {})
            underwriting_status = conversation_state.get("underwriting_status", {})
            
            # Get credit score from Credit Bureau API
            credit_info = self.credit_bureau_api.get_credit_score(customer_id)
            
            # Check if we got valid credit information
            if "error" in credit_info:
                # Handle API error
                return {
                    "customer_response": "I'm having trouble retrieving your credit information at the moment. Could you please bear with me while I resolve this issue?",
                    "internal_data": {
                        "underwriting_stage": "credit_check",
                        "api_error": credit_info["error"],
                        "confidence": 0.5
                    },
                    "next_action": "retry_credit_check"
                }
            
            # Store credit information
            credit_score = credit_info.get("score", 0)
            credit_band = credit_info.get("score_band", "")
            monthly_obligations = credit_info.get("monthly_obligations", 0)
            
            # Update underwriting status
            underwriting_status["credit_checked"] = True
            underwriting_status["credit_score"] = credit_score
            underwriting_status["credit_band"] = credit_band
            underwriting_status["monthly_obligations"] = monthly_obligations
            
            # Get customer's pre-approved limit
            pre_approved_limit = customer_details.get("pre_approved_limit", 0)
            
            # Get requested loan amount and tenure
            loan_amount = loan_details.get("amount", 0)
            loan_tenure = loan_details.get("tenure", 0)
            
            # Determine if salary verification is needed
            # Rule: If requested amount is within pre-approved limit, no salary verification needed
            # If between pre-approved and 2x pre-approved, salary verification needed
            # If more than 2x pre-approved or credit score < 700, reject
            
            if loan_amount <= pre_approved_limit:
                # Within pre-approved limit, no salary verification needed
                underwriting_status["salary_verification_needed"] = False
                underwriting_status["decision"] = "APPROVED"
                underwriting_status["reason"] = "Amount within pre-approved limit"
                underwriting_status["underwriting_complete"] = True
                
                response = f"Good news! Based on your credit profile and pre-approved limit, your loan application for ₹{loan_amount:,} has been approved. No additional documentation is required."
                next_stage = "final_decision"
                next_action = "proceed_to_documentation"
                
            elif loan_amount <= 2 * pre_approved_limit and credit_score >= 700:
                # Between pre-approved and 2x pre-approved, salary verification needed
                underwriting_status["salary_verification_needed"] = True
                
                response = f"Your requested loan amount of ₹{loan_amount:,} exceeds your pre-approved limit of ₹{pre_approved_limit:,}, but you have a good credit score of {credit_score}. I'll need to verify your income to proceed. Could you please upload your latest salary slip?"
                next_stage = "salary_verification"
                next_action = "request_salary_slip"
                
            else:
                # More than 2x pre-approved or credit score < 700, reject
                underwriting_status["salary_verification_needed"] = False
                
                if credit_score < 700:
                    underwriting_status["decision"] = "REJECTED"
                    underwriting_status["reason"] = "Credit score below threshold"
                    response = f"I've reviewed your application, and I regret to inform you that we cannot approve your requested loan amount of ₹{loan_amount:,} at this time. This is because your credit score of {credit_score} is below our threshold of 700 for this loan amount."
                else:
                    underwriting_status["decision"] = "REJECTED"
                    underwriting_status["reason"] = "Requested amount exceeds maximum eligible amount"
                    response = f"I've reviewed your application, and I regret to inform you that we cannot approve your requested loan amount of ₹{loan_amount:,} at this time. This amount significantly exceeds your eligible limit based on our underwriting criteria."
                
                underwriting_status["underwriting_complete"] = True
                next_stage = "final_decision"
                next_action = "proceed_to_documentation"
            
            return {
                "customer_response": response,
                "internal_data": {
                    "underwriting_stage": next_stage,
                    "underwriting_status": underwriting_status,
                    "credit_info": credit_info,
                    "confidence": 0.9
                },
                "next_action": next_action
            }
            
        except Exception as e:
            # Handle unexpected errors
            return {
                "customer_response": "I'm experiencing some technical difficulties with our credit check system. Please bear with me while I resolve this issue.",
                "internal_data": {
                    "underwriting_stage": "credit_check",
                    "error": str(e),
                    "confidence": 0.4
                },
                "next_action": "retry_credit_check"
            }
    
    def _handle_salary_verification(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the salary verification stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the salary verification results and next action
        """
        # Extract relevant information
        customer_message = conversation_state.get("last_customer_message", "")
        loan_details = conversation_state.get("loan_details", {})
        underwriting_status = conversation_state.get("underwriting_status", {})
        
        # Check if salary slip has been uploaded
        salary_slip_id = conversation_state.get("salary_slip_document_id")
        
        if not salary_slip_id:
            # If this is the first time in salary verification and no document ID
            if not conversation_state.get("salary_verification_started"):
                return {
                    "customer_response": "To proceed with your loan application, I need to verify your income. Please upload your latest salary slip.",
                    "internal_data": {
                        "underwriting_stage": "salary_verification",
                        "underwriting_status": underwriting_status,
                        "salary_verification_started": True,
                        "confidence": 0.8
                    },
                    "next_action": "request_salary_slip"
                }
            else:
                # Still waiting for salary slip upload
                return {
                    "customer_response": "I'm still waiting for your salary slip. Please upload it to proceed with your loan application.",
                    "internal_data": {
                        "underwriting_stage": "salary_verification",
                        "underwriting_status": underwriting_status,
                        "confidence": 0.7
                    },
                    "next_action": "request_salary_slip"
                }
        
        try:
            # Process the salary slip
            salary_info = self.document_storage.process_salary_slip(salary_slip_id)
            
            # Check if we got valid salary information
            if "error" in salary_info:
                # Handle API error
                return {
                    "customer_response": "I'm having trouble processing your salary slip. Could you please upload it again or provide a clearer copy?",
                    "internal_data": {
                        "underwriting_stage": "salary_verification",
                        "api_error": salary_info["error"],
                        "confidence": 0.5
                    },
                    "next_action": "request_salary_slip"
                }
            
            # Extract monthly salary
            monthly_salary = salary_info.get("monthly_salary", 0)
            
            # Update underwriting status
            underwriting_status["salary_verified"] = True
            underwriting_status["monthly_salary"] = monthly_salary
            
            # Calculate EMI for the requested loan
            loan_amount = loan_details.get("amount", 0)
            loan_tenure = loan_details.get("tenure", 0)
            interest_rate = loan_details.get("interest_rate", 11)  # Default to 11% if not specified
            
            # Simple EMI calculation
            monthly_rate = interest_rate / (12 * 100)
            emi = (loan_amount * monthly_rate * (1 + monthly_rate) ** loan_tenure) / \
                  ((1 + monthly_rate) ** loan_tenure - 1)
            
            # Get existing monthly obligations
            monthly_obligations = underwriting_status.get("monthly_obligations", 0)
            
            # Calculate total EMI-to-Income ratio
            total_emi = monthly_obligations + emi
            emi_to_income_ratio = total_emi / monthly_salary
            
            # Update underwriting status with EMI details
            underwriting_status["calculated_emi"] = emi
            underwriting_status["total_emi"] = total_emi
            underwriting_status["emi_to_income_ratio"] = emi_to_income_ratio
            
            # Determine eligibility based on EMI-to-Income ratio
            # Rule: EMI should not exceed 50% of monthly salary
            if emi_to_income_ratio <= 0.5:
                underwriting_status["decision"] = "APPROVED"
                underwriting_status["reason"] = "EMI-to-Income ratio within acceptable limit"
                response = f"Good news! Based on your salary of ₹{monthly_salary:,} per month and credit profile, your loan application for ₹{loan_amount:,} has been approved. Your monthly EMI will be approximately ₹{emi:.2f}."
            else:
                underwriting_status["decision"] = "REJECTED"
                underwriting_status["reason"] = "EMI-to-Income ratio exceeds 50%"
                response = f"After reviewing your salary of ₹{monthly_salary:,} per month and existing obligations, I regret to inform you that we cannot approve your requested loan amount of ₹{loan_amount:,} at this time. The monthly EMI of ₹{emi:.2f} would exceed 50% of your income when combined with your existing obligations."
            
            # Mark underwriting as complete
            underwriting_status["underwriting_complete"] = True
            
            return {
                "customer_response": response,
                "internal_data": {
                    "underwriting_stage": "final_decision",
                    "underwriting_status": underwriting_status,
                    "salary_info": salary_info,
                    "confidence": 0.9
                },
                "next_action": "proceed_to_documentation"
            }
            
        except Exception as e:
            # Handle unexpected errors
            return {
                "customer_response": "I'm experiencing some technical difficulties processing your salary information. Please bear with me while I resolve this issue.",
                "internal_data": {
                    "underwriting_stage": "salary_verification",
                    "error": str(e),
                    "confidence": 0.4
                },
                "next_action": "retry_salary_verification"
            }
    
    def _handle_final_decision(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the final decision stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the final decision and next action
        """
        # Extract relevant information
        loan_details = conversation_state.get("loan_details", {})
        underwriting_status = conversation_state.get("underwriting_status", {})
        
        # Check if underwriting is complete
        if not underwriting_status.get("underwriting_complete"):
            # If underwriting is not complete, determine what's missing
            if not underwriting_status.get("credit_checked"):
                return self._handle_credit_check(customer_id, conversation_state)
            elif underwriting_status.get("salary_verification_needed") and not underwriting_status.get("salary_verified"):
                return self._handle_salary_verification(customer_id, conversation_state)
        
        # Get the decision and reason
        decision = underwriting_status.get("decision")
        reason = underwriting_status.get("reason")
        
        # Format the final decision message
        if decision == "APPROVED":
            loan_amount = loan_details.get("amount", 0)
            loan_tenure = loan_details.get("tenure", 0)
            interest_rate = loan_details.get("interest_rate", 11)  # Default to 11% if not specified
            emi = underwriting_status.get("calculated_emi", 0)
            
            response = f"Congratulations! Your loan application for ₹{loan_amount:,} for {loan_tenure} months has been approved. The interest rate is {interest_rate}% per annum, and your monthly EMI will be approximately ₹{emi:.2f}. I'll now generate your sanction letter with all the details."
            next_action = "generate_sanction_letter"
        else:
            response = f"I regret to inform you that your loan application has been declined. Reason: {reason}. If you'd like to explore other loan options or have any questions, please feel free to ask."
            next_action = "handle_rejection"
        
        # Prepare the loan summary for documentation
        loan_summary = {
            "customer_id": customer_id,
            "loan_amount": loan_details.get("amount", 0),
            "tenure": loan_details.get("tenure", 0),
            "interest_rate": loan_details.get("interest_rate", 11),
            "monthly_emi": underwriting_status.get("calculated_emi", 0),
            "credit_score": underwriting_status.get("credit_score", 0),
            "decision": decision,
            "reason": reason
        }
        
        return {
            "customer_response": response,
            "internal_data": {
                "underwriting_stage": "completed",
                "underwriting_status": underwriting_status,
                "loan_summary": loan_summary,
                "confidence": 1.0
            },
            "next_action": next_action
        }

# Example usage
if __name__ == "__main__":
    # Test the Underwriting Agent
    underwriting_agent = UnderwritingAgent()
    
    # Simulate a conversation for pre-approved scenario
    conversation_state = {
        "conversation_history": [],
        "last_customer_message": "I've completed verification and ready for underwriting.",
        "loan_details": {
            "amount": 300000,
            "tenure": 36,
            "interest_rate": 10.5
        },
        "customer_details": {
            "pre_approved_limit": 500000
        }
    }
    
    # Initial assessment
    response = underwriting_agent.process("TC001", conversation_state)
    print(f"Underwriting Agent: {response['customer_response']}")
    
    # Update conversation state with credit check
    conversation_state["conversation_history"].append({
        "role": "agent",
        "message": response["customer_response"]
    })
    conversation_state.update(response["internal_data"])
    
    # Process credit check
    response = underwriting_agent.process("TC001", conversation_state)
    print(f"\nUnderwriting Agent: {response['customer_response']}")
    
    # Print next action
    print(f"\nNext action: {response['next_action']}")
    
    # Simulate a conversation for salary verification scenario
    print("\n\n--- Salary Verification Scenario ---")
    conversation_state = {
        "conversation_history": [],
        "last_customer_message": "I've completed verification and ready for underwriting.",
        "loan_details": {
            "amount": 800000,
            "tenure": 36,
            "interest_rate": 10.5
        },
        "customer_details": {
            "pre_approved_limit": 500000
        }
    }
    
    # Initial assessment
    response = underwriting_agent.process("TC001", conversation_state)
    print(f"Underwriting Agent: {response['customer_response']}")
    
    # Update conversation state with credit check
    conversation_state["conversation_history"].append({
        "role": "agent",
        "message": response["customer_response"]
    })
    conversation_state.update(response["internal_data"])
    
    # Process credit check
    response = underwriting_agent.process("TC001", conversation_state)
    print(f"\nUnderwriting Agent: {response['customer_response']}")
    
    # Update conversation state with salary slip upload
    conversation_state["conversation_history"].append({
        "role": "agent",
        "message": response["customer_response"]
    })
    conversation_state.update(response["internal_data"])
    conversation_state["last_customer_message"] = "I've uploaded my salary slip."
    conversation_state["salary_slip_document_id"] = "salary_slip_TC001_1234567890"
    
    # Process salary verification
    response = underwriting_agent.process("TC001", conversation_state)
    print(f"\nCustomer: {conversation_state['last_customer_message']}")
    print(f"Underwriting Agent: {response['customer_response']}")
    
    # Print next action
    print(f"\nNext action: {response['next_action']}")