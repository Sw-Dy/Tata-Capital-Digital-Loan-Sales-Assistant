# Mock Data for Tata Capital Digital Loan Sales Assistant

import json
import random
from datetime import datetime, timedelta

# ===============================
# Customer Data
# ===============================

customers = [
    {
        "customer_id": "TC001",
        "name": "Rajesh Kumar",
        "age": 32,
        "city": "Mumbai",
        "phone": "+919876543210",
        "email": "rajesh.kumar@example.com",
        "address": "Flat 301, Sunshine Apartments, Andheri West, Mumbai - 400053",
        "occupation": "Software Engineer",
        "employer": "TCS",
        "monthly_income": 85000,
        "existing_loans": [
            {
                "type": "Home Loan",
                "outstanding": 2500000,
                "emi": 25000,
                "tenure_remaining": 120
            }
        ],
        "account_number": "TATACAP12345",
        "credit_score": 780,
        "pre_approved_limit": 500000
    },
    {
        "customer_id": "TC002",
        "name": "Priya Sharma",
        "age": 28,
        "city": "Delhi",
        "phone": "+919876543211",
        "email": "priya.sharma@example.com",
        "address": "House No. 45, Block C, Greater Kailash, New Delhi - 110048",
        "occupation": "Marketing Manager",
        "employer": "Reliance Retail",
        "monthly_income": 70000,
        "existing_loans": [],
        "account_number": "TATACAP12346",
        "credit_score": 820,
        "pre_approved_limit": 600000
    },
    {
        "customer_id": "TC003",
        "name": "Amit Patel",
        "age": 35,
        "city": "Ahmedabad",
        "phone": "+919876543212",
        "email": "amit.patel@example.com",
        "address": "42, Satellite Road, Ahmedabad - 380015",
        "occupation": "Business Owner",
        "employer": "Self Employed",
        "monthly_income": 120000,
        "existing_loans": [
            {
                "type": "Business Loan",
                "outstanding": 1000000,
                "emi": 32000,
                "tenure_remaining": 36
            },
            {
                "type": "Car Loan",
                "outstanding": 500000,
                "emi": 12000,
                "tenure_remaining": 48
            }
        ],
        "account_number": "TATACAP12347",
        "credit_score": 750,
        "pre_approved_limit": 800000
    },
    {
        "customer_id": "TC004",
        "name": "Sunita Reddy",
        "age": 42,
        "city": "Hyderabad",
        "phone": "+919876543213",
        "email": "sunita.reddy@example.com",
        "address": "Plot 78, Jubilee Hills, Hyderabad - 500033",
        "occupation": "Doctor",
        "employer": "Apollo Hospitals",
        "monthly_income": 150000,
        "existing_loans": [
            {
                "type": "Home Loan",
                "outstanding": 3500000,
                "emi": 42000,
                "tenure_remaining": 180
            }
        ],
        "account_number": "TATACAP12348",
        "credit_score": 850,
        "pre_approved_limit": 1200000
    },
    {
        "customer_id": "TC005",
        "name": "Vikram Singh",
        "age": 30,
        "city": "Bangalore",
        "phone": "+919876543214",
        "email": "vikram.singh@example.com",
        "address": "Flat 205, Tech Park Residency, Whitefield, Bangalore - 560066",
        "occupation": "Product Manager",
        "employer": "Flipkart",
        "monthly_income": 110000,
        "existing_loans": [
            {
                "type": "Personal Loan",
                "outstanding": 300000,
                "emi": 15000,
                "tenure_remaining": 24
            }
        ],
        "account_number": "TATACAP12349",
        "credit_score": 790,
        "pre_approved_limit": 700000
    },
    {
        "customer_id": "TC006",
        "name": "Meera Joshi",
        "age": 26,
        "city": "Pune",
        "phone": "+919876543215",
        "email": "meera.joshi@example.com",
        "address": "33, Koregaon Park, Pune - 411001",
        "occupation": "HR Manager",
        "employer": "Infosys",
        "monthly_income": 65000,
        "existing_loans": [],
        "account_number": "TATACAP12350",
        "credit_score": 760,
        "pre_approved_limit": 400000
    },
    {
        "customer_id": "TC007",
        "name": "Arjun Nair",
        "age": 38,
        "city": "Kochi",
        "phone": "+919876543216",
        "email": "arjun.nair@example.com",
        "address": "Villa 8, Marine Drive, Kochi - 682001",
        "occupation": "Architect",
        "employer": "Design Solutions",
        "monthly_income": 95000,
        "existing_loans": [
            {
                "type": "Car Loan",
                "outstanding": 600000,
                "emi": 18000,
                "tenure_remaining": 36
            }
        ],
        "account_number": "TATACAP12351",
        "credit_score": 800,
        "pre_approved_limit": 750000
    },
    {
        "customer_id": "TC008",
        "name": "Kavita Mehta",
        "age": 33,
        "city": "Jaipur",
        "phone": "+919876543217",
        "email": "kavita.mehta@example.com",
        "address": "45, Civil Lines, Jaipur - 302006",
        "occupation": "Financial Analyst",
        "employer": "HDFC Bank",
        "monthly_income": 80000,
        "existing_loans": [
            {
                "type": "Education Loan",
                "outstanding": 400000,
                "emi": 12000,
                "tenure_remaining": 36
            }
        ],
        "account_number": "TATACAP12352",
        "credit_score": 770,
        "pre_approved_limit": 550000
    },
    {
        "customer_id": "TC009",
        "name": "Rahul Verma",
        "age": 29,
        "city": "Lucknow",
        "phone": "+919876543218",
        "email": "rahul.verma@example.com",
        "address": "78, Gomti Nagar, Lucknow - 226010",
        "occupation": "Government Employee",
        "employer": "UP State Government",
        "monthly_income": 55000,
        "existing_loans": [
            {
                "type": "Two-wheeler Loan",
                "outstanding": 80000,
                "emi": 4000,
                "tenure_remaining": 24
            }
        ],
        "account_number": "TATACAP12353",
        "credit_score": 720,
        "pre_approved_limit": 300000
    },
    {
        "customer_id": "TC010",
        "name": "Neha Kapoor",
        "age": 31,
        "city": "Chandigarh",
        "phone": "+919876543219",
        "email": "neha.kapoor@example.com",
        "address": "House 123, Sector 18, Chandigarh - 160018",
        "occupation": "Professor",
        "employer": "Punjab University",
        "monthly_income": 75000,
        "existing_loans": [],
        "account_number": "TATACAP12354",
        "credit_score": 810,
        "pre_approved_limit": 600000
    }
]

