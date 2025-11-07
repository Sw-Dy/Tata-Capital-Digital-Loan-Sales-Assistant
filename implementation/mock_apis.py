# Mock APIs for Tata Capital Digital Loan Sales Assistant

import json
import os
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

# Import mock data
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mock_data import customers, loan_products, generate_personalized_offers, get_customer_details, get_credit_score, extract_salary_info

# Base API class with simulated network behavior
class BaseApi:
    def __init__(self, failure_rate=0.05, timeout_rate=0.05, max_retries=3):
        self.failure_rate = failure_rate  # 5% chance of API failure
        self.timeout_rate = timeout_rate  # 5% chance of timeout
        self.max_retries = max_retries
    
    def _simulate_network_issues(self):
        """Simulate network issues like timeouts and failures"""
        # Simulate random delay (10-500ms)
        time.sleep(random.uniform(0.01, 0.5))
        
        # Simulate timeout
        if random.random() < self.timeout_rate:
            time.sleep(random.uniform(2, 5))
            raise TimeoutError("API request timed out")
        
        # Simulate failure
        if random.random() < self.failure_rate:
            raise ConnectionError("API request failed")
    
    def call_with_retry(self, func, *args, **kwargs):
        """Call an API function with retry logic"""
        retries = 0
        while retries < self.max_retries:
            try:
                self._simulate_network_issues()
                return func(*args, **kwargs)
            except (TimeoutError, ConnectionError) as e:
                retries += 1
                if retries >= self.max_retries:
                    raise e
                # Exponential backoff
                time.sleep(0.5 * (2 ** retries))

# CRM API for customer information
class CRMApi(BaseApi):
    def __init__(self, failure_rate=0.05, timeout_rate=0.05, max_retries=3):
        super().__init__(failure_rate, timeout_rate, max_retries)
    
    def get_customer_by_id(self, customer_id: str) -> Dict:
        """Get customer details by ID"""
        return self.call_with_retry(self._get_customer_by_id, customer_id)
    
    def _get_customer_by_id(self, customer_id: str) -> Dict:
        """Internal implementation to get customer details"""
        return get_customer_details(customer_id)
    
    def get_customer_by_phone(self, phone: str) -> Dict:
        """Get customer details by phone number"""
        return self.call_with_retry(self._get_customer_by_phone, phone)
    
    def _get_customer_by_phone(self, phone: str) -> Dict:
        """Internal implementation to get customer by phone"""
        customer = next((c for c in customers if c["phone"] == phone), None)
        if customer:
            return get_customer_details(customer["customer_id"])
        return {"error": "Customer not found"}
    
    def verify_customer_details(self, customer_id: str, details: Dict) -> Dict:
        """Verify customer details against CRM records"""
        return self.call_with_retry(self._verify_customer_details, customer_id, details)
    
    def _verify_customer_details(self, customer_id: str, details: Dict) -> Dict:
        """Internal implementation to verify customer details"""
        crm_details = get_customer_details(customer_id)
        if "error" in crm_details:
            return crm_details
        
        verification_result = {
            "verified": True,
            "mismatches": []
        }
        
        # Check each provided detail against CRM records
        for key, value in details.items():
            if key in crm_details and crm_details[key] != value:
                verification_result["verified"] = False
                verification_result["mismatches"].append({
                    "field": key,
                    "provided": value,
                    "actual": crm_details[key]
                })
        
        return verification_result

# Offer Mart API for loan products and offers
class OfferMartApi(BaseApi):
    def __init__(self, failure_rate=0.05, timeout_rate=0.05, max_retries=3):
        super().__init__(failure_rate, timeout_rate, max_retries)
    
    def get_loan_products(self) -> List[Dict]:
        """Get all available loan products"""
        return self.call_with_retry(self._get_loan_products)
    
    def _get_loan_products(self) -> List[Dict]:
        """Internal implementation to get loan products"""
        return loan_products
    
    def get_personalized_offers(self, customer_id: str, loan_amount: Optional[float] = None, 
                               loan_tenure: Optional[int] = None) -> Dict:
        """Get personalized offers for a customer"""
        return self.call_with_retry(self._get_personalized_offers, customer_id, loan_amount, loan_tenure)
    
    def _get_personalized_offers(self, customer_id: str, loan_amount: Optional[float] = None, 
                                loan_tenure: Optional[int] = None) -> Dict:
        """Internal implementation to get personalized offers"""
        return generate_personalized_offers(customer_id, loan_amount, loan_tenure)
    
    def calculate_emi(self, loan_amount: float, tenure: int, interest_rate: float) -> Dict:
        """Calculate EMI for given loan parameters"""
        return self.call_with_retry(self._calculate_emi, loan_amount, tenure, interest_rate)
    
    def _calculate_emi(self, loan_amount: float, tenure: int, interest_rate: float) -> Dict:
        """Internal implementation to calculate EMI"""
        monthly_rate = interest_rate / (12 * 100)
        emi = (loan_amount * monthly_rate * (1 + monthly_rate) ** tenure) / \
              ((1 + monthly_rate) ** tenure - 1)
        
        total_payment = emi * tenure
        total_interest = total_payment - loan_amount
        
        return {
            "loan_amount": loan_amount,
            "tenure": tenure,
            "interest_rate": interest_rate,
            "monthly_emi": round(emi, 2),
            "total_interest": round(total_interest, 2),
            "total_payment": round(total_payment, 2)
        }

