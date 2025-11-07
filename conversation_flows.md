# Conversation Flows for Tata Capital Digital Loan Sales Assistant

This document outlines example conversation flows between the customer and the Agentic AI system, demonstrating how the Master Agent and Worker Agents collaborate to process loan applications.

## Scenario 1: Successful Loan Application (Pre-approved)

### Initial Greeting and Intent Capture

**Master Agent**: "Welcome to Tata Capital! I'm your Smart Assistant. How may I help you today?"

**Customer**: "I'm interested in getting a personal loan."

**Master Agent**: "Great! I'd be happy to help you explore personal loan options with Tata Capital. May I know your name and mobile number to get started?"

**Customer**: "My name is Rajesh Kumar and my mobile number is 9876543210."

### Sales Exploration (Sales Agent)

**Master Agent** → **Sales Agent**: *[Internal] Verify customer and explore loan needs*

**Sales Agent**: "Thank you, Mr. Kumar. I can see you're already a valued customer with Tata Capital. I'd like to understand your loan requirements better. What amount are you looking for, and what would be the purpose of this loan?"

**Customer**: "I need about 4 lakhs for home renovation."

**Sales Agent**: "Thank you for sharing that. For a home renovation loan of ₹4,00,000, we have several options. Based on your profile, you're eligible for our Quick Personal Loan with an interest rate of 10.25%. Would you prefer a shorter tenure with higher EMI or a longer tenure with lower EMI?"

**Customer**: "I'd prefer a 3-year tenure."

**Sales Agent**: "Excellent choice. With a 3-year tenure for ₹4,00,000, your EMI would be approximately ₹12,900 per month. This is well within your affordability range based on your income. Would you like to proceed with this option?"

**Customer**: "Yes, that sounds good."

**Sales Agent** → **Master Agent**: *[Internal] Customer has selected a 3-year personal loan of ₹4,00,000 at 10.25% interest rate. Customer profile indicates pre-approved status for this amount.*

### Verification Process (Verification Agent)

**Master Agent** → **Verification Agent**: *[Internal] Verify customer KYC details*

**Verification Agent**: "Thank you for choosing to proceed, Mr. Kumar. I need to verify a few details. Is your current address still Flat 301, Sunshine Apartments, Andheri West, Mumbai - 400053?"

**Customer**: "Yes, that's correct."

**Verification Agent**: "And you're still working as a Software Engineer at TCS?"

**Customer**: "Yes, that's right."

**Verification Agent** → **Master Agent**: *[Internal] KYC verification successful. Address and employment details confirmed.*

### Underwriting Process (Underwriting Agent)

**Master Agent** → **Underwriting Agent**: *[Internal] Evaluate loan eligibility*

**Underwriting Agent**: "Mr. Kumar, I'm pleased to inform you that based on your excellent credit score of 780 and your relationship with Tata Capital, your loan application for ₹4,00,000 has been pre-approved. This means we can process your application without requiring additional documentation."

**Underwriting Agent** → **Master Agent**: *[Internal] Loan approved. Customer has a credit score of 780, requested amount is within pre-approved limit of ₹5,00,000. Decision: APPROVED. EMI: ₹12,900. Tenure: 36 months. Interest Rate: 10.25%.*

### Documentation (Sanction Letter Generator)

**Master Agent** → **Sanction Letter Generator**: *[Internal] Generate sanction letter*

**Sanction Letter Generator** → **Master Agent**: *[Internal] Sanction letter generated successfully. Document ID: SL-TC001-12345*

**Master Agent**: "Congratulations, Mr. Kumar! Your loan of ₹4,00,000 has been approved. I've generated your sanction letter which contains all the details including your EMI of ₹12,900 and interest rate of 10.25%. You can download it from the link I've just shared. The funds will be disbursed to your registered bank account within 24 hours."

### Closure

**Master Agent**: "Is there anything else you'd like to know about your approved loan?"

**Customer**: "No, that's all. Thank you!"

**Master Agent**: "Thank you for choosing Tata Capital for your personal loan needs. If you have any questions in the future, feel free to reach out. Have a great day!"

## Scenario 2: Loan Application Requiring Salary Slip

### Initial Greeting and Intent Capture

**Master Agent**: "Welcome to Tata Capital! I'm your Smart Assistant. How may I help you today?"

**Customer**: "Hi, I want to apply for a personal loan."

**Master Agent**: "I'd be happy to help you with a personal loan application. May I know your name and mobile number to get started?"

**Customer**: "I'm Priya Sharma, my number is 9876543211."

