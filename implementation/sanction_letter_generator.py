# Sanction Letter Generator Agent for Tata Capital Digital Loan Sales Assistant

import json
import os
import sys
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import mock APIs
from implementation.mock_apis import DocumentStorage

# Configure logging
logger = logging.getLogger(__name__)

class SanctionLetterGenerator:
    """Sanction Letter Generator Agent responsible for creating loan documentation"""
    
    def __init__(self, customers_df=None):
        """Initialize the Sanction Letter Generator Agent with required APIs and data
        
        Args:
            customers_df: DataFrame containing customer information
        """
        self.document_storage = DocumentStorage()
        
        # Load CSV data if not provided
        try:
            self.customers_df = customers_df if customers_df is not None else pd.read_csv(os.path.join('data', 'customers.csv'))
            logger.info("Sanction Letter Generator initialized with CSV data")
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            # Initialize empty DataFrame as fallback
            self.customers_df = pd.DataFrame()
        
        # Ensure output directory exists
        self.output_dir = os.path.join(os.getcwd(), 'output')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # System prompt for the Sanction Letter Generator
        self.system_prompt = """
        You are a professional and precise Sanction Letter Generator for Tata Capital, a leading NBFC in India.
        Your role is to create official loan documentation and communicate decisions to customers.
        
        Follow these guidelines:
        1. Generate clear, professional sanction letters for approved loans
        2. Craft empathetic, personalized rejection messages
        3. Ensure all documentation includes accurate loan details
        4. Maintain a formal yet approachable tone
        5. Follow regulatory compliance in all communications
        6. Protect customer financial data and privacy
        
        Your goal is to provide customers with clear, accurate, and professional documentation.
        """
    
    def process(self, state) -> Dict:
        """Process the current conversation state and generate appropriate documentation
        
        Args:
            state: The conversation state object from the Master Agent
            
        Returns:
            Updated state object with documentation information
        """
        logger.info("Sanction Letter Generator processing conversation state")
        
        # Extract relevant information from state
        loan_details = state.loan_details or {}
        customer_details = state.customer_details or {}
        underwriting_status = state.underwriting_status or {}
        
        # Check if we have a customer ID
        customer_id = customer_details.get("customer_id")
        
        if not customer_id:
            logger.warning("No customer ID found in state")
            state.documentation_status = {
                "status": "error",
                "reason": "Customer ID not found"
            }
            return state
        
        # Check underwriting status
        loan_status = underwriting_status.get("status")
        
        if not loan_status:
            logger.warning("No underwriting decision found")
            state.documentation_status = {
                "status": "pending",
                "reason": "Waiting for underwriting decision"
            }
            return state
        
        # Generate appropriate documentation based on loan status
        if loan_status == "approved":
            # Generate sanction letter for approved loan
            pdf_path = self._generate_sanction_letter(customer_id, customer_details, loan_details, underwriting_status)
            
            if pdf_path:
                state.documentation_status = {
                    "status": "completed",
                    "document_type": "sanction_letter",
                    "document_path": pdf_path
                }
                logger.info(f"Sanction letter generated for customer {customer_id}: {pdf_path}")
            else:
                state.documentation_status = {
                    "status": "error",
                    "reason": "Failed to generate sanction letter"
                }
                logger.error(f"Failed to generate sanction letter for customer {customer_id}")
        
        elif loan_status == "conditional_approval":
            # Generate conditional approval letter
            pdf_path = self._generate_conditional_approval_letter(customer_id, customer_details, loan_details, underwriting_status)
            
            if pdf_path:
                state.documentation_status = {
                    "status": "completed",
                    "document_type": "conditional_approval",
                    "document_path": pdf_path
                }
                logger.info(f"Conditional approval letter generated for customer {customer_id}: {pdf_path}")
            else:
                state.documentation_status = {
                    "status": "error",
                    "reason": "Failed to generate conditional approval letter"
                }
                logger.error(f"Failed to generate conditional approval letter for customer {customer_id}")
        
        elif loan_status == "rejected":
            # Generate rejection letter
            pdf_path = self._generate_rejection_letter(customer_id, customer_details, loan_details, underwriting_status)
            
            if pdf_path:
                state.documentation_status = {
                    "status": "completed",
                    "document_type": "rejection_letter",
                    "document_path": pdf_path
                }
                logger.info(f"Rejection letter generated for customer {customer_id}: {pdf_path}")
            else:
                state.documentation_status = {
                    "status": "error",
                    "reason": "Failed to generate rejection letter"
                }
                logger.error(f"Failed to generate rejection letter for customer {customer_id}")
        
        else:
            # Unknown status
            state.documentation_status = {
                "status": "error",
                "reason": f"Unknown loan status: {loan_status}"
            }
            logger.warning(f"Unknown loan status for customer {customer_id}: {loan_status}")
        
        return state
    
    def _generate_sanction_letter(self, customer_id: str, customer_details: Dict, loan_details: Dict, underwriting_status: Dict) -> Optional[str]:
        """Generate a sanction letter for an approved loan
        
        Args:
            customer_id: The customer ID
            customer_details: Dictionary with customer information
            loan_details: Dictionary with loan information
            underwriting_status: Dictionary with underwriting status
            
        Returns:
            Path to the generated PDF or None if generation failed
        """
        try:
            # Create filename
            filename = f"sanction_letter_{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Add Tata Capital header
            header_style = ParagraphStyle(
                'Header',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.darkblue,
                spaceAfter=12
            )
            elements.append(Paragraph("TATA CAPITAL", header_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add title
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12
            )
            elements.append(Paragraph("LOAN SANCTION LETTER", title_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add date
            date_style = styles["Normal"]
            elements.append(Paragraph(f"Date: {datetime.now().strftime('%d-%m-%Y')}", date_style))
            elements.append(Spacer(1, 0.1*inch))
            
            # Add reference number
            ref_num = f"TC/LOAN/{customer_id}/{datetime.now().strftime('%Y%m%d')}"
            elements.append(Paragraph(f"Reference Number: {ref_num}", date_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add customer details
            elements.append(Paragraph(f"To: {customer_details.get('name', 'Valued Customer')}", styles["Normal"]))
            if 'address' in customer_details:
                elements.append(Paragraph(f"Address: {customer_details['address']}", styles["Normal"]))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add subject
            subject_style = ParagraphStyle(
                'Subject',
                parent=styles['Normal'],
                fontName='Helvetica-Bold'
            )
            elements.append(Paragraph("Subject: Sanction of Loan", subject_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add greeting
            elements.append(Paragraph("Dear Sir/Madam,", styles["Normal"]))
            elements.append(Spacer(1, 0.1*inch))
            
            # Add body
            body_text = f"""We are pleased to inform you that your loan application has been approved. The details of the sanctioned loan are as follows:"""
            elements.append(Paragraph(body_text, styles["Normal"]))
            elements.append(Spacer(1, 0.2*inch))
            
            # Add loan details table
            loan_amount = loan_details.get("loan_amount", "N/A")
            loan_tenure = loan_details.get("loan_tenure", "N/A")
            interest_rate = underwriting_status.get("interest_rate", "N/A")
            
            data = [
                ["Loan Details", ""],
                ["Loan Amount", f"₹ {loan_amount}"],
                ["Loan Tenure", f"{loan_tenure} months"],
                ["Interest Rate", f"{interest_rate}% per annum"],
                ["Processing Fee", "1% of loan amount"]
            ]
            
            table = Table(data, colWidths=[2.5*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.darkblue),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.25*inch))
            
            # Add terms and conditions
            elements.append(Paragraph("Terms and Conditions:", subject_style))
            elements.append(Spacer(1, 0.1*inch))
            
            terms = [
                "1. The loan is subject to the terms and conditions as mentioned in the loan agreement.",
                "2. The interest rate is fixed for the entire tenure of the loan.",
                "3. Prepayment charges as applicable as per the loan agreement.",
                "4. Late payment charges will be applicable as per the loan agreement.",
                "5. The loan amount will be disbursed after completion of all documentation formalities."
            ]
            
            for term in terms:
                elements.append(Paragraph(term, styles["Normal"]))
                elements.append(Spacer(1, 0.05*inch))
            
            elements.append(Spacer(1, 0.25*inch))
            
            # Add closing
            elements.append(Paragraph("Thanking you,", styles["Normal"]))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("Yours faithfully,", styles["Normal"]))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("For Tata Capital Financial Services Limited", styles["Normal"]))
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("Authorized Signatory", styles["Normal"]))
            
            # Build PDF
            doc.build(elements)
            
            logger.info(f"Sanction letter generated successfully: {pdf_path}")
            return pdf_path
        
        except Exception as e:
            logger.error(f"Error generating sanction letter: {e}")
            return None
            
    def _generate_sanction_letter_content(self, customer_id: str, customer_details: Dict, loan_details: Dict, underwriting_status: Dict) -> str:
        """Generate the content for a sanction letter
        
        Args:
            customer_id: The unique identifier for the customer
            customer_details: Dictionary containing customer information
            loan_details: Dictionary containing loan information
            underwriting_status: Dictionary containing underwriting results
            
        Returns:
            String containing the sanction letter content
        """
        # Extract customer information
        customer_name = customer_details.get("name", "Valued Customer")
        customer_address = customer_details.get("address", "")
        
        # Extract loan information
        loan_amount = loan_details.get("loan_amount", 0)
        loan_tenure = loan_details.get("loan_tenure", 0)
        interest_rate = underwriting_status.get("interest_rate", 11)  # Default to 11% if not specified
        loan_purpose = loan_details.get("purpose", "Personal Expenses")
        
        # Extract EMI information
        emi = underwriting_status.get("calculated_emi", 0)
        
        # Calculate processing fee (typically 1-2% of loan amount)
        processing_fee_rate = 0.01  # 1%
        processing_fee = loan_amount * processing_fee_rate
        
        # Calculate disbursement amount
        disbursement_amount = loan_amount - processing_fee
        
        # Generate current date
        current_date = datetime.now().strftime("%d-%m-%Y")
        
        # Generate sanction letter reference number
        reference_number = f"TC/PL/{customer_id}/{current_date.replace('-', '')}"
        
        # Generate EMI schedule (simplified for this example)
        emi_schedule = []
        remaining_principal = loan_amount
        for month in range(1, min(loan_tenure + 1, 13)):  # Show first 12 months or less
            interest_payment = remaining_principal * (interest_rate / (12 * 100))
            principal_payment = emi - interest_payment
            remaining_principal -= principal_payment
            
            emi_schedule.append({
                "month": month,
                "emi": emi,
                "principal": principal_payment,
                "interest": interest_payment,
                "remaining_principal": max(0, remaining_principal)
            })
        
        # Generate sanction letter content
        sanction_letter = f"""
        TATA CAPITAL FINANCIAL SERVICES LIMITED
        Corporate Office: One World Center, 16th Floor, Tower 2A, 
        Jupiter Mills Compound, Senapati Bapat Marg, Mumbai - 400013
        
        Date: {current_date}
        Reference No: {reference_number}
        
        SANCTION LETTER
        
        To,
        {customer_name}
        {customer_address}
        
        Dear {customer_name.split()[0]},
        
        Subject: Sanction of Personal Loan
        
        We are pleased to inform you that your application for a Personal Loan has been approved with the following terms and conditions:
        
        LOAN DETAILS:
        
        1. Loan Amount: ₹{loan_amount:,}
        2. Loan Tenure: {loan_tenure} months
        3. Interest Rate: {interest_rate}% per annum (fixed)
        4. Processing Fee: ₹{processing_fee:,.2f} ({processing_fee_rate*100}% of loan amount)
        5. Disbursement Amount: ₹{disbursement_amount:,.2f}
        6. Monthly EMI: ₹{emi:,.2f}
        7. Loan Purpose: {loan_purpose}
        
        EMI SCHEDULE (First {len(emi_schedule)} months):
        
        Month | EMI Amount | Principal | Interest | Remaining Principal
        ------|------------|-----------|----------|--------------------
        """
        
        # Add EMI schedule to sanction letter
        for month_data in emi_schedule:
            sanction_letter += f"{month_data['month']:5d} | ₹{month_data['emi']:9,.2f} | ₹{month_data['principal']:8,.2f} | ₹{month_data['interest']:7,.2f} | ₹{month_data['remaining_principal']:19,.2f}\n        "
        
        # Add terms and conditions
        sanction_letter += f"""
        
        TERMS AND CONDITIONS:
        
        1. The loan will be disbursed to your registered bank account within 2 working days.
        2. EMI payments will commence from the next month after disbursement.
        3. EMIs will be deducted through ECS/NACH mandate on the 5th of every month.
        4. Prepayment charges of 2% will be applicable for partial or full prepayments made within 6 months of loan disbursal.
        5. Late payment charges of 2% per month will be applicable on the overdue amount.
        6. The loan is subject to the terms and conditions mentioned in the loan agreement.
        
        This sanction letter is valid for 15 days from the date of issue. Please accept the offer by signing the loan agreement and completing the verification process.
        
        For any queries, please contact our customer care at 1800-267-8282 or email us at customercare@tatacapital.com.
        
        Yours sincerely,
        
        Loan Sanction Team
        Tata Capital Financial Services Limited
        
        Note: This is a system-generated letter and does not require a physical signature.
        """
        
        return sanction_letter
    
    def _generate_conditional_approval_letter(self, customer_id: str, customer_details: Dict, loan_details: Dict, underwriting_status: Dict) -> Optional[str]:
        """Generate a conditional approval letter
        
        Args:
            customer_id: The customer ID
            customer_details: Dictionary with customer information
            loan_details: Dictionary with loan information
            underwriting_status: Dictionary with underwriting status
            
        Returns:
            Path to the generated PDF or None if generation failed
        """
        try:
            # Create filename
            filename = f"conditional_approval_{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Add Tata Capital header
            header_style = ParagraphStyle(
                'Header',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.darkblue,
                spaceAfter=12
            )
            elements.append(Paragraph("TATA CAPITAL", header_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add title
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12
            )
            elements.append(Paragraph("CONDITIONAL LOAN APPROVAL", title_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add date
            date_style = styles["Normal"]
            elements.append(Paragraph(f"Date: {datetime.now().strftime('%d-%m-%Y')}", date_style))
            elements.append(Spacer(1, 0.1*inch))
            
            # Add reference number
            ref_num = f"TC/COND/{customer_id}/{datetime.now().strftime('%Y%m%d')}"
            elements.append(Paragraph(f"Reference Number: {ref_num}", date_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add customer details
            elements.append(Paragraph(f"To: {customer_details.get('name', 'Valued Customer')}", styles["Normal"]))
            if 'address' in customer_details:
                elements.append(Paragraph(f"Address: {customer_details['address']}", styles["Normal"]))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add subject
            subject_style = ParagraphStyle(
                'Subject',
                parent=styles['Normal'],
                fontName='Helvetica-Bold'
            )
            elements.append(Paragraph("Subject: Conditional Approval of Loan", subject_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add greeting
            elements.append(Paragraph("Dear Sir/Madam,", styles["Normal"]))
            elements.append(Spacer(1, 0.1*inch))
            
            # Add body
            body_text = f"""We are pleased to inform you that your loan application has been conditionally approved. The approval is subject to fulfillment of certain conditions as mentioned below."""
            elements.append(Paragraph(body_text, styles["Normal"]))
            elements.append(Spacer(1, 0.2*inch))
            
            # Add loan details table
            loan_amount = loan_details.get("loan_amount", "N/A")
            loan_tenure = loan_details.get("loan_tenure", "N/A")
            interest_rate = underwriting_status.get("interest_rate", "N/A")
            
            data = [
                ["Loan Details", ""],
                ["Loan Amount", f"₹ {loan_amount}"],
                ["Loan Tenure", f"{loan_tenure} months"],
                ["Interest Rate", f"{interest_rate}% per annum"],
                ["Processing Fee", "1% of loan amount"]
            ]
            
            table = Table(data, colWidths=[2.5*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.darkblue),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.25*inch))
            
            # Add conditions
            elements.append(Paragraph("Conditions for Final Approval:", subject_style))
            elements.append(Spacer(1, 0.1*inch))
            
            conditions = underwriting_status.get("conditions", ["Additional documentation required"])
            
            for i, condition in enumerate(conditions, 1):
                elements.append(Paragraph(f"{i}. {condition}", styles["Normal"]))
                elements.append(Spacer(1, 0.05*inch))
            
            elements.append(Spacer(1, 0.25*inch))
            
            # Add next steps
            elements.append(Paragraph("Next Steps:", subject_style))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("Please submit the required documents at your earliest convenience to proceed with the final approval of your loan application.", styles["Normal"]))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add closing
            elements.append(Paragraph("Thanking you,", styles["Normal"]))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("Yours faithfully,", styles["Normal"]))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("For Tata Capital Financial Services Limited", styles["Normal"]))
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("Authorized Signatory", styles["Normal"]))
            
            # Build PDF
            doc.build(elements)
            
            logger.info(f"Conditional approval letter generated successfully: {pdf_path}")
            return pdf_path
        
        except Exception as e:
            logger.error(f"Error generating conditional approval letter: {e}")
            return None
    
    def _generate_rejection_letter(self, customer_id: str, customer_details: Dict, loan_details: Dict, underwriting_status: Dict) -> Optional[str]:
        """Generate a rejection letter
        
        Args:
            customer_id: The customer ID
            customer_details: Dictionary with customer information
            loan_details: Dictionary with loan information
            underwriting_status: Dictionary with underwriting status
            
        Returns:
            Path to the generated PDF or None if generation failed
        """
        try:
            # Create filename
            filename = f"rejection_letter_{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Add Tata Capital header
            header_style = ParagraphStyle(
                'Header',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.darkblue,
                spaceAfter=12
            )
            elements.append(Paragraph("TATA CAPITAL", header_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add title
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12
            )
            elements.append(Paragraph("LOAN APPLICATION STATUS", title_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add date
            date_style = styles["Normal"]
            elements.append(Paragraph(f"Date: {datetime.now().strftime('%d-%m-%Y')}", date_style))
            elements.append(Spacer(1, 0.1*inch))
            
            # Add reference number
            ref_num = f"TC/REJ/{customer_id}/{datetime.now().strftime('%Y%m%d')}"
            elements.append(Paragraph(f"Reference Number: {ref_num}", date_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add customer details
            elements.append(Paragraph(f"To: {customer_details.get('name', 'Valued Customer')}", styles["Normal"]))
            if 'address' in customer_details:
                elements.append(Paragraph(f"Address: {customer_details['address']}", styles["Normal"]))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add subject
            subject_style = ParagraphStyle(
                'Subject',
                parent=styles['Normal'],
                fontName='Helvetica-Bold'
            )
            elements.append(Paragraph("Subject: Status of Loan Application", subject_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add greeting
            elements.append(Paragraph("Dear Sir/Madam,", styles["Normal"]))
            elements.append(Spacer(1, 0.1*inch))
            
            # Add body
            reason = underwriting_status.get("reason", "Unable to meet lending criteria at this time")
            body_text = f"""Thank you for your loan application with Tata Capital. We appreciate your interest in our financial services.

After careful consideration of your application, we regret to inform you that we are unable to approve your loan request at this time. The decision was based on the following reason:

{reason}

Please note that this decision does not reflect on your character or financial responsibility. We encourage you to review your credit profile and consider reapplying in the future when your circumstances change."""
            
            for paragraph in body_text.split("\n"):
                elements.append(Paragraph(paragraph, styles["Normal"]))
                elements.append(Spacer(1, 0.1*inch))
            
            elements.append(Spacer(1, 0.15*inch))
            
            # Add alternative options
            elements.append(Paragraph("Alternative Options:", subject_style))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("You may consider exploring other loan products that might better suit your current financial situation. Our customer service team would be happy to discuss these options with you.", styles["Normal"]))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add closing
            elements.append(Paragraph("Thanking you,", styles["Normal"]))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("Yours faithfully,", styles["Normal"]))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("For Tata Capital Financial Services Limited", styles["Normal"]))
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("Authorized Signatory", styles["Normal"]))
            
            # Build PDF
            doc.build(elements)
            
            logger.info(f"Rejection letter generated successfully: {pdf_path}")
            return pdf_path
        
        except Exception as e:
            logger.error(f"Error generating rejection letter: {e}")
            return None
    def _determine_documentation_stage(self, conversation_state: Dict) -> str:
        """Determine the current stage in the documentation process
        
        Args:
            conversation_state: The current state of the conversation
            
        Returns:
            String indicating the current documentation stage
        """
        # Extract underwriting status and documentation status
        underwriting_status = conversation_state.get("underwriting_status", {})
        documentation_status = conversation_state.get("documentation_status", {})
        
        # If no documentation has been done, determine based on underwriting decision
        if not documentation_status:
            decision = underwriting_status.get("decision")
            if decision == "APPROVED":
                return "generate_sanction_letter"
            elif decision == "CONDITIONAL_APPROVAL":
                return "generate_conditional_approval"
            elif decision == "REJECTED":
                return "handle_rejection"
            else:
                # If no decision yet, wait for underwriting
                return "waiting_for_underwriting"
        
        # If document has been generated but not shared, proceed to sharing
        if documentation_status.get("document_generated") and not documentation_status.get("document_shared"):
            return "share_document"
        
        # If document has been shared, we're done
        if documentation_status.get("document_shared"):
            return "documentation_complete"
        
        # Default to waiting for underwriting
        return "waiting_for_underwriting"
    
    def _handle_sanction_letter_generation(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the sanction letter generation stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the sanction letter generation results and next action
        """
        try:
            # Extract relevant information
            loan_details = conversation_state.get("loan_details", {})
            customer_details = conversation_state.get("customer_details", {})
            underwriting_status = conversation_state.get("underwriting_status", {})
            loan_summary = conversation_state.get("loan_summary", {})
            
            # Check if we have all required information
            if not loan_details or not customer_details or not underwriting_status:
                return {
                    "customer_response": "I'm missing some information needed to generate your sanction letter. Let me check with our underwriting team.",
                    "internal_data": {
                        "documentation_stage": "waiting_for_underwriting",
                        "error": "Missing required information",
                        "confidence": 0.5
                    },
                    "next_action": "return_to_underwriting"
                }
            
            # Check if the loan was approved
            decision = underwriting_status.get("decision")
            if decision != "APPROVED":
                return self._handle_rejection(customer_id, conversation_state)
            
            # Generate sanction letter PDF
            pdf_path = self._generate_sanction_letter(
                customer_id, customer_details, loan_details, underwriting_status
            )
            
            if not pdf_path:
                return {
                    "customer_response": "I'm having trouble generating your sanction letter. Let me check with our technical team.",
                    "internal_data": {
                        "documentation_stage": "generate_sanction_letter",
                        "error": "Failed to generate PDF",
                        "confidence": 0.5
                    },
                    "next_action": "retry_generation"
                }
            
            # Initialize documentation status
            documentation_status = {
                "document_generated": True,
                "document_type": "sanction_letter",
                "document_path": pdf_path,
                "generation_timestamp": datetime.now().isoformat(),
                "document_shared": False
            }
            
            # Generate appropriate response
            response = "I've generated your loan sanction letter. It contains all the details of your approved loan, including the loan amount, tenure, interest rate, and EMI. Would you like me to share it with you now?"
            
            return {
                "customer_response": response,
                "internal_data": {
                    "documentation_stage": "share_document",
                    "documentation_status": documentation_status,
                    "confidence": 0.9
                },
                "next_action": "confirm_document_sharing"
            }
            
        except Exception as e:
            # Handle unexpected errors
            return {
                "customer_response": "I'm experiencing some technical difficulties generating your sanction letter. Please bear with me while I resolve this issue.",
                "internal_data": {
                    "documentation_stage": "generate_sanction_letter",
                    "error": str(e),
                    "confidence": 0.4
                },
                "next_action": "retry_document_generation"
            }
    
    def _handle_rejection(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the rejection stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the rejection results and next action
        """
        # Extract relevant information
        loan_details = conversation_state.get("loan_details", {})
        customer_details = conversation_state.get("customer_details", {})  
        underwriting_status = conversation_state.get("underwriting_status", {})
        
        # Get the rejection reason
        reason = underwriting_status.get("reason", "Did not meet eligibility criteria")
        
        # Generate personalized rejection message
        customer_name = customer_details.get("name", "Valued Customer")
        loan_amount = loan_details.get("loan_amount", 0)
        
        # Generate rejection letter PDF
        pdf_path = self._generate_rejection_letter(
            customer_id, customer_details, loan_details, underwriting_status
        )
        
        # Initialize documentation status
        documentation_status = {
            "document_generated": True,
            "document_type": "rejection_letter",
            "document_path": pdf_path,
            "generation_timestamp": datetime.now().isoformat(),
            "document_shared": True,  # No need to explicitly share rejection letter
            "rejection_reason": reason
        }
        
        # Generate appropriate response based on rejection reason
        if "credit score" in reason.lower():
            response = f"I understand this isn't the news you were hoping for, {customer_name}. Unfortunately, we couldn't approve your loan application for ₹{loan_amount:,} at this time due to credit score considerations. I'd like to suggest a few steps that might help improve your credit profile for future applications. Would you like some guidance on this?"
            alternative_action = "offer_credit_improvement_tips"
        elif "emi-to-income" in reason.lower():
            response = f"I understand this isn't the news you were hoping for, {customer_name}. Unfortunately, we couldn't approve your loan application for ₹{loan_amount:,} at this time because the EMI would exceed our recommended limit relative to your income. Would you like to explore a lower loan amount that might work better with your current income?"
            alternative_action = "offer_lower_loan_amount"
        elif "exceeds maximum" in reason.lower():
            response = f"I understand this isn't the news you were hoping for, {customer_name}. Unfortunately, we couldn't approve your loan application for ₹{loan_amount:,} at this time as it exceeds our maximum eligible amount based on your profile. Would you like to explore a pre-approved offer that's available for you?"
            alternative_action = "offer_pre_approved_amount"
        else:
            response = f"I understand this isn't the news you were hoping for, {customer_name}. Unfortunately, we couldn't approve your loan application for ₹{loan_amount:,} at this time. Our decision was based on {reason}. Is there anything else I can help you with today?"
            alternative_action = "offer_assistance"
        
        return {
            "customer_response": response,
            "internal_data": {
                "documentation_stage": "documentation_complete",
                "documentation_status": documentation_status,
                "confidence": 0.9
            },
            "next_action": alternative_action
        }
    
    def _handle_document_sharing(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the document sharing stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the document sharing results and next action
        """
        # Extract relevant information
        documentation_status = conversation_state.get("documentation_status", {})
        customer_message = conversation_state.get("last_customer_message", "").lower()
        
        # Check if we have a document to share
        if not documentation_status or not documentation_status.get("document_generated"):
            return self._handle_sanction_letter_generation(customer_id, conversation_state)
        
        # Check if the customer wants to see the document
        if not self._check_for_confirmation(customer_message) and not "share" in customer_message:
            # If customer hasn't confirmed, ask again
            return {
                "customer_response": "Would you like me to share your loan sanction letter with you now?",
                "internal_data": {
                    "documentation_stage": "share_document",
                    "documentation_status": documentation_status,
                    "confidence": 0.7
                },
                "next_action": "confirm_document_sharing"
            }
        
        try:
            # Get document path
            document_path = documentation_status.get("document_path")
            
            if not document_path or not os.path.exists(document_path):
                logger.error(f"Document path not found: {document_path}")
                return {
                    "customer_response": "I'm having trouble locating your document. Let me regenerate it for you.",
                    "internal_data": {
                        "documentation_stage": "generate_sanction_letter",
                        "error": "Document path not found",
                        "confidence": 0.5
                    },
                    "next_action": "retry_generation"
                }
            
            # Update documentation status
            documentation_status["document_shared"] = True
            documentation_status["sharing_timestamp"] = datetime.now().isoformat()
            
            # Get document type
            document_type = documentation_status.get("document_type", "sanction_letter")
            
            # Generate appropriate response based on document type
            if document_type == "sanction_letter":
                response = f"I've prepared your loan sanction letter. It contains all the details of your approved loan, including the loan amount, tenure, interest rate, and EMI. The document has been saved at: {document_path}\n\nPlease review it carefully and let me know if you have any questions. Congratulations on your approved loan!"
            elif document_type == "conditional_approval":
                response = f"I've prepared your conditional loan approval letter. It contains the details of your conditionally approved loan and the conditions that need to be fulfilled. The document has been saved at: {document_path}\n\nPlease review it carefully and let me know if you have any questions."
            else:
                response = f"I've prepared your document. It has been saved at: {document_path}\n\nPlease review it and let me know if you have any questions."
            
            return {
                "customer_response": response,
                "internal_data": {
                    "documentation_stage": "documentation_complete",
                    "documentation_status": documentation_status,
                    "document_path": document_path,
                    "confidence": 1.0
                },
                "next_action": "close_conversation"
            }
            
        except Exception as e:
            # Handle unexpected errors
            return {
                "customer_response": "I'm experiencing some technical difficulties sharing your sanction letter. Please bear with me while I resolve this issue.",
                "internal_data": {
                    "documentation_stage": "share_document",
                    "error": str(e),
                    "confidence": 0.4
                },
                "next_action": "retry_document_sharing"
            }
    
    def _handle_conditional_approval(self, customer_id: str, conversation_state: Dict) -> Dict:
        """Handle the conditional approval stage
        
        Args:
            customer_id: The unique identifier for the customer
            conversation_state: The current state of the conversation
            
        Returns:
            Dict containing the conditional approval results and next action
        """
        try:
            # Extract relevant information
            loan_details = conversation_state.get("loan_details", {})
            customer_details = conversation_state.get("customer_details", {})  
            underwriting_status = conversation_state.get("underwriting_status", {})
            
            # Generate conditional approval letter PDF
            pdf_path = self._generate_conditional_approval_letter(
                customer_id, customer_details, loan_details, underwriting_status
            )
            
            if not pdf_path:
                return {
                    "customer_response": "I'm having trouble generating your conditional approval letter. Let me check with our technical team.",
                    "internal_data": {
                        "documentation_stage": "generate_conditional_approval",
                        "error": "Failed to generate PDF",
                        "confidence": 0.5
                    },
                    "next_action": "retry_generation"
                }
            
            # Initialize documentation status
            documentation_status = {
                "document_generated": True,
                "document_type": "conditional_approval",
                "document_path": pdf_path,
                "generation_timestamp": datetime.now().isoformat(),
                "document_shared": False
            }
            
            # Get conditions
            conditions = underwriting_status.get("conditions", ["Additional documentation required"])
            conditions_text = "\n".join([f"- {condition}" for condition in conditions])
            
            # Generate appropriate response
            response = f"I've generated a conditional approval letter for your loan. Your application has been conditionally approved, subject to the following conditions:\n\n{conditions_text}\n\nWould you like me to share the conditional approval letter with you now?"
            
            return {
                "customer_response": response,
                "internal_data": {
                    "documentation_stage": "share_document",
                    "documentation_status": documentation_status,
                    "confidence": 0.9
                },
                "next_action": "confirm_document_sharing"
            }
            
        except Exception as e:
            # Handle unexpected errors
            return {
                "customer_response": "I'm experiencing some technical difficulties generating your conditional approval letter. Please bear with me while I resolve this issue.",
                "internal_data": {
                    "documentation_stage": "generate_conditional_approval",
                    "error": str(e),
                    "confidence": 0.4
                },
                "next_action": "retry_document_generation"
            }
    
    def _check_for_confirmation(self, message: str) -> bool:
        """Check if the message contains a confirmation
        
        Args:
            message: The message to check
            
        Returns:
            Boolean indicating whether the message contains a confirmation
        """
        confirmation_phrases = [
            "yes", "yeah", "yep", "sure", "ok", "okay", "fine", "good", 
            "great", "perfect", "excellent", "please", "proceed", "go ahead",
            "confirm", "agreed", "approve", "accept", "send", "share"
        ]
        
        message = message.lower()
        
        for phrase in confirmation_phrases:
            if phrase in message:
                return True
        
        return False

# Example usage
if __name__ == "__main__":
    # Test the Sanction Letter Generator
    sanction_letter_generator = SanctionLetterGenerator()
    
    # Simulate a conversation for approved loan
    conversation_state = {
        "conversation_history": [],
        "last_customer_message": "Great! My loan is approved.",
        "loan_details": {
            "amount": 300000,
            "tenure": 36,
            "interest_rate": 10.5,
            "purpose": "Home Renovation"
        },
        "customer_details": {
            "name": "Rahul Sharma",
            "address": "123 Main Street, Mumbai - 400001",
            "pre_approved_limit": 500000
        },
        "underwriting_status": {
            "decision": "APPROVED",
            "reason": "Amount within pre-approved limit",
            "calculated_emi": 9735.76,
            "underwriting_complete": True
        }
    }
    
    # Generate sanction letter
    response = sanction_letter_generator.process("TC001", conversation_state)
    print(f"Sanction Letter Generator: {response['customer_response']}")
    
    # Update conversation state with document generation
    conversation_state["conversation_history"].append({
        "role": "agent",
        "message": response["customer_response"]
    })
    conversation_state.update(response["internal_data"])
    
    # Simulate customer confirmation
    conversation_state["last_customer_message"] = "Yes, please share it with me."
    
    # Share document
    response = sanction_letter_generator.process("TC001", conversation_state)
    print(f"\nCustomer: {conversation_state['last_customer_message']}")
    print(f"Sanction Letter Generator: {response['customer_response']}")
    
    # Print next action
    print(f"\nNext action: {response['next_action']}")
    
    # Simulate a conversation for rejected loan
    print("\n\n--- Rejection Scenario ---")
    conversation_state = {
        "conversation_history": [],
        "last_customer_message": "What's the status of my loan application?",
        "loan_details": {
            "amount": 800000,
            "tenure": 36,
            "interest_rate": 10.5,
            "purpose": "Debt Consolidation"
        },
        "customer_details": {
            "name": "Priya Patel",
            "address": "456 Park Avenue, Delhi - 110001",
            "pre_approved_limit": 300000
        },
        "underwriting_status": {
            "decision": "REJECTED",
            "reason": "EMI-to-Income ratio exceeds 50%",
            "calculated_emi": 25828.69,
            "underwriting_complete": True
        }
    }
    
    # Handle rejection
    response = sanction_letter_generator.process("TC002", conversation_state)
    print(f"Customer: {conversation_state['last_customer_message']}")
    print(f"Sanction Letter Generator: {response['customer_response']}")
    
    # Print next action
    print(f"\nNext action: {response['next_action']}")