# Credit Bureau API for credit scores and history
class CreditBureauApi(BaseApi):
    def __init__(self, failure_rate=0.05, timeout_rate=0.05, max_retries=3):
        super().__init__(failure_rate, timeout_rate, max_retries)
    
    def get_credit_score(self, customer_id: str) -> Dict:
        """Get credit score and history for a customer"""
        return self.call_with_retry(self._get_credit_score, customer_id)
    
    def _get_credit_score(self, customer_id: str) -> Dict:
        """Internal implementation to get credit score"""
        return get_credit_score(customer_id)
    
    def get_credit_score_by_pan(self, pan: str) -> Dict:
        """Get credit score using PAN number"""
        return self.call_with_retry(self._get_credit_score_by_pan, pan)
    
    def _get_credit_score_by_pan(self, pan: str) -> Dict:
        """Internal implementation to get credit score by PAN"""
        # In a real system, this would look up by PAN
        # For mock purposes, we'll just return a random customer's credit score
        customer = random.choice(customers)
        return get_credit_score(customer["customer_id"])
    
    def calculate_eligibility(self, customer_id: str, loan_amount: float, 
                             tenure: int, monthly_income: float) -> Dict:
        """Calculate loan eligibility based on credit score and income"""
        return self.call_with_retry(self._calculate_eligibility, customer_id, 
                                  loan_amount, tenure, monthly_income)
    
    def _calculate_eligibility(self, customer_id: str, loan_amount: float, 
                              tenure: int, monthly_income: float) -> Dict:
        """Internal implementation to calculate eligibility"""
        credit_info = get_credit_score(customer_id)
        if "error" in credit_info:
            return credit_info
        
        # Get customer details
        customer = next((c for c in customers if c["customer_id"] == customer_id), None)
        if not customer:
            return {"error": "Customer not found"}
        
        # Calculate EMI for requested loan
        # Assume 11% interest rate for calculation
        monthly_rate = 11 / (12 * 100)
        emi = (loan_amount * monthly_rate * (1 + monthly_rate) ** tenure) / \
              ((1 + monthly_rate) ** tenure - 1)
        
        # Calculate existing EMI obligations
        existing_emi = credit_info.get("monthly_obligations", 0)
        
        # Calculate total EMI-to-Income ratio
        total_emi = existing_emi + emi
        emi_to_income_ratio = total_emi / monthly_income
        
        # Determine eligibility
        is_eligible = True
        reason = ""
        
        # Check if amount is within pre-approved limit
        if loan_amount <= customer["pre_approved_limit"]:
            decision = "APPROVED"
            reason = "Amount within pre-approved limit"
        elif loan_amount <= 2 * customer["pre_approved_limit"]:
            # Check EMI-to-Income ratio
            if emi_to_income_ratio <= 0.5:
                decision = "APPROVED"
                reason = "EMI-to-Income ratio within acceptable limit"
            else:
                decision = "REJECTED"
                reason = "EMI-to-Income ratio exceeds 50%"
                is_eligible = False
        else:
            # Check credit score and EMI-to-Income ratio
            if credit_info["score"] >= 700 and emi_to_income_ratio <= 0.5:
                decision = "APPROVED"
                reason = "Good credit score and acceptable EMI-to-Income ratio"
            else:
                decision = "REJECTED"
                if credit_info["score"] < 700:
                    reason = "Credit score below threshold"
                else:
                    reason = "EMI-to-Income ratio exceeds 50%"
                is_eligible = False
        
        return {
            "customer_id": customer_id,
            "loan_amount": loan_amount,
            "tenure": tenure,
            "monthly_income": monthly_income,
            "credit_score": credit_info["score"],
            "existing_emi": existing_emi,
            "new_emi": round(emi, 2),
            "total_emi": round(total_emi, 2),
            "emi_to_income_ratio": round(emi_to_income_ratio, 2),
            "is_eligible": is_eligible,
            "decision": decision,
            "reason": reason
        }