# ===============================
# Offer Mart API Data
# ===============================

loan_products = [
    {
        "product_id": "PL001",
        "name": "Tata Capital Quick Personal Loan",
        "description": "Get instant funds for your personal needs with minimal documentation",
        "min_amount": 100000,
        "max_amount": 1500000,
        "min_tenure": 12,
        "max_tenure": 60,
        "base_interest_rate": 10.5,
        "processing_fee_percent": 1.0,
        "processing_fee_cap": 5000,
        "prepayment_charges": 2.0,
        "late_payment_charges": 2.0,
        "features": [
            "Minimal documentation",
            "Quick approval within 48 hours",
            "No collateral required",
            "Flexible repayment options"
        ],
        "eligibility": {
            "min_age": 23,
            "max_age": 58,
            "min_income": 25000,
            "min_credit_score": 700
        }
    },
    {
        "product_id": "PL002",
        "name": "Tata Capital Premium Personal Loan",
        "description": "Premium loan offering with competitive interest rates and higher limits",
        "min_amount": 300000,
        "max_amount": 2500000,
        "min_tenure": 12,
        "max_tenure": 72,
        "base_interest_rate": 9.5,
        "processing_fee_percent": 0.75,
        "processing_fee_cap": 7500,
        "prepayment_charges": 1.5,
        "late_payment_charges": 2.0,
        "features": [
            "Competitive interest rates",
            "Higher loan amounts",
            "Extended tenure options",
            "Dedicated relationship manager"
        ],
        "eligibility": {
            "min_age": 25,
            "max_age": 60,
            "min_income": 50000,
            "min_credit_score": 750
        }
    },
    {
        "product_id": "PL003",
        "name": "Tata Capital Salary Personal Loan",
        "description": "Special personal loan for salaried employees with partner companies",
        "min_amount": 100000,
        "max_amount": 2000000,
        "min_tenure": 12,
        "max_tenure": 60,
        "base_interest_rate": 10.0,
        "processing_fee_percent": 0.5,
        "processing_fee_cap": 5000,
        "prepayment_charges": 1.0,
        "late_payment_charges": 2.0,
        "features": [
            "Special rates for salaried employees",
            "Simplified documentation",
            "Quick disbursal",
            "Zero foreclosure charges after 12 months"
        ],
        "eligibility": {
            "min_age": 23,
            "max_age": 58,
            "min_income": 30000,
            "min_credit_score": 720,
            "employment_type": "Salaried"
        }
    }
]

