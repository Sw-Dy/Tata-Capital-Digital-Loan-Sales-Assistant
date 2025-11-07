# Worker Agents Design

## 1. Sales Agent

### 1.1 Overview

The Sales Agent is responsible for engaging with customers to understand their loan requirements, presenting suitable offers, and negotiating terms. This agent combines persuasive communication with product knowledge to guide customers toward appropriate loan products.

### 1.2 Core Responsibilities

- Understand customer needs through questioning
- Retrieve personalized offers from the Offer Mart API
- Present loan options with clear benefits
- Negotiate loan terms (amount, tenure, interest rate)
- Create a structured intent summary for the Master Agent

### 1.3 Implementation

#### 1.3.1 System Prompt

```
You are the Sales Agent for Tata Capital's Digital Loan Sales Assistant. Your role is to engage with customers seeking personal loans, understand their needs, and present suitable loan options. You will:

1. Ask questions to understand the customer's loan requirements (amount, purpose, tenure)
2. Retrieve personalized offers from the Offer Mart API
3. Present loan options with clear benefits and features
4. Negotiate terms to find the best fit for the customer
5. Create a structured summary of the customer's intent

Your communication style should be:
- Friendly and conversational
- Persuasive but not pushy
- Clear about loan features and benefits
- Transparent about terms and conditions

You represent Tata Capital, so maintain a professional tone while building rapport with the customer.
```

#### 1.3.2 Function Definitions

```python
class SalesAgent:
    def __init__(self, offer_mart_api_client):
        self.offer_mart_api = offer_mart_api_client
        self.llm = ChatOpenAI(model="gpt-4")
    
    def process(self, task_input):
        # Extract customer information and conversation context
        customer_id = task_input["customer_profile"].get("customer_id")
        conversation_history = task_input["conversation_context"]["conversation_history"]
        
        # Analyze conversation to determine current sales stage
        sales_stage = self._determine_sales_stage(conversation_history)
        
        # Process based on current stage
        if sales_stage == "NEED_IDENTIFICATION":
            return self._handle_need_identification(task_input)
        elif sales_stage == "OFFER_PRESENTATION":
            return self._handle_offer_presentation(task_input)
        elif sales_stage == "NEGOTIATION":
            return self._handle_negotiation(task_input)
        elif sales_stage == "CONFIRMATION":
            return self._handle_confirmation(task_input)
    
    def _determine_sales_stage(self, conversation_history):
        # Logic to determine current sales stage based on conversation
        # Returns one of: NEED_IDENTIFICATION, OFFER_PRESENTATION, NEGOTIATION, CONFIRMATION
        pass
    
    def _handle_need_identification(self, task_input):
        # Ask questions about loan amount, purpose, and tenure
        pass
    
    def _handle_offer_presentation(self, task_input):
        # Retrieve offers from API and present to customer
        customer_id = task_input["customer_profile"].get("customer_id")
        loan_amount = self._extract_loan_amount(task_input)
        loan_tenure = self._extract_loan_tenure(task_input)
        
        offers = self.offer_mart_api.get_offers(
            customer_id=customer_id,
            loan_amount=loan_amount,
            loan_tenure=loan_tenure
        )
        
        # Format offers for presentation
        return self._format_offer_response(offers, task_input)
    
    def _handle_negotiation(self, task_input):
        # Handle customer questions and negotiate terms
        pass
    
    def _handle_confirmation(self, task_input):
        # Confirm final loan details and create intent summary
        loan_details = self._extract_loan_details(task_input)
        
        # Create structured intent summary
        intent_summary = {
            "loan_amount": loan_details["amount"],
            "loan_tenure": loan_details["tenure"],
            "interest_rate": loan_details["interest_rate"],
            "purpose": loan_details["purpose"],
            "monthly_emi": loan_details["monthly_emi"]
        }
        
        return {
            "customer_response": "Great! I've noted your loan requirements. Let's proceed with verifying your details to check eligibility.",
            "internal_data": intent_summary,
            "next_action": "VERIFICATION"
        }
```

## 2. Verification Agent

### 2.1 Overview

The Verification Agent validates customer identity and KYC details by cross-checking information with the CRM API. It ensures that all required verification steps are completed before proceeding to underwriting.