### Sales Exploration (Sales Agent)

**Master Agent** → **Sales Agent**: *[Internal] Verify customer and explore loan needs*

**Sales Agent**: "Thank you, Ms. Sharma. I can see you're already a valued customer with Tata Capital. What loan amount are you looking for, and what would be the purpose?"

**Customer**: "I need 10 lakhs for my sister's wedding."

**Sales Agent**: "Thank you for sharing that. For a wedding loan of ₹10,00,000, we have our Premium Personal Loan option. Based on your profile, the interest rate would be around 9.75%. Would you prefer a 3, 4, or 5-year tenure?"

**Customer**: "I think 4 years would work best for me."

**Sales Agent**: "With a 4-year tenure for ₹10,00,000 at 9.75%, your EMI would be approximately ₹25,300 per month. Would you like to proceed with this option?"

**Customer**: "Yes, please."

**Sales Agent** → **Master Agent**: *[Internal] Customer has selected a 4-year personal loan of ₹10,00,000 at 9.75% interest rate. Amount exceeds pre-approved limit of ₹6,00,000 but is within twice the limit.*

### Verification Process (Verification Agent)

**Master Agent** → **Verification Agent**: *[Internal] Verify customer KYC details*

**Verification Agent**: "Thank you for choosing to proceed, Ms. Sharma. I need to verify a few details. Is your current address still House No. 45, Block C, Greater Kailash, New Delhi - 110048?"

**Customer**: "Yes, that's correct."

**Verification Agent**: "And you're still working as a Marketing Manager at Reliance Retail?"

**Customer**: "Yes, that's right."

**Verification Agent** → **Master Agent**: *[Internal] KYC verification successful. Address and employment details confirmed.*

### Underwriting Process (Underwriting Agent)

**Master Agent** → **Underwriting Agent**: *[Internal] Evaluate loan eligibility*

**Underwriting Agent**: "Ms. Sharma, your credit score of 820 is excellent, which is great news. However, since your requested loan amount of ₹10,00,000 exceeds your pre-approved limit of ₹6,00,000, we'll need to verify your income. Could you please upload your latest salary slip so we can complete the assessment?"

**Customer**: "Sure, I'll upload it now." *[Customer uploads salary slip]*

**Underwriting Agent**: "Thank you for uploading your salary slip. I can see your monthly income is ₹70,000. For the requested loan amount, your EMI would be ₹25,300, which is 36% of your monthly income. This is within our acceptable limit of 50%."

**Underwriting Agent** → **Master Agent**: *[Internal] Salary slip verified. Monthly income: ₹70,000. EMI-to-Income ratio: 36%. Decision: APPROVED. EMI: ₹25,300. Tenure: 48 months. Interest Rate: 9.75%.*

### Documentation (Sanction Letter Generator)

**Master Agent** → **Sanction Letter Generator**: *[Internal] Generate sanction letter*

**Sanction Letter Generator** → **Master Agent**: *[Internal] Sanction letter generated successfully. Document ID: SL-TC002-12346*

**Master Agent**: "Congratulations, Ms. Sharma! Your loan of ₹10,00,000 has been approved. I've generated your sanction letter which contains all the details including your EMI of ₹25,300 and interest rate of 9.75%. You can download it from the link I've just shared. The funds will be disbursed to your registered bank account within 24 hours."

### Closure

**Master Agent**: "Is there anything else you'd like to know about your approved loan?"

**Customer**: "What documents will I need to sign?"

**Master Agent**: "You'll receive an email with digital loan agreement documents that you can sign electronically using Aadhaar-based OTP verification. No physical documents are required. Once signed, the loan will be processed immediately."

**Customer**: "That sounds convenient. Thank you!"

**Master Agent**: "Thank you for choosing Tata Capital for your personal loan needs. If you have any questions in the future, feel free to reach out. Have a great day!"

## Scenario 3: Loan Application Rejection

### Initial Greeting and Intent Capture

**Master Agent**: "Welcome to Tata Capital! I'm your Smart Assistant. How may I help you today?"

**Customer**: "I need a personal loan urgently."

**Master Agent**: "I'd be happy to help you with a personal loan application. May I know your name and mobile number to get started?"

**Customer**: "Rahul Verma, 9876543218."

### Sales Exploration (Sales Agent)

**Master Agent** → **Sales Agent**: *[Internal] Verify customer and explore loan needs*

**Sales Agent**: "Thank you, Mr. Verma. I can see you're already a customer with Tata Capital. What loan amount are you looking for, and what would be the purpose?"

**Customer**: "I need 8 lakhs for debt consolidation."