# Document Storage for salary slips and sanction letters
class DocumentStorage(BaseApi):
    def __init__(self, failure_rate=0.05, timeout_rate=0.05, max_retries=3):
        super().__init__(failure_rate, timeout_rate, max_retries)
        self.documents = {}  # In-memory document storage
    
    def upload_document(self, document_type: str, customer_id: str, 
                       file_content: bytes, file_name: str) -> Dict:
        """Upload a document to storage"""
        return self.call_with_retry(self._upload_document, document_type, 
                                  customer_id, file_content, file_name)
    
    def _upload_document(self, document_type: str, customer_id: str, 
                        file_content: bytes, file_name: str) -> Dict:
        """Internal implementation to upload document"""
        document_id = f"{document_type}_{customer_id}_{int(time.time())}"
        
        # In a real system, this would save the file to disk or cloud storage
        # For mock purposes, we'll just store a reference
        self.documents[document_id] = {
            "document_id": document_id,
            "document_type": document_type,
            "customer_id": customer_id,
            "file_name": file_name,
            "upload_time": datetime.now().isoformat(),
            "size": len(file_content) if file_content else 0,
            "content_hash": hash(file_content) if file_content else None
        }
        
        return {
            "document_id": document_id,
            "status": "success",
            "url": f"https://storage.tatacapital.com/documents/{document_id}"
        }
    
    def get_document(self, document_id: str) -> Dict:
        """Get document metadata by ID"""
        return self.call_with_retry(self._get_document, document_id)
    
    def _get_document(self, document_id: str) -> Dict:
        """Internal implementation to get document"""
        if document_id in self.documents:
            return self.documents[document_id]
        return {"error": "Document not found"}
    
    def process_salary_slip(self, document_id: str) -> Dict:
        """Process a salary slip document and extract information"""
        return self.call_with_retry(self._process_salary_slip, document_id)
    
    def _process_salary_slip(self, document_id: str) -> Dict:
        """Internal implementation to process salary slip"""
        document = self._get_document(document_id)
        if "error" in document:
            return document
        
        if document["document_type"] != "salary_slip":
            return {"error": "Document is not a salary slip"}
        
        # Extract salary information
        # In a real system, this would use OCR and ML
        # For mock purposes, we'll use our mock function
        return extract_salary_info(document["file_name"])
    
    def generate_sanction_letter(self, customer_id: str, loan_details: Dict) -> Dict:
        """Generate a sanction letter for an approved loan"""
        return self.call_with_retry(self._generate_sanction_letter, customer_id, loan_details)
    
    def _generate_sanction_letter(self, customer_id: str, loan_details: Dict) -> Dict:
        """Internal implementation to generate sanction letter"""
        # Get customer details
        customer = next((c for c in customers if c["customer_id"] == customer_id), None)
        if not customer:
            return {"error": "Customer not found"}
        
        # Generate a unique document ID
        document_id = f"SL-{customer_id}-{int(time.time())}"
        
        # In a real system, this would generate a PDF
        # For mock purposes, we'll just store metadata
        sanction_letter = {
            "document_id": document_id,
            "document_type": "sanction_letter",
            "customer_id": customer_id,
            "customer_name": customer["name"],
            "loan_amount": loan_details.get("amount"),
            "tenure": loan_details.get("tenure"),
            "interest_rate": loan_details.get("interest_rate"),
            "emi": loan_details.get("emi"),
            "processing_fee": loan_details.get("processing_fee"),
            "disbursal_account": customer.get("account_number"),
            "generation_date": datetime.now().isoformat(),
            "validity": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        # Store the sanction letter
        self.documents[document_id] = sanction_letter
        
        return {
            "document_id": document_id,
            "status": "success",
            "url": f"https://storage.tatacapital.com/documents/{document_id}"
        }

# Example usage
if __name__ == "__main__":
    # Test the APIs
    crm_api = CRMApi()
    offer_mart_api = OfferMartApi()
    credit_bureau_api = CreditBureauApi()
    document_storage = DocumentStorage()
    
    # Test CRM API
    print("\nTesting CRM API:")
    customer = crm_api.get_customer_by_id("TC001")
    print(f"Customer: {customer['name']}")
    
    # Test Offer Mart API
    print("\nTesting Offer Mart API:")
    offers = offer_mart_api.get_personalized_offers("TC001", 500000, 36)
    print(f"Number of offers: {len(offers['offers'])}")
    if offers['offers']:
        print(f"First offer: {offers['offers'][0]['product_name']}")
        print(f"Interest rate: {offers['offers'][0]['interest_rate']}%")
        print(f"EMI: ₹{offers['offers'][0]['monthly_emi']}")
    
    # Test Credit Bureau API
    print("\nTesting Credit Bureau API:")
    credit_info = credit_bureau_api.get_credit_score("TC001")
    print(f"Credit score: {credit_info['score']} ({credit_info['score_band']})")
    
    # Test eligibility calculation
    eligibility = credit_bureau_api.calculate_eligibility("TC001", 500000, 36, 85000)
    print(f"Eligibility: {eligibility['decision']} - {eligibility['reason']}")
    
    # Test Document Storage
    print("\nTesting Document Storage:")
    # Upload a mock salary slip
    upload_result = document_storage.upload_document(
        "salary_slip", "TC001", b"Mock salary slip content", "salary_slip_TC001.pdf"
    )
    print(f"Upload result: {upload_result['status']}")
    print(f"Document ID: {upload_result['document_id']}")
    
    # Process the salary slip
    salary_info = document_storage.process_salary_slip(upload_result['document_id'])
    print(f"Extracted salary: ₹{salary_info['monthly_salary']}")
    
    # Generate a sanction letter
    sanction_result = document_storage.generate_sanction_letter(
        "TC001", {
            "amount": 500000,
            "tenure": 36,
            "interest_rate": 10.5,
            "emi": 16200,
            "processing_fee": 5000
        }
    )
    print(f"Sanction letter ID: {sanction_result['document_id']}")
    print(f"Sanction letter URL: {sanction_result['url']}")