### 2.2 Core Responsibilities

- Verify phone number, address, and other KYC information
- Cross-check details with CRM API
- Flag inconsistencies or missing information
- Request additional verification if needed
- Provide verification status to Master Agent

### 2.3 Implementation

#### 2.3.1 System Prompt

```
You are the Verification Agent for Tata Capital's Digital Loan Sales Assistant. Your role is to validate customer identity and KYC details. You will:

1. Verify customer information (name, phone, address, etc.)
2. Cross-check details with the CRM API
3. Identify and flag any inconsistencies
4. Request additional verification when needed
5. Provide a clear verification status

Your communication style should be:
- Clear and direct about verification requirements
- Reassuring about data security
- Helpful in resolving verification issues
- Patient when requesting additional information

Remember that verification is a critical compliance step, but try to make the process as smooth as possible for the customer.
```

#### 2.3.2 Function Definitions

```python
class VerificationAgent:
    def __init__(self, crm_api_client):
        self.crm_api = crm_api_client
        self.llm = ChatOpenAI(model="gpt-4")
    
    def process(self, task_input):
        # Extract customer information
        customer_id = task_input["customer_profile"].get("customer_id")
        customer_name = task_input["customer_profile"].get("name")
        customer_phone = task_input["customer_profile"].get("phone")
        customer_address = task_input["customer_profile"].get("address")
        
        # Get customer details from CRM
        crm_details = self.crm_api.get_customer_details(customer_id)
        
        # Verify customer details
        verification_result = self._verify_customer_details(
            provided_details={
                "name": customer_name,
                "phone": customer_phone,
                "address": customer_address
            },
            crm_details=crm_details
        )
        
        if verification_result["verified"]:
            return {
                "customer_response": "Thank you! Your details have been verified successfully. Let's proceed with checking your loan eligibility.",
                "internal_data": verification_result,
                "next_action": "UNDERWRITING"
            }
        else:
            # Handle verification issues
            return self._handle_verification_issues(verification_result, task_input)
    
    def _verify_customer_details(self, provided_details, crm_details):
        # Compare provided details with CRM records
        verification_result = {
            "verified": True,
            "issues": []
        }
        
        # Check name match
        if not self._is_name_match(provided_details["name"], crm_details["name"]):
            verification_result["verified"] = False
            verification_result["issues"].append({
                "field": "name",
                "provided": provided_details["name"],
                "recorded": crm_details["name"]
            })
        
        # Check phone match
        if provided_details["phone"] != crm_details["phone"]:
            verification_result["verified"] = False
            verification_result["issues"].append({
                "field": "phone",
                "provided": provided_details["phone"],
                "recorded": crm_details["phone"]
            })
        
        # Check address match
        if not self._is_address_match(provided_details["address"], crm_details["address"]):
            verification_result["verified"] = False
            verification_result["issues"].append({
                "field": "address",
                "provided": provided_details["address"],
                "recorded": crm_details["address"]
            })
        
        return verification_result
    
    def _is_name_match(self, provided_name, recorded_name):
        # Implement fuzzy name matching logic
        pass
    
    def _is_address_match(self, provided_address, recorded_address):
        # Implement address matching logic
        pass
    
    def _handle_verification_issues(self, verification_result, task_input):
        # Generate appropriate response for verification issues
        issues = verification_result["issues"]
        
        # Use LLM to generate a helpful response
        response = self.llm.generate_verification_issue_response(issues)
        
        return {
            "customer_response": response,
            "internal_data": verification_result,
            "next_action": "VERIFICATION"
        }
```

## 3. Underwriting Agent

### 3.1 Overview

The Underwriting Agent evaluates loan eligibility by applying business rules to customer data, credit scores, and financial information. It makes the final approval decision and calculates loan terms.

### 3.2 Core Responsibilities

- Fetch credit score from Credit Bureau API
- Apply eligibility rules based on pre-approved limits
- Request and analyze salary slips when needed
- Calculate EMI and validate against salary
- Make final approval/rejection decision
- Generate structured decision summary

### 3.3 Implementation

#### 3.3.1 System Prompt