# Function to generate personalized offers based on customer profile
def generate_personalized_offers(customer_id, loan_amount=None, loan_tenure=None):
    # Find customer
    customer = next((c for c in customers if c["customer_id"] == customer_id), None)
    if not customer:
        return {"error": "Customer not found"}
    
    # Default values if not provided
    if not loan_amount:
        loan_amount = min(customer["pre_approved_limit"], 500000)
    if not loan_tenure:
        loan_tenure = 36
    
    # Calculate existing EMI obligations
    total_existing_emi = sum(loan["emi"] for loan in customer["existing_loans"])
    
    # Calculate debt-to-income ratio
    dti_ratio = total_existing_emi / customer["monthly_income"]
    
    # Adjust interest rate based on credit score and DTI
    interest_rate_adjustments = {
        "credit_score": 0,
        "dti": 0
    }
    
    # Credit score adjustment
    if customer["credit_score"] >= 800:
        interest_rate_adjustments["credit_score"] = -0.5
    elif customer["credit_score"] >= 750:
        interest_rate_adjustments["credit_score"] = -0.25
    elif customer["credit_score"] < 720:
        interest_rate_adjustments["credit_score"] = 0.5
    
    # DTI adjustment
    if dti_ratio <= 0.2:
        interest_rate_adjustments["dti"] = -0.25
    elif dti_ratio >= 0.4:
        interest_rate_adjustments["dti"] = 0.5
    
    # Generate offers
    personalized_offers = []
    for product in loan_products:
        # Check if customer meets basic eligibility
        if (
            customer["age"] >= product["eligibility"]["min_age"] and
            customer["age"] <= product["eligibility"]["max_age"] and
            customer["monthly_income"] >= product["eligibility"]["min_income"] and
            customer["credit_score"] >= product["eligibility"]["min_credit_score"] and
            loan_amount >= product["min_amount"] and
            loan_amount <= product["max_amount"] and
            loan_tenure >= product["min_tenure"] and
            loan_tenure <= product["max_tenure"]
        ):
            # Calculate personalized interest rate
            interest_rate = product["base_interest_rate"] + \
                           interest_rate_adjustments["credit_score"] + \
                           interest_rate_adjustments["dti"]
            
            # Calculate EMI
            monthly_rate = interest_rate / (12 * 100)
            emi = (loan_amount * monthly_rate * (1 + monthly_rate) ** loan_tenure) / \
                  ((1 + monthly_rate) ** loan_tenure - 1)
            
            # Calculate processing fee
            processing_fee = min(
                loan_amount * (product["processing_fee_percent"] / 100),
                product["processing_fee_cap"]
            )
            
            # Calculate total interest payable
            total_payment = emi * loan_tenure
            total_interest = total_payment - loan_amount
            
            offer = {
                "offer_id": f"OFF-{customer_id}-{product['product_id']}",
                "product_id": product["product_id"],
                "product_name": product["name"],
                "loan_amount": loan_amount,
                "loan_tenure": loan_tenure,
                "interest_rate": round(interest_rate, 2),
                "monthly_emi": round(emi, 2),
                "processing_fee": round(processing_fee, 2),
                "total_interest": round(total_interest, 2),
                "total_payment": round(total_payment, 2),
                "features": product["features"],
                "pre_approved": loan_amount <= customer["pre_approved_limit"]
            }
            
            personalized_offers.append(offer)
    
    return {
        "customer_id": customer_id,
        "offers": personalized_offers
    }

