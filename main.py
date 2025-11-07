# Main entry point for Tata Capital Digital Loan Sales Assistant

import os
import sys
import json
import logging
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
print(f"Loaded API key from .env: {os.environ.get('GEMINI_API_KEY', 'Not found')[:5]}...")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('output', 'app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('tata_capital_assistant')

# Add implementation directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'implementation'))

# Import all components
from implementation.master_agent import MasterAgent, ConversationState, ConversationStage, Decision
from implementation.sales_agent import SalesAgent
from implementation.verification_agent import VerificationAgent
from implementation.underwriting_agent import UnderwritingAgent
from implementation.sanction_letter_generator import SanctionLetterGenerator
from implementation.mock_apis import CRMApi, OfferMartApi, CreditBureauApi, DocumentStorage

def run_interactive_chat():
    """Run an interactive chat with the Tata Capital Digital Loan Sales Assistant"""
    print("\n" + "="*80)
    print("Tata Capital Digital Loan Sales Assistant")
    print("="*80)
    
    # Get Gemini API key from environment variable
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    
    # Initialize the Master Agent with Gemini API
    master_agent = MasterAgent(gemini_api_key=gemini_api_key)
    
    # Print welcome message
    print("Tata Capital Assistant: Welcome to Tata Capital! How can I help you with your loan needs today?")
    
    # Add initial message to conversation state
    if isinstance(master_agent.state, dict):
        # If state is a dictionary, we need to initialize messages list
        if "messages" not in master_agent.state:
            master_agent.state["messages"] = []
        master_agent.state["messages"].append({"role": "assistant", "content": "Welcome to Tata Capital! How can I help you with your loan needs today?"})
    else:
        # If state is an object, use the method
        master_agent.state.add_message("assistant", "Welcome to Tata Capital! How can I help you with your loan needs today?")
    
    # Main chat loop
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check for exit command
        if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
            print("\nTata Capital Assistant: Thank you for using Tata Capital Smart Assistant. Your session summary and sanction letter (if approved) are saved in /output.")
            
            # Save conversation log
            save_conversation_log(master_agent.state)
            break
        
        # Check for document upload command
        if user_input.lower().startswith("upload "):
            # Extract document type and path
            parts = user_input[7:].split(" as ")
            if len(parts) == 2:
                document_path = parts[0].strip()
                document_type = parts[1].strip()
                
                print(f"\n[System: Processing {document_type} upload: {document_path}]")
                
                # Process the document
                result = master_agent.process_document(document_path, document_type)
                
                if result["status"] == "processed":
                    print(f"[System: {document_type} uploaded successfully]")
                    
                    # Add system message to conversation
                    if isinstance(master_agent.state, dict):
                        if "messages" not in master_agent.state:
                            master_agent.state["messages"] = []
                        master_agent.state["messages"].append({"role": "system", "content": f"Uploaded {document_type}: {document_path}"})
                    else:
                        master_agent.state.add_message("system", f"Uploaded {document_type}: {document_path}")
                    
                    # If this is a salary slip, extract salary information
                    if document_type.lower() == "salary slip" and "extraction_result" in result:
                        extraction = result["extraction_result"]
                        if "extracted_data" in extraction and "monthly_salary" in extraction["extracted_data"]:
                            salary = extraction["extracted_data"]["monthly_salary"]
                            print(f"[System: Extracted monthly salary: {salary}]")
                else:
                    print(f"[System: Error processing {document_type}: {result.get('error', 'Unknown error')}]")
                
                continue
        
        # Add user message to conversation state
        if isinstance(master_agent.state, dict):
            if "messages" not in master_agent.state:
                master_agent.state["messages"] = []
            master_agent.state["messages"].append({"role": "user", "content": user_input})
        else:
            master_agent.state.add_message("user", user_input)
        
        # Process user input using the process_message method which properly handles state
        result = master_agent.process_message(user_input)
        
        # Extract the response from the result
        if result and isinstance(result, dict):
            response_text = result.get("response", "Sorry, I didn't catch that.")
            
            # Print the assistant response
            print(f"\nTata Capital Assistant: {response_text}")
            
            # Check if a sanction letter was generated
            if hasattr(master_agent.state, 'sanction_letter_id') and master_agent.state.sanction_letter_id:
                print(f"\n[System: Sanction letter generated: output/sanction_letter_{master_agent.state.sanction_letter_id}.pdf]")
            elif isinstance(master_agent.state, dict) and master_agent.state.get("sanction_letter_id"):
                print(f"\n[System: Sanction letter generated: output/sanction_letter_{master_agent.state['sanction_letter_id']}.pdf]")
        
        # Log the current state
        if isinstance(master_agent.state, dict):
            logger.info(f"Conversation stage: {master_agent.state.get('stage', 'unknown')}, Decision: {master_agent.state.get('decision', 'pending')}")
        else:
            logger.info(f"Conversation stage: {master_agent.state.stage.value}, Decision: {master_agent.state.decision.value}")

def save_conversation_log(state: Dict[str, Any]):
    """Save the conversation log to a file"""
    log_file = os.path.join('output', f"conversation_{state['session_id']}.json")
    
    with open(log_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"\n[System: Conversation log saved to {log_file}]")
    
    # If a decision was made, log it
    if state['decision'] != Decision.PENDING.value:
        decision_log = os.path.join('output', f"decision_{state['session_id']}.txt")
        
        with open(decision_log, 'w') as f:
            f.write(f"Decision: {state['decision']}\n")
            f.write(f"Loan amount: {state['loan_details']['amount']}\n")
            f.write(f"Loan tenure: {state['loan_details']['tenure']}\n")
            f.write(f"Interest rate: {state['loan_details']['interest_rate']}\n")
            f.write(f"EMI: {state['loan_details']['emi']}\n")
            f.write(f"Processing fee: {state['loan_details']['processing_fee']}\n")
            
            if state['decision'] == Decision.APPROVED.value and state['sanction_letter_id']:
                f.write(f"Sanction letter: output/sanction_letter_{state['sanction_letter_id']}.pdf\n")
        
        print(f"[System: Decision log saved to {decision_log}]")

def main():
    """Main entry point for the Tata Capital Digital Loan Sales Assistant"""
    # Load environment variables from .env file if it exists
    if os.path.exists(".env"):
        load_dotenv()
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join("output", "loan_assistant.log")),
            logging.StreamHandler()
        ]
    )
    
    # Run the interactive chat
    run_interactive_chat()

if __name__ == "__main__":
    main()