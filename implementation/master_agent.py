# Master Agent Implementation for Tata Capital Digital Loan Sales Assistant

import json
import uuid
import os
import requests
import traceback
import subprocess
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import google.generativeai as genai
import time
from google.api_core.exceptions import ResourceExhausted

from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Import Worker Agents
# These will be implemented in separate files
from implementation.sales_agent import SalesAgent
from implementation.verification_agent import VerificationAgent
from implementation.underwriting_agent import UnderwritingAgent
from implementation.sanction_letter_generator import SanctionLetterGenerator
from implementation.state_manager import StateManager
import sys

# Import Mock APIs
from implementation.mock_apis import CRMApi, OfferMartApi, CreditBureauApi, DocumentStorage

# Import CSV handling
import pandas as pd
import csv
import os

# Conversation State Enum
class ConversationStage(str, Enum):
    GREETING = "greeting"
    INTENT_CAPTURE = "intent_capture"
    SALES_EXPLORATION = "sales_exploration"
    VERIFICATION = "verification"
    UNDERWRITING = "underwriting"
    DOCUMENTATION = "documentation"
    CLOSURE = "closure"

# Decision Enum
class Decision(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEED_MORE_INFO = "need_more_info"

# Configure Gemini API
def configure_gemini_api(api_key=None):
    """Configure the Gemini API with the provided API key"""
    if api_key is None:
        # Try to get from environment variable
        api_key = os.environ.get("GEMINI_API_KEY")
        print(f"Using Gemini API key from environment variables: {'*' * (len(api_key) - 4) + api_key[-4:] if api_key else 'None'}")
    else:
        print(f"Using provided Gemini API key: {'*' * (len(api_key) - 4) + api_key[-4:] if api_key else 'None'}")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            
            # List available models
            print("Listing available models...")
            model_to_use = "gemini-pro" 
            try:
                for m in genai.list_models():
                    if "generateContent" in m.supported_generation_methods:
                        if 'gemini' in m.name:
                            model_to_use = m.name
                            break
            except Exception as e:
                print(f"Error listing models: {str(e)}")
                print(f"Using default model name: {model_to_use}")
            print(f"Using model: {model_to_use}")
            
            # Test the API connection
            model = genai.GenerativeModel(model_to_use)
            test_response = self.generate_content_with_retry(model, "Test connection")
            print(f"Gemini API configured successfully. Test response received: {len(test_response.text)} characters")
            return True, model_to_use
        except Exception as e:
            print(f"ERROR: Failed to configure Gemini API: {str(e)}")
            print(f"Error details: {traceback.format_exc()}")
            return False, None
    else:
        print("ERROR: Gemini API key not found. Please set GEMINI_API_KEY environment variable.")
        return False, None

# Master Agent State
class ConversationState:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        self.stage = ConversationStage.GREETING
        self.customer_id = None
        self.customer_name = None
        self.customer_phone = None
        self.customer_details = {
            # Personal Information
            "full_name": None,
            "date_of_birth": None,
            "father_or_spouse_name": None,
            "permanent_address": None,
            "current_address": None,
            "mobile_number": None,
            "email_id": None,
            "marital_status": None,
            "number_of_dependents": None,
            "nationality": None,
            "pan_number": None,
            "aadhaar_number": None,
            "id_proof": None,
            "address_proof": None,
            
            # Employment Information
            "employment_type": None,  # salaried or self-employed
            "company_or_business_name": None,
            "job_designation": None,
            "years_of_experience": None,
            "monthly_income": None,
            "annual_income": None,
            "employer_or_business_details": None,
            
            # Financial Information
            "existing_loans_or_emis": None,
            "monthly_financial_obligations": None,
            "savings_and_investments": None,
            "credit_score": None,
            "cibil_score": None,
            
            # Income Documentation
            "salary_slips_available": False,
            "form_16_or_itr_available": False,
            "bank_statements_available": False,
            "gst_certificate_available": False,  # for self-employed
            "trade_license_available": False,  # for self-employed
            "profit_and_loss_statement_available": False,  # for self-employed
            "balance_sheet_available": False,  # for self-employed
            
            # Additional Documents
            "photographs": None,
            "signature": None
        }
        self.loan_details = {
            "amount": None,
            "tenure": None,
            "purpose": None,
            "interest_rate": None,
            "emi": None,
            "processing_fee": None
        }
        self.selected_offer = {}
        self.verification_status = {}
        self.underwriting_result = {}
        self.decision = Decision.PENDING
        self.sanction_letter_id = None
        self.messages = []
        self.errors = []
        self.next_agent = None
        self.api_retries = {}
        self.document_uploads = {}
        self.gemini_history = []
        self.recursion_depth = 0   # ✅ Added line — fixes LangGraph recursion issue

    
    def to_dict(self) -> Dict:
        """Convert state to dictionary for serialization"""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "stage": self.stage.value,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "customer_details": self.customer_details,
            "loan_details": self.loan_details,
            "selected_offer": self.selected_offer,
            "verification_status": self.verification_status,
            "underwriting_result": self.underwriting_result,
            "decision": self.decision.value,
            "sanction_letter_id": self.sanction_letter_id,
            "messages": self.messages,
            "errors": self.errors,
            "next_agent": self.next_agent,
            "api_retries": self.api_retries,
            "document_uploads": self.document_uploads
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationState':
        """Create state from dictionary"""
        state = cls()
        state.session_id = data.get("session_id", state.session_id)
        state.start_time = datetime.fromisoformat(data.get("start_time", state.start_time.isoformat()))
        state.stage = ConversationStage(data.get("stage", state.stage.value))
        state.gemini_history = data.get("gemini_history", [])
        state.customer_id = data.get("customer_id", state.customer_id)
        state.customer_name = data.get("customer_name", state.customer_name)
        state.customer_phone = data.get("customer_phone", state.customer_phone)
        state.customer_details = data.get("customer_details", state.customer_details)
        state.loan_details = data.get("loan_details", state.loan_details)
        state.selected_offer = data.get("selected_offer", state.selected_offer)
        state.verification_status = data.get("verification_status", state.verification_status)
        state.underwriting_result = data.get("underwriting_result", state.underwriting_result)
        state.decision = Decision(data.get("decision", state.decision.value))
        state.sanction_letter_id = data.get("sanction_letter_id", state.sanction_letter_id)
        state.messages = data.get("messages", state.messages)
        state.errors = data.get("errors", state.errors)
        state.next_agent = data.get("next_agent", state.next_agent)
        state.api_retries = data.get("api_retries", state.api_retries)
        state.document_uploads = data.get("document_uploads", state.document_uploads)
        return state
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_error(self, error_type: str, error_message: str, agent: Optional[str] = None) -> None:
        """Add an error to the error log"""
        self.errors.append({
            "type": error_type,
            "message": error_message,
            "agent": agent,
            "timestamp": datetime.now().isoformat()
        })

# Master Agent Class
class MasterAgent:
    def __init__(self, state_file_path="implementation/conversation_state.json", gemini_api_key=None):
        print("\n" + "="*50)
        print("Initializing Master Agent for Tata Capital Digital Loan Sales Assistant")
        print("="*50)
        
        print("Creating conversation state...")
        self.state = ConversationState()

    def generate_content_with_retry(self, model, prompt, max_retries=5, backoff_factor=2):
        retries = 0
        while retries < max_retries:
            try:
                response = self.generate_content_with_retry(model, prompt)
                return response
            except ResourceExhausted as e:
                retries += 1
                if retries >= max_retries:
                    raise e
                sleep_time = backoff_factor ** retries
                print(f"Rate limit exceeded. Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
        
        # Initialize state manager
        print("Initializing state manager...")
        self.state_manager = StateManager()
        print("State manager initialized")
        
        # Configure Gemini API
        print("Configuring Gemini API...")
        self.gemini_configured, self.gemini_model = configure_gemini_api(gemini_api_key)
        print(f"Gemini API configured: {self.gemini_configured}")
        print(f"Using model: {self.gemini_model}")
        
        # Load CSV data
        print("Loading CSV data...")
        self.customers_df = self._load_csv_data('data/customers.csv')
        self.offer_mart_df = self._load_csv_data('data/offer_mart.csv')
        self.crm_data_df = self._load_csv_data('data/crm_data.csv')
        self.credit_bureau_df = self._load_csv_data('data/credit_bureau.csv')
        print(f"Loaded {len(self.customers_df)} customer records")
        print(f"Loaded {len(self.offer_mart_df)} offer records")
        
        # Initialize APIs
        print("Initializing API connections...")
        self.crm_api = CRMApi()
        self.offer_mart_api = OfferMartApi()
        self.credit_bureau_api = CreditBureauApi()
        self.document_storage = DocumentStorage()
        print("API connections initialized")
        
        # Initialize Worker Agents
        print("Initializing specialized worker agents...")
        self.sales_agent = SalesAgent(offer_mart_df=self.offer_mart_df)
        print("- Sales Agent initialized")
        self.verification_agent = VerificationAgent(crm_data_df=self.crm_data_df)
        print("- Verification Agent initialized")
        self.underwriting_agent = UnderwritingAgent(customers_df=self.customers_df, credit_bureau_df=self.credit_bureau_df)
        print("- Underwriting Agent initialized")
        self.sanction_letter_agent = SanctionLetterGenerator()
        print("- Sanction Letter Generator initialized")
        
        # Initialize LangGraph
        print("Building LangGraph for conversation flow...")
        self.graph = self._build_graph()
        print("LangGraph built successfully")
        
        # Create output directory if it doesn't exist
        print("Creating output directory...")
        os.makedirs('output', exist_ok=True)
        
        # Start parallel processes
        print("Starting parallel processes...")
        self._start_parallel_processes()
        print("Parallel processes started")
        print("="*50 + "\n")
        
    def process_document(self, document_path: str, document_type: str) -> Dict:
        """Process an uploaded document using Gemini API for text extraction"""
        if not self.gemini_configured:
            self.state.add_error("API", "Gemini API not configured. Using mock document processing.")
            return {"status": "processed", "type": document_type, "path": document_path, "mock": True}
        
        try:
            # For PDF documents, we would extract text and then send to Gemini
            # For images, we can use Gemini's multimodal capabilities directly
            
            # Mock document content for now
            # In a real implementation, we would read the file and extract text/image
            document_content = "This is a salary slip for the amount of 75000 INR per month."
            
            # Prepare prompt for Gemini
            prompt = f"""
            You are an AI assistant for Tata Capital's loan processing department.
            Extract key information from the following {document_type} document:
            
            Document content: {document_content}
            
            If this is a salary slip, extract:
            - Monthly salary amount
            - Employee name
            - Employer name
            - Date of salary
            
            Format your response as JSON with the following structure:
            {{"extracted_data": {{"key": "value"}}, "verification_result": "valid|invalid", "confidence": 0.XX}}
            """
            
            # Call Gemini API
            model = genai.GenerativeModel(self.gemini_model)
            response = self.generate_content_with_retry(model, prompt)
            
            # Parse the response
            try:
                result = json.loads(response.text)
                
                # Add document to storage
                document_id = self.document_storage.store_document(
                    document_path, 
                    document_type,
                    metadata={
                        "processed_at": datetime.now().isoformat(),
                        "extraction_result": result
                    }
                )
                
                # Add to state
                self.state.document_uploads[document_id] = {
                    "path": document_path,
                    "type": document_type,
                    "processed_at": datetime.now().isoformat(),
                    "extraction_result": result
                }
                
                # Add to Gemini history
                self.state.gemini_history.append({
                    "prompt": prompt,
                    "response": response.text,
                    "timestamp": datetime.now().isoformat(),
                    "document_id": document_id
                })
                
                return {
                    "status": "processed",
                    "document_id": document_id,
                    "type": document_type,
                    "path": document_path,
                    "extraction_result": result
                }
                
            except json.JSONDecodeError:
                self.state.add_error("Processing", "Failed to parse Gemini document extraction response as JSON")
                return {"status": "error", "type": document_type, "path": document_path, "error": "Failed to parse extraction result"}
            
        except Exception as e:
            self.state.add_error("API", f"Gemini API document processing error: {str(e)}")
            return {"status": "error", "type": document_type, "path": document_path, "error": str(e)}
    
    def _load_csv_data(self, file_path):
        """Load data from CSV file into a pandas DataFrame"""
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            print(f"Error loading CSV data from {file_path}: {str(e)}")
            return pd.DataFrame()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for orchestration"""
        # Define the graph
        builder = StateGraph(ConversationState)
        
        # Add nodes for each agent and processing step
        builder.add_node("process_user_input", self._process_user_input)
        builder.add_node("determine_next_step", self._determine_next_step)
        builder.add_node("sales_agent", self._run_sales_agent)
        builder.add_node("verification_agent", self._run_verification_agent)
        builder.add_node("underwriting_agent", self._run_underwriting_agent)
        builder.add_node("sanction_letter_agent", self._run_sanction_letter_agent)
        builder.add_node("generate_response", self._generate_response)
        
        # Define the edges
        builder.add_edge("process_user_input", "determine_next_step")
        
        # Conditional routing based on next_agent
        builder.add_conditional_edges(
            "determine_next_step",
            self._route_to_agent,
            {
                "sales_agent": "sales_agent",
                "verification_agent": "verification_agent",
                "underwriting_agent": "underwriting_agent",
                "sanction_letter_agent": "sanction_letter_agent",
                "generate_response": "generate_response",
                "end": END
            }
        )
        
        # Connect all agent nodes back to generate_response
        builder.add_edge("sales_agent", "generate_response")
        builder.add_edge("verification_agent", "generate_response")
        builder.add_edge("underwriting_agent", "generate_response")
        builder.add_edge("sanction_letter_agent", "generate_response")
        
        # Set the entry point
        builder.set_entry_point("process_user_input")
        
        return builder.compile()
    
    def _process_user_input(self, state: Dict) -> Dict:
        """Process user input and extract intent using Gemini API"""
        # Convert dict to ConversationState if needed
        if not isinstance(state, ConversationState):
            state_obj = ConversationState.from_dict(state)
        else:
            state_obj = state
            
        try:
            if not self.gemini_configured:
                state_obj.add_error("API", "Gemini API not configured. Using mock processing.")
                # ✅ Ensures valid dict return for LangGraph compatibility
                return {
                    "response": "Using mock processing", 
                    "next_agent": "determine_next_step", 
                    "state": state_obj.to_dict()
                }
            
            # Get the latest user message
            if state_obj.messages and state_obj.messages[-1]["role"] == "user":
                user_message = state_obj.messages[-1]["content"]
                
                # Prepare conversation history for context
                conversation_history = ""
                for msg in state_obj.messages[-10:]:  # Last 10 messages for better context
                    if msg["role"] == "user":
                        conversation_history += f"User: {msg['content']}\n"
                    elif msg["role"] == "assistant":
                        conversation_history += f"Assistant: {msg['content']}\n"
                
                # Prepare prompt for Gemini with more detailed extraction
                prompt = f"""
                You are an AI assistant for Tata Capital's loan sales process. 
                Extract the user's intent and any relevant information from their message.
                
                Current conversation stage: {state_obj.stage.value}
                
                Recent conversation history:
                {conversation_history}
                
                Latest user message: {user_message}
                
                Extract the following information (if present):
                - Loan amount requested (extract exact number)
                - Loan tenure requested (extract number and unit - months/years)
                - Loan purpose (e.g., home renovation, education, vehicle, personal, etc.)
                - Customer identification information (name, phone, email, etc.)
                - Income information (monthly or annual salary)
                - Employment details (employer name, job title, years of employment)
                - Verification information (any documents mentioned, ID numbers, etc.)
                
                Also extract comprehensive customer details including:
                - Full name, date of birth, father's or spouse's name
                - Permanent and current address
                - Mobile number, email ID, marital status, number of dependents, nationality
                - PAN number, Aadhaar number, ID proof, address proof
                - Employment type (salaried or self-employed), company/business name, job designation
                - Years of experience, monthly/annual income, employer/business details
                - Existing loans or EMIs, monthly financial obligations, savings and investments
                - Credit score (CIBIL score)
                - Document availability (salary slips, Form 16/ITR, bank statements, GST certificate, trade license, profit & loss statement, balance sheet)
                - Photographs and signature availability
                
                Format your response as JSON with the following structure:
                {{"intent": "<primary_intent>", "entities": {{"key": "value"}}, "next_stage": "<suggested_next_stage>", "confidence": 0.XX}}
                
                For intent, choose from: greeting, loan_inquiry, provide_information, document_submission, confirmation, rejection, other
                For next_stage, choose from: greeting, intent_capture, sales_exploration, verification, underwriting, documentation, closure
                
                Ensure the JSON is valid and properly formatted. Only include fields where you have extracted information.
                """
                
                try:
                    # Call Gemini API
                    model = genai.GenerativeModel(self.gemini_model)
                    response = self.generate_content_with_retry(model, prompt)
                    
                    # Parse the response
                    try:
                        # Extract text from response
                        response_text = response.text
                        
                        # Try to find JSON in the response
                        import re
                        json_match = re.search(r'\{[\s\S]*\}', response_text)
                        if json_match:
                            json_str = json_match.group(0)
                            result = json.loads(json_str)
                        else:
                            result = json.loads(response_text)
                        
                        # Update state with extracted information
                        if "entities" in result:
                            entities = result["entities"]
                            
                            # Update loan details if present
                            if "loan_amount" in entities:
                                state_obj.loan_details["amount"] = entities["loan_amount"]
                            if "loan_tenure" in entities:
                                state_obj.loan_details["tenure"] = entities["loan_tenure"]
                            if "loan_purpose" in entities:
                                state_obj.loan_details["purpose"] = entities["loan_purpose"]
                            
                            # Update customer details if present
                            if "customer_name" in entities:
                                state_obj.customer_name = entities["customer_name"]
                                state_obj.customer_details["full_name"] = entities["customer_name"]
                            if "phone" in entities:
                                state_obj.customer_phone = entities["phone"]
                                state_obj.customer_details["mobile_number"] = entities["phone"]
                            if "email" in entities:
                                state_obj.customer_details["email_id"] = entities["email"]
                            
                            # Map all comprehensive customer details
                            customer_detail_mappings = {
                                # Personal Information
                                "full_name": "full_name",
                                "date_of_birth": "date_of_birth",
                                "father_or_spouse_name": "father_or_spouse_name",
                                "permanent_address": "permanent_address",
                                "current_address": "current_address",
                                "mobile_number": "mobile_number",
                                "email_id": "email_id",
                                "marital_status": "marital_status",
                                "number_of_dependents": "number_of_dependents",
                                "nationality": "nationality",
                                "pan_number": "pan_number",
                                "aadhaar_number": "aadhaar_number",
                                "id_proof": "id_proof",
                                "address_proof": "address_proof",
                                
                                # Employment Information
                                "employment_type": "employment_type",
                                "company_or_business_name": "company_or_business_name",
                                "job_designation": "job_designation",
                                "years_of_experience": "years_of_experience",
                                "monthly_income": "monthly_income",
                                "annual_income": "annual_income",
                                "employer_or_business_details": "employer_or_business_details",
                                
                                # Financial Information
                                "existing_loans_or_emis": "existing_loans_or_emis",
                                "monthly_financial_obligations": "monthly_financial_obligations",
                                "savings_and_investments": "savings_and_investments",
                                "credit_score": "credit_score",
                                "cibil_score": "cibil_score",
                                
                                # Document Availability
                                "salary_slips_available": "salary_slips_available",
                                "form_16_or_itr_available": "form_16_or_itr_available",
                                "bank_statements_available": "bank_statements_available",
                                "gst_certificate_available": "gst_certificate_available",
                                "trade_license_available": "trade_license_available",
                                "profit_and_loss_statement_available": "profit_and_loss_statement_available",
                                "balance_sheet_available": "balance_sheet_available",
                                "photographs": "photographs",
                                "signature": "signature"
                            }
                            
                            # Update customer details based on mapped entities
                            for entity_key, detail_key in customer_detail_mappings.items():
                                if entity_key in entities:
                                    state_obj.customer_details[detail_key] = entities[entity_key]
                            
                            # Handle additional entities that don't have direct mappings
                            for key, value in entities.items():
                                if key not in ["loan_amount", "loan_tenure", "loan_purpose", "customer_name", "phone"] and key not in customer_detail_mappings.keys():
                                    # Only add if the key doesn't already exist in customer_details
                                    if key not in state_obj.customer_details:
                                        state_obj.customer_details[key] = value
                        
                        # Update next stage if suggested
                        if "next_stage" in result:
                            suggested_stage = result["next_stage"]
                            try:
                                state_obj.stage = ConversationStage(suggested_stage)
                            except ValueError:
                                # Invalid stage suggestion, ignore
                                pass
                        
                        # Add to Gemini history
                        state_obj.gemini_history.append({
                            "prompt": prompt,
                            "response": response_text,
                            "timestamp": datetime.now().isoformat(),
                            "parsed_result": result
                        })
                        
                        # Print extracted information for debugging
                        print(f"Extracted information: {json.dumps(result, indent=2)}")
                        
                    except json.JSONDecodeError as e:
                        state_obj.add_error("Processing", f"Failed to parse Gemini response as JSON: {str(e)}")
                        print(f"JSON parsing error: {str(e)}")
                        print(f"Response text: {response_text}")
                
                except Exception as e:
                    state_obj.add_error("API", f"Gemini API error: {str(e)}")
                    print(f"Gemini API error in _process_user_input: {str(e)}")
        except Exception as e:
            # ✅ Fallback for any exceptions to ensure valid dict return
            state_obj.add_error("exception", f"Error in _process_user_input: {str(e)}")
            return {
                "response": f"Error encountered: {str(e)}", 
                "next_agent": "determine_next_step", 
                "state": state_obj.to_dict()
            }
        
        # ✅ Ensures valid dict return for LangGraph compatibility
        return {
            "response": "Processed user input", 
            "next_agent": "determine_next_step",
            "state": state_obj.to_dict()
        }

    
    def _determine_next_step(self, state: Dict) -> Dict:
        """Determine the next step based on the current state"""
        # Convert dict to ConversationState if needed
        if not isinstance(state, ConversationState):
            state_obj = ConversationState.from_dict(state)
        else:
            state_obj = state
        
        try:    
            # Logic to determine which agent to call next based on conversation stage
            if state_obj.stage == ConversationStage.GREETING:
                # If we have customer ID, move to intent capture
                if state_obj.customer_id:
                    state_obj.stage = ConversationStage.INTENT_CAPTURE
                    state_obj.next_agent = "generate_response"
                else:
                    # Need to identify customer first
                    state_obj.next_agent = "generate_response"
            
            elif state_obj.stage == ConversationStage.INTENT_CAPTURE:
                # Move to sales exploration
                state_obj.stage = ConversationStage.SALES_EXPLORATION
                state_obj.next_agent = "sales_agent"
            
            elif state_obj.stage == ConversationStage.SALES_EXPLORATION:
                # If sales exploration is complete, move to verification
                if state_obj.loan_details.get("amount") and state_obj.loan_details.get("tenure"):
                    state_obj.stage = ConversationStage.VERIFICATION
                    state_obj.next_agent = "verification_agent"
                else:
                    # Continue with sales exploration
                    state_obj.next_agent = "sales_agent"
            
            elif state_obj.stage == ConversationStage.VERIFICATION:
                # If verification is complete, move to underwriting
                if state_obj.verification_status.get("verified", False):
                    state_obj.stage = ConversationStage.UNDERWRITING
                    state_obj.next_agent = "underwriting_agent"
                else:
                    # Continue with verification
                    state_obj.next_agent = "verification_agent"
            
            elif state_obj.stage == ConversationStage.UNDERWRITING:
                # If underwriting is complete, move to documentation or closure
                if state_obj.decision in [Decision.APPROVED, Decision.REJECTED]:
                    if state_obj.decision == Decision.APPROVED:
                        state_obj.stage = ConversationStage.DOCUMENTATION
                        state_obj.next_agent = "sanction_letter_agent"
                    else:
                        state_obj.stage = ConversationStage.CLOSURE
                        state_obj.next_agent = "generate_response"
                elif state_obj.decision == Decision.NEED_MORE_INFO:
                    # Stay in underwriting but ask for more info
                    state_obj.next_agent = "underwriting_agent"
                else:
                    # Continue with underwriting
                    state_obj.next_agent = "underwriting_agent"
            
            elif state_obj.stage == ConversationStage.DOCUMENTATION:
                # If documentation is complete, move to closure
                if state_obj.sanction_letter_id:
                    state_obj.stage = ConversationStage.CLOSURE
                    state_obj.next_agent = "generate_response"
                else:
                    # Continue with documentation
                    state_obj.next_agent = "sanction_letter_agent"
            
            elif state_obj.stage == ConversationStage.CLOSURE:
                # End the conversation
                state_obj.next_agent = "end"
            
            else:
                # Default case for any unexpected stage
                print(f"Warning: Unexpected conversation stage '{state_obj.stage}', defaulting to 'generate_response'")
                state_obj.next_agent = "generate_response"
                
            # Ensure next_agent is always set to a valid value
            if not state_obj.next_agent:
                print("Warning: next_agent was not set, defaulting to 'generate_response'")
                state_obj.next_agent = "generate_response"
                
        except Exception as e:
            # Catch any exceptions and provide a safe fallback
            print(f"Error in _determine_next_step: {e}")
            state_obj.next_agent = "generate_response"
            state_obj.add_error("exception", f"Error in _determine_next_step: {str(e)}")
            # ✅ Fallback for any exceptions to ensure valid dict return
            return {
                "response": f"Error encountered: {str(e)}",
                "next_agent": "generate_response",
                "state": state_obj.to_dict()
            }
            
        # ✅ Ensures valid dict return for LangGraph compatibility
        return {
            "response": "Determined next step",
            "next_agent": state_obj.next_agent,  # ✅ Explicitly tell LangGraph where to go next
            "state": state_obj.to_dict()
        }

    
    def _route_to_agent(self, state: Dict) -> str:
        """Route to the appropriate agent based on conversation stage or fallback safely."""
        try:
            # Ensure we always work with a valid ConversationState
            if not isinstance(state, ConversationState):
                try:
                    state_obj = ConversationState.from_dict(state)
                except Exception:
                    print("⚠️ Failed to convert state dict properly — creating a fresh ConversationState.")
                    state_obj = ConversationState()
            else:
                state_obj = state

            # Define allowed routing targets
            valid_agents = [
                "sales_agent",
                "verification_agent",
                "underwriting_agent",
                "sanction_letter_agent",
                "generate_response",
                "end"
            ]

            next_agent = getattr(state_obj, "next_agent", None)

            # Validate and fallback
            if next_agent in valid_agents:
                print(f"➡️ Routing to next agent: {next_agent}")
                return {
                    "response": "",
                    "next_agent": next_agent,
                    "state": state_obj.to_dict()
                }
            else:
                print(f"⚠️ Invalid or missing next_agent: {next_agent} — defaulting to 'generate_response'")
                state_obj.next_agent = "generate_response"
                return {
                    "response": "",
                    "next_agent": "generate_response",
                    "state": state_obj.to_dict()
                }

        except Exception as e:
            print(f"❌ Error in _route_to_agent: {str(e)} — returning 'generate_response'")
            # ✅ Fallback for any exceptions to ensure valid dict return
            return {
                "response": f"Error encountered in routing: {str(e)}",
                "next_agent": "generate_response",
                "state": state_obj.to_dict()
            }

    def _run_sales_agent(self, state: Dict) -> Dict:
        """Run the Sales Agent"""
        # Convert dict to ConversationState if needed
        if not isinstance(state, ConversationState):
            state_obj = ConversationState.from_dict(state)
        else:
            state_obj = state
            
        try:
            # Prepare input for Sales Agent
            agent_input = {
                "customer_id": state_obj.customer_id,
                "customer_name": state_obj.customer_name,
                "customer_details": state_obj.customer_details,
                "conversation_history": state_obj.messages,
                "current_loan_details": state_obj.loan_details
            }
            
            # Call Sales Agent
            result = self.sales_agent.process(agent_input)
            
            # Update state with Sales Agent results
            if "loan_details" in result:
                state_obj.loan_details.update(result["loan_details"])
            
            if "selected_offer" in result:
                state_obj.selected_offer = result["selected_offer"]
            
            # Add agent's response to messages
            if "customer_response" in result:
                state_obj.add_message("assistant", result["customer_response"])
            
            # Check for any errors
            if "error" in result:
                state_obj.add_error("sales_agent", result["error"], "sales_agent")
        
        except Exception as e:
            state_obj.add_error("exception", str(e), "sales_agent")
            # ✅ Fallback for any exceptions to ensure valid dict return
            return {
                "response": f"Error encountered in sales agent: {str(e)}",
                "next_agent": "determine_next_step",
                "state": state_obj.to_dict()
            }
        
        # ✅ Ensures valid dict return for LangGraph compatibility
        response = "Sales agent processed request"
        if state_obj.messages and state_obj.messages[-1]["role"] == "assistant":
            response = state_obj.messages[-1]["content"]
        return {
            "response": response, 
            "next_agent": "determine_next_step",
            "state": state_obj.to_dict()
        }
    
    def _run_verification_agent(self, state: Dict) -> Dict:
        """Run the Verification Agent"""
        # Convert dict to ConversationState if needed
        if not isinstance(state, ConversationState):
            state_obj = ConversationState.from_dict(state)
        else:
            state_obj = state
            
        try:
            # Save current state to file for parallel processes
            self.state_manager.save_state(state_obj)
            
            # Call Verification Agent
            state_obj = self.verification_agent.process(state_obj)
            
            # Load any updates from parallel processes
            state_obj = self.state_manager.load_state(state_obj)
            
            # Check for any errors
            if hasattr(state_obj, 'errors') and state_obj.errors:
                for error in state_obj.errors:
                    if error.get('source') == 'verification_agent':
                        print(f"Verification error: {error.get('message')}")
        
        except Exception as e:
            state_obj.add_error("exception", str(e), "verification_agent")
            # ✅ Fallback for any exceptions to ensure valid dict return
            return {
                "response": f"Error encountered in verification agent: {str(e)}",
                "next_agent": "determine_next_step",
                "state": state_obj.to_dict()
            }
        
        # ✅ Ensures valid dict return for LangGraph compatibility
        response = "Verification agent processed request"
        if state_obj.messages and state_obj.messages[-1]["role"] == "assistant":
            response = state_obj.messages[-1]["content"]
        return {
            "response": response, 
            "next_agent": "determine_next_step",
            "state": state_obj.to_dict()
        }
    
    def _run_underwriting_agent(self, state: Dict) -> Dict:
        """Run the Underwriting Agent"""
        # Convert dict to ConversationState if needed
        if not isinstance(state, ConversationState):
            state_obj = ConversationState.from_dict(state)
        else:
            state_obj = state
            
        try:
            # Save current state to file for parallel processes
            self.state_manager.save_state(state_obj)
            
            # Call Underwriting Agent
            state_obj = self.underwriting_agent.process(state_obj)
            
            # Load any updates from parallel processes
            state_obj = self.state_manager.load_state(state_obj)
            
            # Check for any errors
            if hasattr(state_obj, 'errors') and state_obj.errors:
                for error in state_obj.errors:
                    if error.get('source') == 'underwriting_agent':
                        print(f"Underwriting error: {error.get('message')}")
        
        except Exception as e:
            state_obj.add_error("exception", str(e), "underwriting_agent")
            # ✅ Fallback for any exceptions to ensure valid dict return
            return {
                "response": f"Error encountered in underwriting agent: {str(e)}",
                "next_agent": "determine_next_step",
                "state": state_obj.to_dict()
            }
        
        # ✅ Ensures valid dict return for LangGraph compatibility
        response = "Underwriting agent processed request"
        if state_obj.messages and state_obj.messages[-1]["role"] == "assistant":
            response = state_obj.messages[-1]["content"]
        return {
            "response": response, 
            "next_agent": "determine_next_step",
            "state": state_obj.to_dict()
        }
        
    def _start_parallel_processes(self):
        """Start parallel processes for document verification and sanction letter generation"""
        try:
            # Get the implementation directory
            implementation_dir = 'implementation'
            
            # Use the run_parallel_processes.py script
            run_script = os.path.join(implementation_dir, "run_parallel_processes.py")
            state_file = os.path.join(implementation_dir, "conversation_state.json")
            
            # Start the process
            subprocess.Popen([sys.executable, run_script, "--state_file", state_file],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
            
            print(f"Parallel processes started successfully using {run_script}")
            print(f"Using state file: {state_file}")
            
        except Exception as e:
            print(f"Error starting parallel processes: {e}")
            traceback.print_exc()
    
    def _run_sanction_letter_agent(self, state: Dict) -> Dict:
        """Run the Sanction Letter Agent"""
        # Convert dict to ConversationState if needed
        if not isinstance(state, ConversationState):
            state_obj = ConversationState.from_dict(state)
        else:
            state_obj = state
            
        try:
            # Save current state to file for parallel processes
            self.state_manager.save_state(state_obj)
            
            # Call Sanction Letter Agent
            state_obj = self.sanction_letter_agent.process(state_obj)
            
            # Load any updates from parallel processes
            state_obj = self.state_manager.load_state(state_obj)
            
            # Check if sanction_letter_id was set by parallel process
            if state_obj.sanction_letter_id:
                print(f"Sanction letter ID set to: {state_obj.sanction_letter_id}")
            
            # Check for any errors
            if hasattr(state_obj, 'errors') and state_obj.errors:
                for error in state_obj.errors:
                    if error.get('source') == 'sanction_letter_agent':
                        print(f"Sanction letter error: {error.get('message')}")
        
        except Exception as e:
            state_obj.add_error("exception", str(e), "sanction_letter_agent")
            # ✅ Fallback for any exceptions to ensure valid dict return
            return {
                "response": f"Error encountered in sanction letter agent: {str(e)}",
                "next_agent": "determine_next_step",
                "state": state_obj.to_dict()
            }
        
        # ✅ Ensures valid dict return for LangGraph compatibility
        response = "Sanction letter agent processed request"
        if state_obj.messages and state_obj.messages[-1]["role"] == "assistant":
            response = state_obj.messages[-1]["content"]
        return {
            "response": response, 
            "next_agent": "determine_next_step",
            "state": state_obj.to_dict()
        }
    
    def _generate_response(self, state: Dict) -> Dict:
        """Generate a response to the user using Gemini API"""
        # Convert dict to ConversationState if needed
        if not isinstance(state, ConversationState):
            state_obj = ConversationState.from_dict(state)
        else:
            state_obj = state
            
        if not self.gemini_configured:
            state_obj.add_error("API", "Gemini API not configured. Using mock response.")
            # Add a mock response
            response_text = "I understand your request. Let me help you with that."
            state_obj.add_message("assistant", response_text)
            
            # Set next_agent to end to break the recursion
            state_obj.next_agent = "end"
            
            # ✅ Ensures valid dict return for LangGraph compatibility
            return {
                "response": response_text, 
                "next_agent": "end",
                "state": state_obj.to_dict()
            }
        
        # Prepare context for Gemini with more detailed information
        context = {
            "stage": state_obj.stage.value,
            "customer_name": state_obj.customer_name,
            "customer_details": state_obj.customer_details,
            "loan_details": state_obj.loan_details,
            "verification_status": state_obj.verification_status,
            "underwriting_result": state_obj.underwriting_result,
            "decision": state_obj.decision.value,
            "selected_offer": state_obj.selected_offer,
            "sanction_letter_id": state_obj.sanction_letter_id
        }
        
        # Prepare conversation history
        conversation_history = ""
        for msg in state_obj.messages[-8:]:  # Last 8 messages for better context
            if msg["role"] == "user":
                conversation_history += f"User: {msg['content']}\n"
            elif msg["role"] == "assistant":
                conversation_history += f"Assistant: {msg['content']}\n"
        
        # Get the latest user message
        latest_user_message = ""
        for msg in reversed(state_obj.messages):
            if msg["role"] == "user":
                latest_user_message = msg["content"]
                break
        
        # Prepare customer greeting with name if available
        customer_greeting = f"Dear {state_obj.customer_name}" if state_obj.customer_name else "Dear valued customer"
        
        # Prepare loan details summary if available
        loan_summary = ""
        if state_obj.loan_details.get("amount") and state_obj.loan_details.get("tenure"):
            loan_summary = f"You're interested in a loan of {state_obj.loan_details['amount']} for a tenure of {state_obj.loan_details['tenure']}"
            if state_obj.loan_details.get("purpose"):
                loan_summary += f" for {state_obj.loan_details['purpose']}"
        
        # Prepare comprehensive customer profile summary
        customer_profile = ""
        if state_obj.customer_details:
            profile_parts = []
            
            # Personal Information
            if state_obj.customer_details.get("full_name"):
                profile_parts.append(f"Name: {state_obj.customer_details['full_name']}")
            if state_obj.customer_details.get("date_of_birth"):
                profile_parts.append(f"DOB: {state_obj.customer_details['date_of_birth']}")
            if state_obj.customer_details.get("marital_status"):
                profile_parts.append(f"Marital Status: {state_obj.customer_details['marital_status']}")
            if state_obj.customer_details.get("number_of_dependents"):
                profile_parts.append(f"Dependents: {state_obj.customer_details['number_of_dependents']}")
            
            # Employment Information
            if state_obj.customer_details.get("employment_type"):
                profile_parts.append(f"Employment: {state_obj.customer_details['employment_type']}")
            if state_obj.customer_details.get("company_or_business_name"):
                profile_parts.append(f"Company: {state_obj.customer_details['company_or_business_name']}")
            if state_obj.customer_details.get("job_designation"):
                profile_parts.append(f"Designation: {state_obj.customer_details['job_designation']}")
            if state_obj.customer_details.get("years_of_experience"):
                profile_parts.append(f"Experience: {state_obj.customer_details['years_of_experience']} years")
            
            # Financial Information
            if state_obj.customer_details.get("monthly_income"):
                profile_parts.append(f"Monthly Income: {state_obj.customer_details['monthly_income']}")
            elif state_obj.customer_details.get("annual_income"):
                profile_parts.append(f"Annual Income: {state_obj.customer_details['annual_income']}")
            if state_obj.customer_details.get("existing_loans_or_emis"):
                profile_parts.append(f"Existing EMIs: {state_obj.customer_details['existing_loans_or_emis']}")
            if state_obj.customer_details.get("credit_score") or state_obj.customer_details.get("cibil_score"):
                score = state_obj.customer_details.get("credit_score") or state_obj.customer_details.get("cibil_score")
                profile_parts.append(f"Credit Score: {score}")
            
            # Document Status
            documents_ready = []
            doc_fields = [
                "salary_slips_available", "form_16_or_itr_available", "bank_statements_available",
                "gst_certificate_available", "trade_license_available", 
                "profit_and_loss_statement_available", "balance_sheet_available"
            ]
            for field in doc_fields:
                if state_obj.customer_details.get(field):
                    doc_name = field.replace("_available", "").replace("_", " ").title()
                    documents_ready.append(doc_name)
            
            if documents_ready:
                profile_parts.append(f"Documents Ready: {', '.join(documents_ready)}")
            
            if profile_parts:
                customer_profile = "Customer Profile: " + " | ".join(profile_parts)
        
        # Prepare prompt for Gemini with highly persuasive language
        prompt = f"""
        You are a highly persuasive and empathetic loan sales assistant for Tata Capital. Your goal is to guide customers through the loan process and help them get approved for a loan that meets their needs. You must be EXTREMELY PERSUASIVE and CONVINCING in your approach.
        
        Current conversation stage: {state_obj.stage.value}
        Current loan application status: {state_obj.decision.value}
        
        Conversation context: {json.dumps(context, indent=2)}
        
        Recent conversation history:
        {conversation_history}
        
        Latest user message: "{latest_user_message}"
        
        {customer_greeting}, {loan_summary}
        
        {customer_profile}
        
        Guidelines based on conversation stage:
        - GREETING: Warmly welcome the customer, introduce yourself as Tata Capital's AI assistant. Use persuasive language to build trust immediately. Ask specific questions about their loan needs and emphasize how Tata Capital can provide the perfect solution. Start collecting basic personal information like full name and contact details.
        
        - INTENT_CAPTURE: Ask targeted questions about their loan requirements (exact amount, specific purpose, preferred tenure). Also begin collecting comprehensive personal information including date of birth, marital status, number of dependents, and nationality. Highlight Tata Capital's industry-leading rates, lightning-fast approval process, and exceptional customer satisfaction. Use phrases like "You're making an excellent choice" and "We're committed to finding your perfect loan solution."
        
        - SALES_EXPLORATION: Present tailored loan options with specific numbers and terms. Collect employment details including employment type (salaried/self-employed), company name, job designation, years of experience, and income details. Use persuasive comparisons to show why our options are superior. Emphasize unique benefits like flexible repayment options, minimal documentation requirements, and exclusive offers available only to them. Create urgency with limited-time offers when appropriate.
        
        - VERIFICATION: Request PAN number, Aadhaar number, and address details (permanent and current). Ask about existing loans and EMIs, monthly financial obligations, and credit score if known. Request necessary information while explaining how this significantly speeds up their application. Assure them about our bank-grade security protocols and how their information helps us tailor the perfect loan for them. Use phrases like "This information helps us fast-track your approval" and "We're just a few steps away from your loan approval."
        
        - UNDERWRITING: Explain our thorough yet efficient assessment process. Collect information about document availability including salary slips, Form 16/ITR, bank statements, GST certificate, trade license, profit & loss statements, and balance sheets based on their employment type. If more documents are needed, explain specifically how each document improves their chances of approval and helps us offer better terms. Emphasize how close they are to approval.
        
        - DOCUMENTATION: Guide them through document submission with clear, step-by-step instructions. Request photographs and signature if not already provided. Create excitement by mentioning how close they are to receiving their funds. Use phrases like "You're at the final stage of your loan journey" and "Your loan funds will soon be on their way to you."
        
        - CLOSURE: If approved, express genuine enthusiasm and congratulate them warmly. Provide clear next steps for fund disbursement. If rejected, be empathetic and immediately offer specific alternatives or future options with clear improvement steps.
        
        IMPORTANT PERSUASIVE TECHNIQUES TO USE:
        1. Use the customer's name frequently
        2. Mention specific numbers, rates, and terms (not generic statements)
        3. Create a sense of exclusivity ("specially selected offers for you")
        4. Emphasize benefits over features (how the loan will improve their life)
        5. Use social proof ("many customers like you have benefited from...")
        6. Create appropriate urgency without being pushy
        7. Address objections before they arise
        8. Use positive, confident language throughout
        9. Show genuine understanding of their specific needs
        10. Always provide a clear next step or call to action
        
        INFORMATION COLLECTION PRIORITY:
        Based on the current conversation stage and missing customer information, prioritize asking for:
        
        - If basic personal info is missing (name, DOB, contact details): Ask for these first in a friendly, conversational way
        - If employment details are missing: Explain how this helps us find the best loan options for them
        - If financial information is missing: Emphasize how this helps us offer better rates and terms
        - If document availability is unclear: Ask about specific documents relevant to their employment type
        - If loan details are incomplete: Focus on getting exact amounts, tenure, and purpose
        
        Always explain WHY each piece of information is important and how it benefits the customer in getting better loan terms.
        
        Your response must be conversational, engaging, and highly persuasive. Avoid generic responses at all costs. Every response should feel tailored specifically to this customer and their unique situation.
        
        IMPORTANT: Log all processes clearly in your response so they can be seen in the terminal.
        """
        
        try:
            # Call Gemini API
            model = genai.GenerativeModel(self.gemini_model)
            print(f"Sending prompt to Gemini API for response generation...")
            response = self.generate_content_with_retry(model, prompt)
            
            # Extract the response text
            response_text = response.text
            print(f"Received response from Gemini API. Length: {len(response_text)} characters")
            
            # Add response to state
            state_obj.add_message("assistant", response_text)
            
            # Add to Gemini history
            state_obj.gemini_history.append({
                "prompt": prompt,
                "response": response_text,
                "timestamp": datetime.now().isoformat()
            })
            
            # Log the response generation
            print(f"Generated response at stage: {state_obj.stage.value}")
            print(f"Customer: {state_obj.customer_name or 'Unknown'}")
            print(f"Loan details: {state_obj.loan_details}")
            
        except Exception as e:
            state_obj.add_error("API", f"Gemini API error: {str(e)}")
            # Add a more informative fallback response
            fallback_response = f"I apologize for the delay in processing your request. We're experiencing a temporary issue with our system. Please try again or provide more details about your loan requirements so I can assist you better. Our team is working to resolve this issue as quickly as possible."
            state_obj.add_message("assistant", fallback_response)
            print(f"Gemini API error in _generate_response: {str(e)}")
            print(f"Error details: {traceback.format_exc()}")
            
            # ✅ Fallback for any exceptions to ensure valid dict return
            return {
                "response": fallback_response,
                "next_agent": "determine_next_step",
                "state": state_obj.to_dict()
            }
        
        # Get the response text from the last assistant message
        response_text = ""
        if state_obj.messages and state_obj.messages[-1]["role"] == "assistant":
            response_text = state_obj.messages[-1]["content"]
        
        # Set next_agent to end to break the recursion
        if state_obj.stage != ConversationStage.CLOSURE:
            next_agent = "determine_next_step"
        else:
            next_agent = "end"
        
        # ✅ Ensures valid dict return for LangGraph compatibility
        return {
            "response": response_text,
            "state": state_obj.to_dict(),
            "next_agent": next_agent
        }
    
    def process_message(self, user_message: str) -> dict:
        """Process a user message through the LangGraph pipeline and return a structured response."""
        print("\n" + "-" * 50)
        print(f"Processing user message: '{user_message}'")

        # 1️⃣ Add user message to conversation history
        self.state.add_message("user", user_message)
        print(f"Added user message to conversation history. Total messages: {len(self.state.messages)}")

        # 2️⃣ Log current state snapshot
        print(f"Current conversation stage: {self.state.stage.value}")
        print(f"Customer details: {self.state.customer_name or 'Unknown'} | Loan amount: {self.state.loan_details.get('amount', 'None')}")
        print("Invoking LangGraph to process message...")

        start_time = datetime.now()
        result = None

        try:
            # 3️⃣ Invoke the LangGraph workflow with node output validation
            def validate_node_output(node_name, node_output):
                print(f"Node '{node_name}' produced output: {type(node_output)}")
                
                if node_output is None:
                    raise ValueError(f"Node '{node_name}' returned None instead of a valid dict")
                    
                if not isinstance(node_output, dict):
                    raise ValueError(f"Node '{node_name}' returned {type(node_output)} instead of a dict")
                    
                # Check for required keys
                required_keys = ["response", "next_agent", "state"]
                missing_keys = [key for key in required_keys if key not in node_output]
                
                if missing_keys:
                    raise ValueError(f"Node '{node_name}' missing required keys: {missing_keys}")
                    
                return node_output
            
            # Configure the graph to use our validator
            for node_name in self.graph.nodes:
                self.graph.add_node(node_name, validate_node_output)
                
            # Invoke the workflow
            result = self.graph.invoke({"message": user_message})

            # 4️⃣ Validate and sanitize graph output
            if not result or not isinstance(result, dict):
                print(f"⚠️ Warning: Invalid LangGraph output: {type(result)}. Creating default response.")
                result = {
                    "response": "I'm sorry, something went wrong while processing your request. Could you please rephrase?",
                    "stage": self.state.stage.value,
                    "decision": self.state.decision.value,
                    "state": self.state.to_dict()
                }

            # 5️⃣ Ensure essential fields exist
            result.setdefault("response", "No valid response generated.")
            result.setdefault("stage", self.state.stage.value)
            result.setdefault("decision", self.state.decision.value)
            result.setdefault("state", self.state.to_dict())

            # 6️⃣ Rebuild internal state if graph returned an updated one
            if isinstance(result.get("state"), dict):
                try:
                    self.state = ConversationState.from_dict(result["state"])
                except Exception as state_err:
                    print(f"⚠️ Warning: Could not rebuild state from graph result: {state_err}")

            # 7️⃣ Extract final text response
            response_text = str(result.get("response", "Sorry, I didn’t catch that."))

            # 8️⃣ Prevent endless loops in LangGraph
            if self.state.recursion_depth > 25:
                print("⚠️ Recursion limit reached. Resetting stage to 'greeting'.")
                self.state.stage = ConversationStage.GREETING
                self.state.next_agent = "generate_response"

        # 9️⃣ Add assistant response to conversation log
            self.state.add_message("assistant", response_text)

            processing_time = (datetime.now() - start_time).total_seconds()
            print(f"Message processed successfully in {processing_time:.2f}s")

            # 🔟 Log the updated conversation state
            print(f"Updated conversation stage: {self.state.stage.value}")
            print(f"Next agent: {self.state.next_agent or 'generate_response'}")

            # ✅ Always return a dict for the API to consume with consistent structure
            return {
                "response": response_text,
                "stage": self.state.stage.value,
                "decision": self.state.decision.value,
                "next_agent": self.state.next_agent or "generate_response",
                "state": self.state.to_dict()
            }

        except Exception as e:
            # ️🧯 Detailed exception handling
            print(f"❌ Error in LangGraph processing: {e}")
            print("For troubleshooting, visit: https://python.langchain.com/docs/troubleshooting/errors/INVALID_GRAPH_NODE_RETURN_VALUE")

            # Add to error history for visibility
            self.state.errors.append({
                "type": "GraphExecutionError",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })

        # ✅ Always return a meaningful response with consistent structure
            return {
                "response": "Apologies, I encountered an internal issue while processing your request.",
                "stage": self.state.stage.value,
                "decision": "error",
                "next_agent": "generate_response",
                "state": self.state.to_dict()
            }

        finally:
            print("-" * 50 + "\n")

def start_conversation(self) -> str:
        """Start a new conversation"""
        print("\n" + "*"*50)
        print("STARTING NEW CONVERSATION")
        print("*"*50)
        
        # Reset conversation state
        self.state = ConversationState()
        print("Conversation state reset")
        
        # Initialize conversation with empty message
        print("Initializing conversation flow...")
        response = self.process_message("Hello")
        
        print("Conversation started successfully")
        print("*"*50 + "\n")
        
        return response

# Example usage
if __name__ == "__main__":
    # This would be integrated with a web interface in a real application
    master_agent = MasterAgent()
    
    # Start conversation
    response = master_agent.start_conversation()
    print("Assistant:", response)
    
    # Simulate user interaction
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            break
        
        response = master_agent.process_message(user_input)
        print("Assistant:", response)