# ===============================
# CRM API Data
# ===============================

# Function to get customer details from CRM
def get_customer_details(customer_id):
    customer = next((c for c in customers if c["customer_id"] == customer_id), None)
    if not customer:
        return {"error": "Customer not found"}
    
    # Return only the fields that would be available in CRM
    return {
        "customer_id": customer["customer_id"],
        "name": customer["name"],
        "age": customer["age"],
        "city": customer["city"],
        "phone": customer["phone"],
        "email": customer["email"],
        "address": customer["address"],
        "occupation": customer["occupation"],
        "employer": customer["employer"],
        "account_number": customer["account_number"],
        "customer_since": (datetime.now() - timedelta(days=random.randint(30, 1825))).strftime("%Y-%m-%d"),
        "kyc_status": "VERIFIED",
        "relationship_manager": f"RM{random.randint(1000, 9999)}"
    }

# ===============================
# Credit Bureau API Data
# ===============================

# Function to get credit score and history
def get_credit_score(customer_id):
    customer = next((c for c in customers if c["customer_id"] == customer_id), None)
    if not customer:
        return {"error": "Customer not found"}
    
    # Generate credit history entries
    credit_history = []
    for i in range(random.randint(3, 8)):
        loan_type = random.choice(["Home Loan", "Personal Loan", "Car Loan", "Credit Card", "Education Loan"])
        status = random.choice(["Active", "Closed", "Active", "Active"])  # More weight to active
        
        if status == "Active":
            payment_status = random.choices(
                ["Regular", "Irregular", "Overdue"],
                weights=[0.8, 0.15, 0.05],
                k=1
            )[0]
        else:
            payment_status = "Completed"
        
        start_date = datetime.now() - timedelta(days=random.randint(365, 2190))
        
        if status == "Closed":
            end_date = start_date + timedelta(days=random.randint(365, 1095))
            end_date_str = end_date.strftime("%Y-%m-%d")
        else:
            end_date_str = None
        
        credit_history.append({
            "loan_type": loan_type,
            "lender": random.choice(["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "Tata Capital"]),
            "account_number": f"LOAN{random.randint(10000, 99999)}",
            "status": status,
            "payment_status": payment_status,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date_str,
            "loan_amount": random.randint(100000, 5000000),
            "outstanding": random.randint(0, 3000000) if status == "Active" else 0
        })
    
    # Add existing loans from customer data
    for loan in customer["existing_loans"]:
        start_date = datetime.now() - timedelta(days=random.randint(365, 730))
        
        credit_history.append({
            "loan_type": loan["type"],
            "lender": random.choice(["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "Tata Capital"]),
            "account_number": f"LOAN{random.randint(10000, 99999)}",
            "status": "Active",
            "payment_status": "Regular",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": None,
            "loan_amount": loan["outstanding"] + (loan["emi"] * (60 - loan["tenure_remaining"])),
            "outstanding": loan["outstanding"]
        })
    
    # Calculate total obligations
    total_outstanding = sum(entry["outstanding"] for entry in credit_history)
    total_emi = sum(loan["emi"] for loan in customer["existing_loans"])
    
    return {
        "customer_id": customer["customer_id"],
        "name": customer["name"],
        "score": customer["credit_score"],
        "score_band": get_score_band(customer["credit_score"]),
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "credit_history": credit_history,
        "total_accounts": len(credit_history),
        "active_accounts": sum(1 for entry in credit_history if entry["status"] == "Active"),
        "total_outstanding": total_outstanding,
        "monthly_obligations": total_emi,
        "pre_approved_limit": customer["pre_approved_limit"],
        "inquiries_last_6_months": random.randint(0, 3)
    }

def get_score_band(score):
    if score >= 800:
        return "Excellent"
    elif score >= 750:
        return "Very Good"
    elif score >= 700:
        return "Good"
    elif score >= 650:
        return "Fair"
    else:
        return "Poor"

# ===============================
# Document Processing Mock
# ===============================

# Function to simulate salary slip processing
def extract_salary_info(salary_slip_url):
    # In a real system, this would use OCR and ML to extract information
    # For mock purposes, we'll generate realistic data
    
    # Extract customer_id from URL (assuming format like "salary_slip_TC001.pdf")
    parts = salary_slip_url.split("_")
    customer_id = parts[-1].split(".")[0] if len(parts) > 1 else None
    
    # Get customer data if available
    customer = next((c for c in customers if c["customer_id"] == customer_id), None)
    
    if customer:
        # Use actual customer data with slight variations
        base_salary = int(customer["monthly_income"] * 0.7)  # Base salary is 70% of total income
        hra = int(customer["monthly_income"] * 0.15)        # HRA is 15% of total income
        allowances = int(customer["monthly_income"] * 0.15)  # Allowances are 15% of total income
        
        # Add some random variation (±5%)
        variation = random.uniform(0.95, 1.05)
        monthly_salary = int(customer["monthly_income"] * variation)
    else:
        # Generate random data
        base_salary = random.randint(30000, 100000)
        hra = int(base_salary * 0.4)
        allowances = int(base_salary * 0.2)
        monthly_salary = base_salary + hra + allowances
    
    # Calculate deductions
    pf = min(int(base_salary * 0.12), 1800)  # PF capped at 1800
    professional_tax = 200
    income_tax = int(monthly_salary * random.uniform(0.05, 0.15))
    total_deductions = pf + professional_tax + income_tax
    
    # Net salary
    net_salary = monthly_salary - total_deductions
    
    return {
        "employee_name": customer["name"] if customer else f"Employee {random.randint(1000, 9999)}",
        "employee_id": f"EMP{random.randint(10000, 99999)}",
        "company_name": customer["employer"] if customer else "ABC Corporation",
        "month": (datetime.now() - timedelta(days=random.randint(0, 60))).strftime("%B %Y"),
        "earnings": {
            "basic": base_salary,
            "hra": hra,
            "allowances": allowances,
            "total": monthly_salary
        },
        "deductions": {
            "pf": pf,
            "professional_tax": professional_tax,
            "income_tax": income_tax,
            "total": total_deductions
        },
        "net_salary": net_salary,
        "monthly_salary": monthly_salary,  # Gross monthly salary
        "annual_salary": monthly_salary * 12,  # Annualized salary
        "confidence_score": 0.95  # Confidence in extraction accuracy
    }

# ===============================
# Helper Functions
# ===============================

# Function to save all mock data to JSON files
def save_mock_data():
    # Save customers
    with open("mock_customers.json", "w") as f:
        json.dump(customers, f, indent=2)
    
    # Save loan products
    with open("mock_loan_products.json", "w") as f:
        json.dump(loan_products, f, indent=2)
    
    # Generate and save sample offers
    sample_offers = {}
    for customer in customers:
        sample_offers[customer["customer_id"]] = generate_personalized_offers(
            customer["customer_id"], 500000, 36
        )
    
    with open("mock_offers.json", "w") as f:
        json.dump(sample_offers, f, indent=2)
    
    # Generate and save sample credit reports
    sample_credit_reports = {}
    for customer in customers:
        sample_credit_reports[customer["customer_id"]] = get_credit_score(customer["customer_id"])
    
    with open("mock_credit_reports.json", "w") as f:
        json.dump(sample_credit_reports, f, indent=2)
    
    # Generate and save sample salary slips
    sample_salary_slips = {}
    for customer in customers:
        sample_salary_slips[customer["customer_id"]] = extract_salary_info(
            f"salary_slip_{customer['customer_id']}.pdf"
        )
    
    with open("mock_salary_slips.json", "w") as f:
        json.dump(sample_salary_slips, f, indent=2)

# If this script is run directly, save the mock data
if __name__ == "__main__":
    save_mock_data()