```
You are the Underwriting Agent for Tata Capital's Digital Loan Sales Assistant. Your role is to evaluate loan eligibility and make approval decisions. You will:

1. Analyze customer credit information
2. Apply eligibility rules based on pre-approved limits
3. Request and review salary documentation when needed
4. Calculate EMI and validate against income
5. Make final approval or rejection decisions
6. Generate a structured decision summary

Your decision-making should be:
- Consistent with Tata Capital's risk policies
- Based on objective financial criteria
- Transparent about approval/rejection reasons
- Compliant with regulatory requirements

Remember that your decisions directly impact both the customer and the company's risk exposure.
```

#### 3.3.2 Function Definitions

```python
class UnderwritingAgent:
    def __init__(self, credit_bureau_api_client, document_processor):
        self.credit_bureau_api = credit_bureau_api_client
        self.document_processor = document_processor
        self.llm = ChatOpenAI(model="gpt-4")
    
    def process(self, task_input):
        # Extract customer and loan information
        customer_id = task_input["customer_profile"].get("customer_id")
        loan_amount = task_input["loan_details"]["loan_amount"]
        loan_tenure = task_input["loan_details"]["loan_tenure"]
        
        # Get credit score
        credit_info = self.credit_bureau_api.get_credit_score(customer_id)
        credit_score = credit_info["score"]
        pre_approved_limit = credit_info["pre_approved_limit"]
        
        # Apply eligibility rules
        if loan_amount <= pre_approved_limit:
            # Instant approval for amounts within pre-approved limit
            return self._generate_approval_decision(
                customer_id, loan_amount, loan_tenure, credit_score, pre_approved_limit
            )
        elif loan_amount <= (2 * pre_approved_limit) and credit_score >= 700:
            # Request salary slip for amounts up to twice the pre-approved limit
            if "salary_slip_url" in task_input:
                # Analyze salary slip
                salary_info = self._analyze_salary_slip(task_input["salary_slip_url"])
                monthly_salary = salary_info["monthly_salary"]
                
                # Calculate EMI
                emi = self._calculate_emi(loan_amount, loan_tenure)
                
                # Check if EMI is within 50% of salary
                if emi <= (0.5 * monthly_salary):
                    return self._generate_approval_decision(
                        customer_id, loan_amount, loan_tenure, credit_score, pre_approved_limit,
                        emi=emi, monthly_salary=monthly_salary
                    )
                else:
                    return self._generate_rejection_decision(
                        customer_id, loan_amount, credit_score,
                        reason="EMI_EXCEEDS_LIMIT",
                        emi=emi, monthly_salary=monthly_salary
                    )
            else:
                # Request salary slip
                return {
                    "customer_response": "To proceed with your loan application, we'll need to verify your income. Could you please upload your latest salary slip?",
                    "internal_data": {
                        "status": "PENDING",
                        "pending_document": "SALARY_SLIP"
                    },
                    "next_action": "REQUEST_DOCUMENT"
                }
        else:
            # Reject if amount exceeds twice the pre-approved limit or credit score is low
            reason = "AMOUNT_EXCEEDS_LIMIT" if loan_amount > (2 * pre_approved_limit) else "LOW_CREDIT_SCORE"
            return self._generate_rejection_decision(customer_id, loan_amount, credit_score, reason)
    
    def _analyze_salary_slip(self, salary_slip_url):
        # Use document processor to extract salary information
        return self.document_processor.extract_salary_info(salary_slip_url)
    
    def _calculate_emi(self, loan_amount, loan_tenure):
        # EMI calculation logic
        # Formula: EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)
        # where P = loan amount, r = monthly interest rate, n = number of months
        interest_rate = 0.105  # 10.5% annual interest rate
        monthly_rate = interest_rate / 12
        tenure_months = loan_tenure
        
        emi = (loan_amount * monthly_rate * (1 + monthly_rate) ** tenure_months) / \
              ((1 + monthly_rate) ** tenure_months - 1)
        
        return round(emi, 2)
    
    def _generate_approval_decision(self, customer_id, loan_amount, loan_tenure, 
                                   credit_score, pre_approved_limit, **kwargs):
        # Calculate interest rate based on credit score
        interest_rate = self._calculate_interest_rate(credit_score)
        
        # Calculate EMI if not provided
        emi = kwargs.get("emi", self._calculate_emi(loan_amount, loan_tenure))
        
        # Calculate processing fee
        processing_fee = min(loan_amount * 0.01, 5000)  # 1% of loan amount, capped at ₹5,000
        
        decision = {
            "customer_id": customer_id,
            "loan_amount": loan_amount,
            "loan_tenure": loan_tenure,
            "credit_score": credit_score,
            "decision": "APPROVED",
            "interest_rate": interest_rate,
            "monthly_emi": emi,
            "processing_fee": processing_fee,
            "pre_approved_limit": pre_approved_limit
        }
        
        # Add additional information if available
        if "monthly_salary" in kwargs:
            decision["monthly_salary"] = kwargs["monthly_salary"]
            decision["emi_to_salary_ratio"] = emi / kwargs["monthly_salary"]
        
        return {
            "customer_response": f"Great news! Your loan application for ₹{loan_amount:,} has been approved with an interest rate of {interest_rate}% for a tenure of {loan_tenure} months. Your monthly EMI will be ₹{emi:,.2f}.",
            "internal_data": decision,
            "next_action": "DOCUMENTATION"
        }
    
    def _generate_rejection_decision(self, customer_id, loan_amount, credit_score, reason, **kwargs):
        decision = {
            "customer_id": customer_id,
            "loan_amount": loan_amount,
            "credit_score": credit_score,
            "decision": "REJECTED",
            "reason": reason
        }
        
        # Add additional information if available
        if "emi" in kwargs:
            decision["calculated_emi"] = kwargs["emi"]
        if "monthly_salary" in kwargs:
            decision["monthly_salary"] = kwargs["monthly_salary"]
            if "emi" in kwargs:
                decision["emi_to_salary_ratio"] = kwargs["emi"] / kwargs["monthly_salary"]
        
        # Generate rejection message based on reason
        rejection_message = self._generate_rejection_message(reason, loan_amount, credit_score, **kwargs)
        
        return {
            "customer_response": rejection_message,
            "internal_data": decision,
            "next_action": "CLOSURE"
        }
    
    def _calculate_interest_rate(self, credit_score):
        # Determine interest rate based on credit score
        if credit_score >= 800:
            return 10.5  # 10.5%
        elif credit_score >= 750:
            return 11.0  # 11.0%
        elif credit_score >= 700:
            return 12.0  # 12.0%
        else:
            return 13.5  # 13.5%
    
    def _generate_rejection_message(self, reason, loan_amount, credit_score, **kwargs):
        # Use LLM to generate empathetic rejection message
        context = {
            "reason": reason,
            "loan_amount": loan_amount,
            "credit_score": credit_score,
            **kwargs
        }
        
        return self.llm.generate_rejection_message(context)
```