**Sales Agent**: "Thank you for sharing that. For a debt consolidation loan of ₹8,00,000, we have our Quick Personal Loan option. Based on your profile, the interest rate would be around 11%. Would you prefer a 3, 4, or 5-year tenure?"

**Customer**: "3 years would be good."

**Sales Agent**: "With a 3-year tenure for ₹8,00,000 at 11%, your EMI would be approximately ₹26,200 per month. Would you like to proceed with this option?"

**Customer**: "Yes, that works for me."

**Sales Agent** → **Master Agent**: *[Internal] Customer has selected a 3-year personal loan of ₹8,00,000 at 11% interest rate. Amount exceeds pre-approved limit of ₹3,00,000 and is more than twice the limit.*

### Verification Process (Verification Agent)

**Master Agent** → **Verification Agent**: *[Internal] Verify customer KYC details*

**Verification Agent**: "Thank you for choosing to proceed, Mr. Verma. I need to verify a few details. Is your current address still 78, Gomti Nagar, Lucknow - 226010?"

**Customer**: "Yes, that's correct."

**Verification Agent**: "And you're still working as a Government Employee at UP State Government?"

**Customer**: "Yes, that's right."

**Verification Agent** → **Master Agent**: *[Internal] KYC verification successful. Address and employment details confirmed.*

### Underwriting Process (Underwriting Agent)

**Master Agent** → **Underwriting Agent**: *[Internal] Evaluate loan eligibility*

**Underwriting Agent**: "Mr. Verma, since your requested loan amount of ₹8,00,000 exceeds your pre-approved limit of ₹3,00,000, we'll need to verify your income. Could you please upload your latest salary slip?"

**Customer**: "Sure, here it is." *[Customer uploads salary slip]*

**Underwriting Agent**: "Thank you for uploading your salary slip. I can see your monthly income is ₹55,000. For the requested loan amount, your EMI would be ₹26,200, which is approximately 48% of your monthly income. Additionally, I notice you have an existing two-wheeler loan with an EMI of ₹4,000."

**Underwriting Agent**: "When we consider your existing obligations, the total EMI burden would be ₹30,200, which is about 55% of your monthly income. This exceeds our maximum allowable limit of 50%. Additionally, your credit score of 720 is slightly below our threshold for this loan amount."

**Underwriting Agent** → **Master Agent**: *[Internal] Salary slip verified. Monthly income: ₹55,000. Existing EMI: ₹4,000. New EMI: ₹26,200. Total EMI-to-Income ratio: 55%. Credit score: 720. Decision: REJECTED. Reason: EMI-to-Income ratio exceeds 50% and credit score below threshold for requested amount.*

### Rejection Communication

**Master Agent**: "Mr. Verma, thank you for your interest in a personal loan with Tata Capital. After careful evaluation of your application, I regret to inform you that we're unable to approve the loan amount of ₹8,00,000 at this time."

**Master Agent**: "This decision is based on our assessment that the resulting EMI would be approximately 55% of your monthly income when combined with your existing obligations, which exceeds our maximum allowable limit of 50%. We have this policy in place to ensure that our customers maintain a healthy financial balance."

**Master Agent**: "However, I'd like to offer you an alternative. Based on your profile, we can approve a loan of ₹3,00,000 with a 3-year tenure at 11% interest rate. This would result in an EMI of approximately ₹9,800, which would be more aligned with your current financial situation. Would you be interested in this option?"

**Customer**: "That's disappointing, but I understand. Let me think about the alternative offer."

### Closure

**Master Agent**: "I understand your disappointment, Mr. Verma. The alternative offer will remain valid for the next 7 days should you decide to proceed. If your financial situation changes in the future, we'd be happy to reassess your application. Is there anything else I can assist you with today?"

**Customer**: "No, that's all for now. Thank you."

**Master Agent**: "Thank you for considering Tata Capital for your financial needs. If you have any questions or would like to discuss the alternative offer, please don't hesitate to reach out. Have a good day!"

## Scenario 4: API Timeout Edge Case

### Initial Greeting and Intent Capture

**Master Agent**: "Welcome to Tata Capital! I'm your Smart Assistant. How may I help you today?"

**Customer**: "I want to check if I'm eligible for a personal loan."

**Master Agent**: "I'd be happy to help you check your loan eligibility. May I know your name and mobile number to get started?"

**Customer**: "Vikram Singh, 9876543214."

### Sales Exploration (Sales Agent)

**Master Agent** → **Sales Agent**: *[Internal] Verify customer and explore loan needs*

