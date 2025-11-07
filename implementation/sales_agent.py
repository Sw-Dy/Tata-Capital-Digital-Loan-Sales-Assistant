# Sales Agent for Tata Capital Digital Loan Sales Assistant

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

class SalesAgent:
    """Sales Agent responsible for understanding customer needs and presenting loan offers"""
    
    def __init__(self, customers_df=None, offer_mart_df=None):
        """Initialize the Sales Agent with required data
        
        Args:
            customers_df: DataFrame containing customer information
            offer_mart_df: DataFrame containing loan offers
        """
        self.customers_df = customers_df
        self.offer_mart_df = offer_mart_df
        
        # Load data from CSV if not provided
        if self.customers_df is None:
            try:
                self.customers_df = pd.read_csv(os.path.join('data', 'customers.csv'))
                logger.info("Loaded customers data from CSV")
            except Exception as e:
                logger.error(f"Error loading customers data: {e}")
                self.customers_df = pd.DataFrame()
        
        if self.offer_mart_df is None:
            try:
                self.offer_mart_df = pd.read_csv(os.path.join('data', 'offer_mart.csv'))
                logger.info("Loaded offer mart data from CSV")
            except Exception as e:
                logger.error(f"Error loading offer mart data: {e}")
                self.offer_mart_df = pd.DataFrame()
        
        # System prompt for the Sales Agent
        self.system_prompt = """
        You are a professional and friendly Sales Agent for Tata Capital, a leading NBFC in India.
        Your role is to understand customer needs, present personalized loan offers, and guide them through the loan selection process.
        
        Follow these guidelines:
        1. Be warm and professional, representing Tata Capital's brand values
        2. Ask relevant questions to understand the customer's loan requirements
        3. Present personalized offers clearly, highlighting benefits
        4. Explain loan terms in simple language
        5. Address customer concerns with empathy and accurate information
        6. Guide customers toward making informed decisions
        7. Never push products that don't match customer needs
        8. Maintain compliance with financial regulations
        9. Respect customer privacy and data protection
        
        Your goal is to help customers find the right loan product while creating a positive experience.
        """
    
    def process(self, state) -> Dict:
        """Process the current conversation state and update with sales information
        
        Args:
            state: The conversation state object from the Master Agent
            
        Returns:
            Updated state object with sales information
        """
        logger.info("Sales Agent processing conversation state")
        
        # Extract customer ID if available
        customer_id = state.customer_details.get("customer_id") if state.customer_details else None
        
        # Extract loan intent and details from state
        loan_intent = state.intent
        loan_details = state.loan_details
        
        # Process based on what information we have and what we need
        if not loan_details.get("type"):
            # If loan type is not determined, try to extract from intent
            if "personal" in loan_intent.lower():
                loan_details["type"] = "personal"
            elif "home" in loan_intent.lower() or "housing" in loan_intent.lower():
                loan_details["type"] = "home"
            elif "business" in loan_intent.lower():
                loan_details["type"] = "business"
            elif "education" in loan_intent.lower() or "student" in loan_intent.lower():
                loan_details["type"] = "education"
            elif "vehicle" in loan_intent.lower() or "car" in loan_intent.lower() or "auto" in loan_intent.lower():
                loan_details["type"] = "vehicle"
            else:
                # Default to personal loan if we can't determine
                loan_details["type"] = "personal"
            
            logger.info(f"Determined loan type: {loan_details['type']}")
        
        # Extract loan amount if mentioned but not recorded
        if not loan_details.get("amount") and state.extracted_info.get("loan_amount"):
            try:
                # Convert to float and handle various formats (e.g., "5 lakhs", "500000")
                amount_str = state.extracted_info.get("loan_amount", "")
                
                # Handle lakhs/lacs conversion
                if "lakh" in amount_str.lower() or "lac" in amount_str.lower():
                    # Extract the number before lakhs/lacs
                    import re
                    num_match = re.search(r'(\d+(\.\d+)?)', amount_str)
                    if num_match:
                        amount_value = float(num_match.group(1)) * 100000
                        loan_details["amount"] = amount_value
                else:
                    # Try to extract any number from the string
                    import re
                    num_match = re.search(r'(\d+(\.\d+)?)', amount_str)
                    if num_match:
                        loan_details["amount"] = float(num_match.group(1))
                
                logger.info(f"Extracted loan amount: {loan_details['amount']}")
            except Exception as e:
                logger.error(f"Error extracting loan amount: {e}")
        
        # Extract loan tenure if mentioned but not recorded
        if not loan_details.get("tenure") and state.extracted_info.get("loan_tenure"):
            try:
                # Convert to int and handle various formats (e.g., "3 years", "36 months")
                tenure_str = state.extracted_info.get("loan_tenure", "")
                
                # Handle years/months conversion
                import re
                num_match = re.search(r'(\d+)', tenure_str)
                if num_match:
                    tenure_value = int(num_match.group(1))
                    
                    # Convert to years if in months
                    if "month" in tenure_str.lower() and tenure_value > 12:
                        tenure_value = tenure_value // 12
                    
                    loan_details["tenure"] = tenure_value
                    logger.info(f"Extracted loan tenure: {loan_details['tenure']} years")
            except Exception as e:
                logger.error(f"Error extracting loan tenure: {e}")
        
        # Extract loan purpose if mentioned but not recorded
        if not loan_details.get("purpose") and state.extracted_info.get("loan_purpose"):
            loan_details["purpose"] = state.extracted_info.get("loan_purpose")
            logger.info(f"Extracted loan purpose: {loan_details['purpose']}")
        
        # If we have enough information, fetch loan offers
        if loan_details.get("amount") and loan_details.get("tenure"):
            offers = self._get_loan_offers(loan_details["amount"], loan_details["tenure"])
            if offers:
                loan_details["offers"] = offers
                loan_details["selected_offer"] = offers[0]  # Default to first offer
                
                # Set interest rate and processing fee from selected offer
                loan_details["interest_rate"] = offers[0]["interest_rate"]
                loan_details["processing_fee"] = offers[0]["processing_fee"]
                
                # Calculate EMI
                loan_details["emi"] = self._calculate_emi(
                    loan_details["amount"],
                    loan_details["interest_rate"],
                    loan_details["tenure"]
                )
                
                logger.info(f"Calculated EMI: {loan_details['emi']} for loan amount {loan_details['amount']}")
        
        # Update the state with the processed loan details
        state.loan_details = loan_details
        
        return state
    
    def _get_loan_offers(self, amount: float, tenure: int) -> List[Dict]:
        """Get loan offers based on amount and tenure
        
        Args:
            amount: Loan amount requested
            tenure: Loan tenure in years
            
        Returns:
            List of loan offers with interest rates and processing fees
        """
        offers = []
        
        try:
            # Filter offer_mart_df based on tenure
            filtered_offers = self.offer_mart_df[self.offer_mart_df['tenure'] == tenure]
            
            if not filtered_offers.empty:
                # Convert to list of dictionaries
                for _, row in filtered_offers.iterrows():
                    offers.append({
                        "interest_rate": row['interest_rate'],
                        "processing_fee": row['processing_fee'],
                        "tenure": row['tenure']
                    })
            else:
                # If no exact match, find the closest tenure
                closest_tenure = self.offer_mart_df['tenure'].iloc[(self.offer_mart_df['tenure'] - tenure).abs().argsort()[0]]
                filtered_offers = self.offer_mart_df[self.offer_mart_df['tenure'] == closest_tenure]
                
                for _, row in filtered_offers.iterrows():
                    offers.append({
                        "interest_rate": row['interest_rate'],
                        "processing_fee": row['processing_fee'],
                        "tenure": row['tenure']
                    })
                
                logger.info(f"No exact tenure match found. Using closest tenure: {closest_tenure}")
        except Exception as e:
            logger.error(f"Error getting loan offers: {e}")
            # Fallback to default offers
            offers = [
                {"interest_rate": 10.5, "processing_fee": 1.0, "tenure": tenure},
                {"interest_rate": 11.0, "processing_fee": 0.5, "tenure": tenure},
                {"interest_rate": 9.5, "processing_fee": 2.0, "tenure": tenure}
            ]
        
        return offers
    
    def _calculate_emi(self, principal: float, interest_rate: float, tenure: int) -> float:
        """Calculate EMI for a loan
        
        Args:
            principal: Loan amount
            interest_rate: Annual interest rate (in percentage)
            tenure: Loan tenure in years
            
        Returns:
            Monthly EMI amount
        """
        try:
            # Convert annual interest rate to monthly rate
            monthly_rate = interest_rate / (12 * 100)
            
            # Convert tenure from years to months
            tenure_months = tenure * 12
            
            # Calculate EMI using formula: P * r * (1+r)^n / ((1+r)^n - 1)
            emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
            
            return round(emi, 2)
        except Exception as e:
            logger.error(f"Error calculating EMI: {e}")
            # Fallback calculation (simple approximation)
            return round(principal / (tenure * 12), 2)
        
        # If we have loan details but haven't presented offers yet
        if not conversation_state.get("offers_presented"):
            return "offer_presentation"
        
        # If offers have been presented but not confirmed
        if not conversation_state.get("offer_confirmed"):
            return "negotiation"
        
        # If an offer has been confirmed
        return "confirmation"
    
    def _handle_initial_greeting(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the initial greeting stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the agent's response and updated internal data
        """
        greeting_message = "Welcome to Tata Capital! I'm here to help you explore our personal loan options. May I know what loan amount you're looking for and the purpose of the loan?"
        
        return {
            "customer_response": greeting_message,
            "internal_data": {
                "sales_stage": "need_exploration",
                "confidence": 0.9
            },
            "next_action": "continue_sales"
        }
    
    def _handle_need_exploration(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the need exploration stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the agent's response and updated internal data
        """
        # Extract relevant information
        customer_message = conversation_state.get("last_customer_message", "")
        loan_details = conversation_state.get("loan_details", {})
        
        # Extract loan amount if mentioned
        extracted_amount = self._extract_loan_amount(customer_message)
        if extracted_amount and not loan_details.get("amount"):
            loan_details["amount"] = extracted_amount
        
        # Extract loan tenure if mentioned
        extracted_tenure = self._extract_loan_tenure(customer_message)
        if extracted_tenure and not loan_details.get("tenure"):
            loan_details["tenure"] = extracted_tenure
        
        # Extract loan purpose if mentioned
        extracted_purpose = self._extract_loan_purpose(customer_message)
        if extracted_purpose and not loan_details.get("purpose"):
            loan_details["purpose"] = extracted_purpose
        
        # Determine what information we still need
        missing_info = []
        if not loan_details.get("amount"):
            missing_info.append("amount")
        if not loan_details.get("tenure"):
            missing_info.append("tenure")
        if not loan_details.get("purpose"):
            missing_info.append("purpose")
        
        # Generate appropriate response based on missing information
        if not missing_info:
            # We have all the information, move to offer presentation
            return self._prepare_offer_presentation(customer_id, conversation_state, loan_details)
        elif "amount" in missing_info:
            response = "Could you please let me know what loan amount you're looking for?"
        elif "tenure" in missing_info:
            response = f"For a loan of ₹{loan_details['amount']:,}, how many months would you prefer for repayment? We offer tenures between 12 to 60 months."
        elif "purpose" in missing_info:
            response = "May I know the purpose of this loan? This helps us tailor the right offer for you."
        
        # Update internal data
        return {
            "customer_response": response,
            "internal_data": {
                "sales_stage": "need_exploration",
                "loan_details": loan_details,
                "confidence": 0.8
            },
            "next_action": "continue_sales"
        }
    
    def _prepare_offer_presentation(self, customer_id: str, conversation_state: Dict, loan_details: Dict) -> Dict:
        """Prepare personalized offers for presentation
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            loan_details: The collected loan details
            
        Returns:
            Dict containing the agent's response and updated internal data
        """
        try:
            # Get personalized offers from the Offer Mart API
            offers_response = self.offer_mart_api.get_personalized_offers(
                customer_id, 
                loan_details.get("amount"), 
                loan_details.get("tenure")
            )
            
            # Check if we got valid offers
            if "error" in offers_response:
                # Handle API error
                return {
                    "customer_response": "I'm having trouble retrieving personalized offers for you at the moment. Could you please bear with me while I resolve this issue?",
                    "internal_data": {
                        "sales_stage": "need_exploration",
                        "loan_details": loan_details,
                        "api_error": offers_response["error"],
                        "confidence": 0.5
                    },
                    "next_action": "retry_offers"
                }
            
            # Store offers in conversation state
            offers = offers_response.get("offers", [])
            
            # If no offers available, inform the customer
            if not offers:
                return {
                    "customer_response": "Based on your requirements, I couldn't find any matching offers at the moment. Would you like to explore different loan amounts or tenures?",
                    "internal_data": {
                        "sales_stage": "need_exploration",
                        "loan_details": loan_details,
                        "no_offers": True,
                        "confidence": 0.7
                    },
                    "next_action": "continue_sales"
                }
            
            # Move to offer presentation
            return self._handle_offer_presentation(customer_id, {
                **conversation_state,
                "loan_details": loan_details,
                "available_offers": offers
            })
            
        except Exception as e:
            # Handle unexpected errors
            return {
                "customer_response": "I apologize, but I'm experiencing some technical difficulties retrieving offers. Let me try again. Could you confirm the loan amount you're looking for?",
                "internal_data": {
                    "sales_stage": "need_exploration",
                    "loan_details": loan_details,
                    "error": str(e),
                    "confidence": 0.4
                },
                "next_action": "continue_sales"
            }
    
    def _handle_offer_presentation(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the offer presentation stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the agent's response and updated internal data
        """
        # Extract relevant information
        loan_details = conversation_state.get("loan_details", {})
        available_offers = conversation_state.get("available_offers", [])
        
        # If no offers available, go back to need exploration
        if not available_offers:
            return self._handle_need_exploration(customer_id, conversation_state)
        
        # Select the best offer (lowest interest rate)
        best_offer = min(available_offers, key=lambda x: x.get("interest_rate", float('inf')))
        
        # Format the offer presentation message
        loan_amount = loan_details.get("amount", 0)
        loan_tenure = loan_details.get("tenure", 0)
        interest_rate = best_offer.get("interest_rate", 0)
        monthly_emi = best_offer.get("monthly_emi", 0)
        processing_fee = best_offer.get("processing_fee", 0)
        
        offer_message = f"Great news! Based on your profile, you qualify for a personal loan of ₹{loan_amount:,} for {loan_tenure} months at an interest rate of {interest_rate}% per annum. Your monthly EMI would be approximately ₹{monthly_emi:,}, with a one-time processing fee of ₹{processing_fee:,}."
        
        # Add information about other offers if available
        if len(available_offers) > 1:
            offer_message += f"\n\nI also have {len(available_offers)-1} other options that might interest you. Would you like to hear about them or proceed with this offer?"
        else:
            offer_message += "\n\nDoes this offer work for you, or would you like to explore different loan amounts or tenures?"
        
        return {
            "customer_response": offer_message,
            "internal_data": {
                "sales_stage": "negotiation",
                "loan_details": loan_details,
                "selected_offer": best_offer,
                "available_offers": available_offers,
                "offers_presented": True,
                "confidence": 0.9
            },
            "next_action": "continue_sales"
        }
    
    def _handle_negotiation(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the negotiation stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the agent's response and updated internal data
        """
        # Extract relevant information
        customer_message = conversation_state.get("last_customer_message", "")
        loan_details = conversation_state.get("loan_details", {})
        selected_offer = conversation_state.get("selected_offer", {})
        available_offers = conversation_state.get("available_offers", [])
        
        # Check if customer wants to see other offers
        if self._wants_other_offers(customer_message):
            return self._present_alternative_offers(customer_id, conversation_state)
        
        # Check if customer wants to modify loan parameters
        if self._wants_to_modify_loan(customer_message):
            # Extract new loan amount if mentioned
            new_amount = self._extract_loan_amount(customer_message)
            if new_amount:
                loan_details["amount"] = new_amount
            
            # Extract new loan tenure if mentioned
            new_tenure = self._extract_loan_tenure(customer_message)
            if new_tenure:
                loan_details["tenure"] = new_tenure
            
            # Go back to offer preparation with updated details
            return self._prepare_offer_presentation(customer_id, conversation_state, loan_details)
        
        # Check if customer accepts the offer
        if self._accepts_offer(customer_message):
            return self._handle_confirmation(customer_id, {
                **conversation_state,
                "offer_confirmed": True
            })
        
        # If we can't determine the customer's intent, ask for clarification
        return {
            "customer_response": "Would you like to proceed with this offer, explore other options, or modify the loan amount or tenure?",
            "internal_data": {
                "sales_stage": "negotiation",
                "loan_details": loan_details,
                "selected_offer": selected_offer,
                "available_offers": available_offers,
                "offers_presented": True,
                "confidence": 0.7
            },
            "next_action": "continue_sales"
        }
    
    def _present_alternative_offers(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Present alternative offers to the customer
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the agent's response and updated internal data
        """
        # Extract relevant information
        loan_details = conversation_state.get("loan_details", {})
        available_offers = conversation_state.get("available_offers", [])
        
        # If we have less than 2 offers, there are no alternatives to present
        if len(available_offers) < 2:
            return {
                "customer_response": "I'm sorry, but this is the only offer available based on your requirements. Would you like to proceed with this offer or explore different loan parameters?",
                "internal_data": {
                    "sales_stage": "negotiation",
                    "loan_details": loan_details,
                    "selected_offer": available_offers[0] if available_offers else {},
                    "available_offers": available_offers,
                    "offers_presented": True,
                    "confidence": 0.8
                },
                "next_action": "continue_sales"
            }
        
        # Sort offers by interest rate
        sorted_offers = sorted(available_offers, key=lambda x: x.get("interest_rate", float('inf')))
        
        # Present top 3 alternatives or all if less than 3
        alternatives = sorted_offers[:3]
        
        # Format alternative offers message
        alternatives_message = "Here are some alternative offers for you:\n\n"
        
        for i, offer in enumerate(alternatives, 1):
            interest_rate = offer.get("interest_rate", 0)
            monthly_emi = offer.get("monthly_emi", 0)
            processing_fee = offer.get("processing_fee", 0)
            product_name = offer.get("product_name", "Personal Loan")
            
            alternatives_message += f"Option {i}: {product_name} - ₹{loan_details.get('amount', 0):,} for {loan_details.get('tenure', 0)} months at {interest_rate}% interest. Monthly EMI: ₹{monthly_emi:,}, Processing fee: ₹{processing_fee:,}\n\n"
        
        alternatives_message += "Which option would you prefer, or would you like to explore different loan parameters?"
        
        return {
            "customer_response": alternatives_message,
            "internal_data": {
                "sales_stage": "negotiation",
                "loan_details": loan_details,
                "alternative_offers": alternatives,
                "available_offers": available_offers,
                "offers_presented": True,
                "confidence": 0.9
            },
            "next_action": "continue_sales"
        }
    
    def _handle_confirmation(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the confirmation stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the agent's response and updated internal data
        """
        # Extract relevant information
        loan_details = conversation_state.get("loan_details", {})
        selected_offer = conversation_state.get("selected_offer", {})
        
        # Format confirmation message
        loan_amount = loan_details.get("amount", 0)
        loan_tenure = loan_details.get("tenure", 0)
        interest_rate = selected_offer.get("interest_rate", 0)
        monthly_emi = selected_offer.get("monthly_emi", 0)
        processing_fee = selected_offer.get("processing_fee", 0)
        product_name = selected_offer.get("product_name", "Personal Loan")
        
        confirmation_message = f"Excellent choice! You've selected the {product_name} of ₹{loan_amount:,} for {loan_tenure} months at {interest_rate}% interest rate. Your monthly EMI will be ₹{monthly_emi:,}, with a processing fee of ₹{processing_fee:,}.\n\nI'll now transfer you to our verification process to confirm your details and proceed with the application. This will only take a few minutes."
        
        return {
            "customer_response": confirmation_message,
            "internal_data": {
                "sales_stage": "completed",
                "loan_details": loan_details,
                "selected_offer": selected_offer,
                "offer_confirmed": True,
                "confidence": 1.0
            },
            "next_action": "proceed_to_verification"
        }
    
    # Helper methods for extracting information from customer messages
    
    def _extract_loan_amount(self, message: str) -> Optional[float]:
        """Extract loan amount from customer message
        
        Args:
            message: The customer's message
            
        Returns:
            Float representing the loan amount, or None if not found
        """
        # In a real implementation, this would use NLP to extract amounts
        # For this mock, we'll use a simple approach
        
        # Look for currency symbols and numbers
        import re
        
        # Match patterns like "₹50,000", "50000", "50k", "5 lakh", etc.
        amount_patterns = [
            r'₹\s*(\d+[,\d]*)', # ₹50,000 or ₹50000
            r'Rs\.?\s*(\d+[,\d]*)', # Rs.50,000 or Rs50000
            r'INR\s*(\d+[,\d]*)', # INR50,000 or INR50000
            r'(\d+[,\d]*)\s*rupees', # 50,000 rupees or 50000 rupees
            r'(\d+)\s*k', # 50k
            r'(\d+(?:\.\d+)?)\s*lakh', # 5 lakh or 5.5 lakh
            r'(\d+(?:\.\d+)?)\s*lac', # 5 lac or 5.5 lac
            r'(\d+(?:\.\d+)?)\s*million', # 1 million or 1.5 million
        ]
        
        for pattern in amount_patterns:
            matches = re.search(pattern, message, re.IGNORECASE)
            if matches:
                amount_str = matches.group(1).replace(',', '')
                amount = float(amount_str)
                
                # Convert to rupees based on unit
                if 'k' in pattern:
                    amount *= 1000
                elif 'lakh' in pattern or 'lac' in pattern:
                    amount *= 100000
                elif 'million' in pattern:
                    amount *= 1000000
                
                return amount
        
        return None
    
    def _extract_loan_tenure(self, message: str) -> Optional[int]:
        """Extract loan tenure from customer message
        
        Args:
            message: The customer's message
            
        Returns:
            Integer representing the loan tenure in months, or None if not found
        """
        # In a real implementation, this would use NLP to extract tenure
        # For this mock, we'll use a simple approach
        
        import re
        
        # Match patterns like "36 months", "3 years", etc.
        tenure_patterns = [
            r'(\d+)\s*months', # 36 months
            r'(\d+)\s*month', # 1 month
            r'(\d+)\s*years', # 3 years
            r'(\d+)\s*year', # 1 year
            r'(\d+)\s*yr', # 3 yr
            r'(\d+)\s*yrs', # 3 yrs
        ]
        
        for pattern in tenure_patterns:
            matches = re.search(pattern, message, re.IGNORECASE)
            if matches:
                tenure = int(matches.group(1))
                
                # Convert years to months if necessary
                if 'year' in pattern or 'yr' in pattern:
                    tenure *= 12
                
                return tenure
        
        return None
    
    def _extract_loan_purpose(self, message: str) -> Optional[str]:
        """Extract loan purpose from customer message
        
        Args:
            message: The customer's message
            
        Returns:
            String representing the loan purpose, or None if not found
        """
        # In a real implementation, this would use NLP to extract purpose
        # For this mock, we'll use a simple keyword approach
        
        # Common loan purposes
        purposes = {
            "home renovation": ["renovation", "remodel", "repair", "fix", "home improvement"],
            "education": ["education", "college", "university", "school", "tuition", "study"],
            "medical": ["medical", "hospital", "surgery", "treatment", "health"],
            "wedding": ["wedding", "marriage", "ceremony"],
            "travel": ["travel", "vacation", "holiday", "trip"],
            "debt consolidation": ["consolidation", "consolidate", "refinance", "pay off"],
            "business": ["business", "startup", "venture", "enterprise"],
            "vehicle": ["car", "bike", "vehicle", "automobile"],
            "personal": ["personal", "general", "miscellaneous"]
        }
        
        message_lower = message.lower()
        
        for purpose, keywords in purposes.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return purpose
        
        return None
    
    def _wants_other_offers(self, message: str) -> bool:
        """Check if customer wants to see other offers
        
        Args:
            message: The customer's message
            
        Returns:
            Boolean indicating if customer wants other offers
        """
        # Keywords indicating interest in other offers
        keywords = ["other", "alternative", "different", "more", "options", "choices"]
        
        message_lower = message.lower()
        
        for keyword in keywords:
            if keyword in message_lower:
                return True
        
        return False
    
    def _wants_to_modify_loan(self, message: str) -> bool:
        """Check if customer wants to modify loan parameters
        
        Args:
            message: The customer's message
            
        Returns:
            Boolean indicating if customer wants to modify loan
        """
        # Keywords indicating desire to modify loan
        keywords = ["change", "modify", "adjust", "different", "increase", "decrease", "higher", "lower"]
        
        message_lower = message.lower()
        
        for keyword in keywords:
            if keyword in message_lower:
                return True
        
        # Also check if they mentioned a new amount or tenure
        if self._extract_loan_amount(message) or self._extract_loan_tenure(message):
            return True
        
        return False
    
    def _accepts_offer(self, message: str) -> bool:
        """Check if customer accepts the offer
        
        Args:
            message: The customer's message
            
        Returns:
            Boolean indicating if customer accepts the offer
        """
        # Keywords indicating acceptance
        positive_keywords = ["yes", "sure", "okay", "ok", "fine", "good", "great", "proceed", "accept", "go ahead", "sounds good"]
        
        message_lower = message.lower()
        
        for keyword in positive_keywords:
            if keyword in message_lower:
                return True
        
        return False

# Example usage
if __name__ == "__main__":
    # Test the Sales Agent
    sales_agent = SalesAgent()
    
    # Simulate a conversation
    conversation_state = {
        "conversation_history": [],
        "last_customer_message": "Hi, I'm interested in a personal loan."
    }
    
    # Initial greeting
    response = sales_agent.process("TC001", conversation_state)
    print(f"Sales Agent: {response['customer_response']}")
    
    # Update conversation state with customer response
    conversation_state["conversation_history"].append({
        "role": "agent",
        "message": response["customer_response"]
    })
    conversation_state["last_customer_message"] = "I need a loan of 5 lakhs for home renovation for 3 years."
    
    # Process need exploration
    response = sales_agent.process("TC001", conversation_state)
    print(f"\nCustomer: {conversation_state['last_customer_message']}")
    print(f"Sales Agent: {response['customer_response']}")
    
    # Update conversation state with offer details
    conversation_state["conversation_history"].append({
        "role": "customer",
        "message": conversation_state["last_customer_message"]
    })
    conversation_state["conversation_history"].append({
        "role": "agent",
        "message": response["customer_response"]
    })
    conversation_state.update(response["internal_data"])
    conversation_state["last_customer_message"] = "Yes, that sounds good. I'll take this offer."
    
    # Process negotiation
    response = sales_agent.process("TC001", conversation_state)
    print(f"\nCustomer: {conversation_state['last_customer_message']}")
    print(f"Sales Agent: {response['customer_response']}")
    
    # Print next action
    print(f"\nNext action: {response['next_action']}")