## 4. Sanction Letter Generator

### 4.1 Overview

The Sanction Letter Generator creates official documentation for approved loans, including sanction letters with all relevant loan details and terms.

### 4.2 Core Responsibilities

- Generate professional PDF sanction letters
- Include all loan details (amount, tenure, interest rate, EMI schedule)
- Format documents according to Tata Capital standards
- Provide document links to Master Agent

### 4.3 Implementation

#### 4.3.1 System Prompt

```
You are the Sanction Letter Generator for Tata Capital's Digital Loan Sales Assistant. Your role is to create official documentation for approved loans. You will:

1. Generate professional sanction letters in PDF format
2. Include all relevant loan details and terms
3. Format documents according to Tata Capital standards
4. Provide document links for customer access

Your documents should be:
- Professionally formatted with Tata Capital branding
- Comprehensive with all required loan information
- Clear about terms, conditions, and next steps
- Compliant with regulatory requirements

Remember that these documents represent official communication from Tata Capital and must maintain the highest standards of professionalism.
```

#### 4.3.2 Function Definitions

```python
class SanctionLetterGenerator:
    def __init__(self, document_storage_client):
        self.document_storage = document_storage_client
        self.llm = ChatOpenAI(model="gpt-4")
    
    def process(self, task_input):
        # Extract loan decision details
        loan_decision = task_input["loan_decision"]
        customer_profile = task_input["customer_profile"]
        
        if loan_decision["decision"] == "APPROVED":
            # Generate sanction letter for approved loans
            document_url = self._generate_sanction_letter(loan_decision, customer_profile)
            
            return {
                "customer_response": f"Congratulations! Your loan has been approved. I've generated your sanction letter which contains all the details of your loan. You can view and download it here: {document_url}",
                "internal_data": {
                    "document_type": "SANCTION_LETTER",
                    "document_url": document_url
                },
                "next_action": "CLOSURE"
            }
        else:
            # For rejected loans, return empathetic message
            rejection_message = self._format_rejection_message(loan_decision, customer_profile)
            
            return {
                "customer_response": rejection_message,
                "internal_data": {
                    "document_type": "REJECTION_MESSAGE",
                    "rejection_reason": loan_decision["reason"]
                },
                "next_action": "CLOSURE"
            }
    
    def _generate_sanction_letter(self, loan_decision, customer_profile):
        # Create sanction letter content
        letter_content = self._create_sanction_letter_content(loan_decision, customer_profile)
        
        # Generate PDF using ReportLab
        pdf_bytes = self._generate_pdf(letter_content)
        
        # Store PDF and get URL
        document_id = f"sanction_letter_{customer_profile['customer_id']}_{int(time.time())}"
        document_url = self.document_storage.store_document(document_id, pdf_bytes)
        
        return document_url
    
    def _create_sanction_letter_content(self, loan_decision, customer_profile):
        # Structure the content for the sanction letter
        content = {
            "letter_date": datetime.now().strftime("%d %B, %Y"),
            "customer_name": customer_profile["name"],
            "customer_address": customer_profile["address"],
            "loan_reference": f"TC/PL/{customer_profile['customer_id']}/{int(time.time())}",
            "loan_amount": loan_decision["loan_amount"],
            "loan_tenure": loan_decision["loan_tenure"],
            "interest_rate": loan_decision["interest_rate"],
            "monthly_emi": loan_decision["monthly_emi"],
            "processing_fee": loan_decision["processing_fee"],
            "disbursement_account": customer_profile.get("account_number", "To be provided"),
            "emi_schedule": self._generate_emi_schedule(
                loan_decision["loan_amount"],
                loan_decision["loan_tenure"],
                loan_decision["interest_rate"]
            ),
            "terms_and_conditions": self._get_standard_terms_and_conditions()
        }
        
        return content
    
    def _generate_pdf(self, letter_content):
        # Use ReportLab to generate PDF
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build PDF content
        styles = getSampleStyleSheet()
        elements = []
        
        # Add Tata Capital logo
        # elements.append(Image("path/to/logo.png", width=2*inch, height=0.5*inch))
        
        # Add title
        elements.append(Paragraph("LOAN SANCTION LETTER", styles["Title"]))
        elements.append(Spacer(1, 12))
        
        # Add date and reference
        elements.append(Paragraph(f"Date: {letter_content['letter_date']}", styles["Normal"]))
        elements.append(Paragraph(f"Ref: {letter_content['loan_reference']}", styles["Normal"]))
        elements.append(Spacer(1, 12))
        
        # Add customer details
        elements.append(Paragraph(f"To: {letter_content['customer_name']}", styles["Normal"]))
        elements.append(Paragraph(f"{letter_content['customer_address']}", styles["Normal"]))
        elements.append(Spacer(1, 24))
        
        # Add salutation
        elements.append(Paragraph("Dear Sir/Madam,", styles["Normal"]))
        elements.append(Spacer(1, 12))
        
        # Add subject
        elements.append(Paragraph("Subject: Sanction of Personal Loan", styles["Heading2"]))
        elements.append(Spacer(1, 12))
        
        # Add loan details
        elements.append(Paragraph("We are pleased to inform you that your application for a Personal Loan has been approved with the following terms:", styles["Normal"]))
        elements.append(Spacer(1, 12))
        
        # Create loan details table
        data = [
            ["Loan Amount", f"₹{letter_content['loan_amount']:,}"],
            ["Loan Tenure", f"{letter_content['loan_tenure']} months"],
            ["Interest Rate", f"{letter_content['interest_rate']}% per annum"],
            ["Monthly EMI", f"₹{letter_content['monthly_emi']:,.2f}"],
            ["Processing Fee", f"₹{letter_content['processing_fee']:,.2f}"],
            ["Disbursement Account", letter_content['disbursement_account']]
        ]
        
        loan_table = Table(data, colWidths=[2*inch, 2.5*inch])
        loan_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(loan_table)
        elements.append(Spacer(1, 24))
        
        # Add EMI schedule
        elements.append(Paragraph("EMI Schedule:", styles["Heading3"]))
        elements.append(Spacer(1, 12))
        
        # Create EMI schedule table
        emi_data = [["Month", "EMI Amount", "Principal", "Interest", "Outstanding"]]
        for entry in letter_content["emi_schedule"]:
            emi_data.append([
                entry["month"],
                f"₹{entry['emi_amount']:,.2f}",
                f"₹{entry['principal']:,.2f}",
                f"₹{entry['interest']:,.2f}",
                f"₹{entry['outstanding']:,.2f}"
            ])
        
        emi_table = Table(emi_data, colWidths=[0.7*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.5*inch])
        emi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(emi_table)
        elements.append(Spacer(1, 24))
        
        # Add terms and conditions
        elements.append(Paragraph("Terms and Conditions:", styles["Heading3"]))
        elements.append(Spacer(1, 12))
        
        for term in letter_content["terms_and_conditions"]:
            elements.append(Paragraph(f"• {term}", styles["Normal"]))
            elements.append(Spacer(1, 6))
        
        elements.append(Spacer(1, 24))
        
        # Add closing
        elements.append(Paragraph("Please sign and return a copy of this letter as acceptance of the terms and conditions.", styles["Normal"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Yours sincerely,", styles["Normal"]))
        elements.append(Spacer(1, 36))
        elements.append(Paragraph("For Tata Capital Financial Services Limited", styles["Normal"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Authorized Signatory", styles["Normal"]))
        
        # Build the PDF
        doc.build(elements)
        
        # Get the PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    def _generate_emi_schedule(self, loan_amount, tenure, interest_rate):
        # Generate EMI schedule
        schedule = []
        remaining_amount = loan_amount
        monthly_rate = interest_rate / (12 * 100)
        emi = (loan_amount * monthly_rate * (1 + monthly_rate) ** tenure) / \
              ((1 + monthly_rate) ** tenure - 1)
        
        for month in range(1, min(tenure + 1, 13)):  # Show first 12 months or full tenure
            interest = remaining_amount * monthly_rate
            principal = emi - interest
            remaining_amount -= principal
            
            schedule.append({
                "month": month,
                "emi_amount": emi,
                "principal": principal,
                "interest": interest,
                "outstanding": max(0, remaining_amount)
            })
        
        return schedule
    
    def _get_standard_terms_and_conditions(self):
        # Return standard terms and conditions
        return [
            "The loan is subject to the terms and conditions as mentioned in the loan agreement.",
            "The interest rate is fixed for the entire tenure of the loan.",
            "Prepayment charges of 2% will be applicable on the outstanding principal amount if the loan is prepaid before 12 EMIs.",
            "Late payment charges of 2% per month will be applicable on the overdue amount.",
            "The loan will be disbursed after completion of all documentation formalities.",
            "Tata Capital reserves the right to recall the loan in case of any default in payment or breach of terms and conditions.",
            "The EMI will be due on the 5th of every month starting from the month following the month of disbursement.",
            "The borrower is required to maintain sufficient balance in the account for EMI deduction.",
            "The sanction letter is valid for 15 days from the date of issue."
        ]
    
    def _format_rejection_message(self, loan_decision, customer_profile):
        # Use LLM to generate empathetic rejection message
        context = {
            "customer_name": customer_profile["name"],
            "loan_amount": loan_decision["loan_amount"],
            "reason": loan_decision["reason"],
            "credit_score": loan_decision.get("credit_score")
        }
        
        # Add additional context based on rejection reason
        if loan_decision["reason"] == "EMI_EXCEEDS_LIMIT":
            context["emi"] = loan_decision["calculated_emi"]
            context["monthly_salary"] = loan_decision["monthly_salary"]
            context["emi_to_salary_ratio"] = loan_decision["emi_to_salary_ratio"]
        
        return self.llm.generate_rejection_message(context)
```