**Sales Agent**: "Thank you, Mr. Singh. I can see you're already a valued customer with Tata Capital. What loan amount are you interested in, and what would be the purpose?"

**Customer**: "I'm thinking of 6 lakhs for home renovation."

**Sales Agent**: "Thank you for sharing that. For a home renovation loan of ₹6,00,000, we have our Quick Personal Loan option. Based on your profile, the interest rate would be around 10.5%. Would you prefer a 3, 4, or 5-year tenure?"

**Customer**: "4 years sounds good."

**Sales Agent** → **Master Agent**: *[Internal] Customer has selected a 4-year personal loan of ₹6,00,000 at 10.5% interest rate.*

### Verification Process (Verification Agent)

**Master Agent** → **Verification Agent**: *[Internal] Verify customer KYC details*

**Verification Agent**: "Thank you for choosing to proceed, Mr. Singh. I need to verify a few details. Is your current address still Flat 205, Tech Park Residency, Whitefield, Bangalore - 560066?"

**Customer**: "Yes, that's correct."

**Verification Agent**: "And you're still working as a Product Manager at Flipkart?"

**Customer**: "Yes, that's right."

**Verification Agent** → **Master Agent**: *[Internal] KYC verification successful. Address and employment details confirmed.*

### Underwriting Process (Underwriting Agent) - API Timeout

**Master Agent** → **Underwriting Agent**: *[Internal] Evaluate loan eligibility*

**Underwriting Agent** → **Master Agent**: *[Internal] Error: Credit Bureau API timeout after multiple retries.*

**Master Agent**: "Mr. Singh, I apologize for the inconvenience, but we're currently experiencing some technical difficulties while accessing your credit information. This is a temporary issue on our end."

**Master Agent**: "We have two options: we can either try again in a few minutes, or we can schedule a callback from our loan specialist who can assist you further once our systems are back to normal. What would you prefer?"

**Customer**: "Let's try again in a few minutes."

**Master Agent**: "Thank you for your patience. I'll try accessing your information again."

### Retry Underwriting Process

**Master Agent** → **Underwriting Agent**: *[Internal] Retry evaluating loan eligibility*

**Underwriting Agent**: "Mr. Singh, I've successfully accessed your credit information now. I can see you have an excellent credit score of 790. Since your requested loan amount of ₹6,00,000 is within your pre-approved limit of ₹7,00,000, I'm pleased to inform you that your loan has been approved."

**Underwriting Agent** → **Master Agent**: *[Internal] Loan approved. Customer has a credit score of 790, requested amount is within pre-approved limit of ₹7,00,000. Decision: APPROVED. EMI: ₹15,200. Tenure: 48 months. Interest Rate: 10.5%.*

### Documentation (Sanction Letter Generator)

**Master Agent** → **Sanction Letter Generator**: *[Internal] Generate sanction letter*

**Sanction Letter Generator** → **Master Agent**: *[Internal] Sanction letter generated successfully. Document ID: SL-TC005-12349*

**Master Agent**: "Congratulations, Mr. Singh! Your loan of ₹6,00,000 has been approved. I've generated your sanction letter which contains all the details including your EMI of ₹15,200 and interest rate of 10.5%. You can download it from the link I've just shared. The funds will be disbursed to your registered bank account within 24 hours."

### Closure

**Master Agent**: "Thank you for your patience during the technical issue earlier. Is there anything else you'd like to know about your approved loan?"

**Customer**: "No, that's all. Thanks for resolving it quickly."

**Master Agent**: "Thank you for choosing Tata Capital for your personal loan needs. If you have any questions in the future, feel free to reach out. Have a great day!"

## Scenario 5: Loan Modification Request

### Initial Greeting and Intent Capture

**Master Agent**: "Welcome to Tata Capital! I'm your Smart Assistant. How may I help you today?"

**Customer**: "I want to apply for a personal loan."

**Master Agent**: "I'd be happy to help you with a personal loan application. May I know your name and mobile number to get started?"

**Customer**: "Meera Joshi, 9876543215."

### Sales Exploration (Sales Agent)

**Master Agent** → **Sales Agent**: *[Internal] Verify customer and explore loan needs*

**Sales Agent**: "Thank you, Ms. Joshi. I can see you're already a valued customer with Tata Capital. What loan amount are you looking for, and what would be the purpose?"

**Customer**: "I need 3 lakhs for a vacation."

**Sales Agent**: "Thank you for sharing that. For a vacation loan of ₹3,00,000, we have our Quick Personal Loan option. Based on your profile, the interest rate would be around 10.75%. Would you prefer a 2, 3, or 4-year tenure?"

**Customer**: "3 years would be good."

**Sales Agent**: "With a 3-year tenure for ₹3,00,000 at 10.75%, your EMI would be approximately ₹9,800 per month. Would you like to proceed with this option?"

**Customer**: "Actually, I think I might need 4 lakhs instead. Can we check that?"

**Sales Agent**: "Of course, we can adjust the loan amount. For a vacation loan of ₹4,00,000 with a 3-year tenure at 10.75%, your EMI would be approximately ₹13,100 per month. Would this work better for your needs?"

**Customer**: "Yes, and can we check what the EMI would be for a 4-year tenure instead?"

**Sales Agent**: "For a ₹4,00,000 loan with a 4-year tenure at 10.75%, your EMI would be lower at approximately ₹10,300 per month. Would you prefer this option with the longer tenure and lower monthly payment?"

**Customer**: "Yes, the 4-year option sounds better."

**Sales Agent** → **Master Agent**: *[Internal] Customer has selected a 4-year personal loan of ₹4,00,000 at 10.75% interest rate. Amount is within pre-approved limit of ₹4,00,000.*

### Verification Process (Verification Agent)

**Master Agent** → **Verification Agent**: *[Internal] Verify customer KYC details*

**Verification Agent**: "Thank you for choosing to proceed, Ms. Joshi. I need to verify a few details. Is your current address still 33, Koregaon Park, Pune - 411001?"

**Customer**: "Yes, that's correct."

**Verification Agent**: "And you're still working as an HR Manager at Infosys?"

**Customer**: "Yes, that's right."

**Verification Agent** → **Master Agent**: *[Internal] KYC verification successful. Address and employment details confirmed.*

### Underwriting Process (Underwriting Agent)

**Master Agent** → **Underwriting Agent**: *[Internal] Evaluate loan eligibility*

**Underwriting Agent**: "Ms. Joshi, I'm pleased to inform you that based on your excellent credit score of 760 and your relationship with Tata Capital, your loan application for ₹4,00,000 has been pre-approved. This means we can process your application without requiring additional documentation."

**Underwriting Agent** → **Master Agent**: *[Internal] Loan approved. Customer has a credit score of 760, requested amount is within pre-approved limit of ₹4,00,000. Decision: APPROVED. EMI: ₹10,300. Tenure: 48 months. Interest Rate: 10.75%.*

### Documentation (Sanction Letter Generator)

**Master Agent** → **Sanction Letter Generator**: *[Internal] Generate sanction letter*

**Sanction Letter Generator** → **Master Agent**: *[Internal] Sanction letter generated successfully. Document ID: SL-TC006-12350*

**Master Agent**: "Congratulations, Ms. Joshi! Your loan of ₹4,00,000 has been approved. I've generated your sanction letter which contains all the details including your EMI of ₹10,300 and interest rate of 10.75%. You can download it from the link I've just shared. The funds will be disbursed to your registered bank account within 24 hours."

**Customer**: "Actually, I've been thinking, and I'd like to go back to the 3-year option. Is that still possible?"

**Master Agent**: "Certainly, Ms. Joshi. We can modify your loan application before final processing. Let me recalculate the details for a 3-year tenure."

**Master Agent** → **Underwriting Agent**: *[Internal] Modify loan application: Change tenure from 48 months to 36 months, keeping loan amount at ₹4,00,000 and interest rate at 10.75%.*

**Underwriting Agent** → **Master Agent**: *[Internal] Loan modification approved. New EMI: ₹13,100. New Tenure: 36 months. Interest Rate unchanged at 10.75%.*

**Master Agent** → **Sanction Letter Generator**: *[Internal] Regenerate sanction letter with updated terms*

**Sanction Letter Generator** → **Master Agent**: *[Internal] Updated sanction letter generated successfully. Document ID: SL-TC006-12351*

**Master Agent**: "I've updated your loan application to a 3-year tenure as requested. Your new EMI will be ₹13,100 per month. I've generated a revised sanction letter with the updated details, which you can download from the link I've just shared. The funds will still be disbursed within 24 hours."

### Closure

**Master Agent**: "Is there anything else you'd like to modify or any questions about your approved loan?"

**Customer**: "No, that's perfect. Thank you for being so flexible."

**Master Agent**: "You're welcome, Ms. Joshi. We're always happy to accommodate changes to ensure you get the loan that best suits your needs. Thank you for choosing Tata Capital for your personal loan. If you have any questions in the future, feel free to reach out. Have a great day!"