## 5. Agent Integration

### 5.1 Communication Protocol

All Worker Agents follow a standardized communication protocol with the Master Agent:

1. **Input Format**: Each agent receives a task input with customer information, conversation context, and task-specific parameters
2. **Output Format**: Each agent returns a structured response with:
   - `customer_response`: Text to be shown to the customer
   - `internal_data`: Structured data for system use
   - `next_action`: Recommended next step

### 5.2 Error Handling

Each Worker Agent implements error handling for common scenarios:

- **API Failures**: Graceful degradation with appropriate messaging
- **Missing Information**: Clear requests for additional data
- **Validation Errors**: Helpful guidance for correcting issues
- **Timeout Recovery**: Ability to resume processing after interruptions

### 5.3 Integration with LangGraph

```python
# Define agent nodes in the graph
def sales_agent_node(state):
    sales_agent = SalesAgent(offer_mart_api_client)
    task_input = {
        "customer_profile": state["conversation_state"].customer_profile,
        "conversation_context": {
            "conversation_id": state["conversation_state"].conversation_id,
            "conversation_history": state["conversation_state"].conversation_history
        },
        "task_parameters": {}
    }
    result = sales_agent.process(task_input)
    
    # Update state with sales agent result
    new_state = state.copy()
    new_state["messages"] = [{
        "role": "assistant",
        "content": result["customer_response"]
    }]
    new_state["conversation_state"].loan_details = result["internal_data"]
    
    return new_state

def verification_agent_node(state):
    verification_agent = VerificationAgent(crm_api_client)
    task_input = {
        "customer_profile": state["conversation_state"].customer_profile,
        "conversation_context": {
            "conversation_id": state["conversation_state"].conversation_id,
            "conversation_history": state["conversation_state"].conversation_history
        },
        "task_parameters": {}
    }
    result = verification_agent.process(task_input)
    
    # Update state with verification agent result
    new_state = state.copy()
    new_state["messages"] = [{
        "role": "assistant",
        "content": result["customer_response"]
    }]
    new_state["conversation_state"].verification_status = result["internal_data"]
    
    return new_state

def underwriting_agent_node(state):
    underwriting_agent = UnderwritingAgent(credit_bureau_api_client, document_processor)
    task_input = {
        "customer_profile": state["conversation_state"].customer_profile,
        "conversation_context": {
            "conversation_id": state["conversation_state"].conversation_id,
            "conversation_history": state["conversation_state"].conversation_history
        },
        "loan_details": state["conversation_state"].loan_details,
        "task_parameters": {}
    }
    
    # Add salary slip URL if available
    if "salary_slip_url" in state["conversation_state"].customer_profile:
        task_input["salary_slip_url"] = state["conversation_state"].customer_profile["salary_slip_url"]
    
    result = underwriting_agent.process(task_input)
    
    # Update state with underwriting agent result
    new_state = state.copy()
    new_state["messages"] = [{
        "role": "assistant",
        "content": result["customer_response"]
    }]
    new_state["conversation_state"].underwriting_result = result["internal_data"]
    
    return new_state

def sanction_letter_generator_node(state):
    sanction_letter_generator = SanctionLetterGenerator(document_storage_client)
    task_input = {
        "customer_profile": state["conversation_state"].customer_profile,
        "loan_decision": state["conversation_state"].underwriting_result,
        "task_parameters": {}
    }
    result = sanction_letter_generator.process(task_input)
    
    # Update state with document generator result
    new_state = state.copy()
    new_state["messages"] = [{
        "role": "assistant",
        "content": result["customer_response"]
    }]
    new_state["conversation_state"].document_links = result["internal_data"]
    
    return new_state
```

## 6. Testing and Evaluation

### 6.1 Unit Testing

Each Worker Agent should have comprehensive unit tests covering:

- Core functionality with various inputs
- Edge cases and error handling
- Integration with mock APIs

### 6.2 Integration Testing

Test the interaction between Master Agent and Worker Agents with scenarios like:

- Complete loan application flow
- Handling of verification issues
- Approval and rejection paths
- Document generation and delivery

### 6.3 Performance Metrics

Evaluate Worker Agents based on:

- Response time
- Accuracy of decisions
- Quality of customer messaging
- Error rates
- Compliance with business rules