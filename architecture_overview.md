# Tata Capital Digital Loan Sales Assistant - Agentic AI Architecture

## 1. System Overview

This document outlines the architecture for an end-to-end Agentic AI system designed to serve as a digital loan sales assistant for Tata Capital. The system uses a multi-agent approach to autonomously process personal loan applications from initial customer contact through to loan sanction or rejection.

## 2. Multi-Agent Architecture

![Architecture Diagram](./diagrams/architecture_diagram.svg)

### 2.1 Agent Structure

#### Master Agent
- **Role**: Central orchestrator that manages the overall conversation flow and delegates tasks to specialized Worker Agents
- **Responsibilities**:
  - Maintain conversation context and customer state
  - Detect customer intent
  - Route control to appropriate Worker Agents
  - Integrate responses from Worker Agents into a coherent conversation
  - Make decisions based on business rules and agent outputs
  - Ensure compliance with financial regulations

#### Worker Agents

1. **Sales Agent**
   - **Role**: Handles customer engagement and loan product exploration
   - **Responsibilities**:
     - Understand customer needs through questioning
     - Retrieve suitable offers from Offer Mart API
     - Negotiate loan terms (amount, tenure, interest rate)
     - Create intent summary for Master Agent

2. **Verification Agent**
   - **Role**: Validates customer identity and KYC details
   - **Responsibilities**:
     - Verify phone number, address, and other KYC information
     - Cross-check details with CRM API
     - Flag inconsistencies or missing information
     - Request additional verification if needed

3. **Underwriting Agent**
   - **Role**: Evaluates loan eligibility and makes approval decisions
   - **Responsibilities**:
     - Fetch credit score from Credit Bureau API
     - Apply eligibility rules based on pre-approved limits
     - Request and analyze salary slips when needed
     - Calculate EMI and validate against salary
     - Make final approval/rejection decision
     - Generate structured decision summary

4. **Sanction Letter Generator**
   - **Role**: Creates official documentation for approved loans
   - **Responsibilities**:
     - Generate professional PDF sanction letters
     - Include all loan details (amount, tenure, interest rate, EMI schedule)
     - Format rejection messages with appropriate empathy
     - Provide document links to Master Agent

### 2.2 System Data Flow

1. **Customer Initiation**
   - Customer lands on chat interface from digital ad
   - Master Agent welcomes and initiates conversation

2. **Sales Process**
   - Master Agent triggers Sales Agent
   - Sales Agent collects loan requirements
   - Sales Agent retrieves offers and negotiates terms
   - Sales Agent returns intent summary to Master Agent

3. **Verification Process**
   - Master Agent triggers Verification Agent
   - Verification Agent validates KYC details via CRM API
   - Verification Agent returns validation results to Master Agent

4. **Underwriting Process**
   - Master Agent triggers Underwriting Agent
   - Underwriting Agent fetches credit score via Credit Bureau API
   - Underwriting Agent applies eligibility rules
   - Underwriting Agent requests salary slip if needed
   - Underwriting Agent returns decision summary to Master Agent

5. **Documentation Process**
   - For approvals: Master Agent triggers Sanction Letter Generator
   - Sanction Letter Generator creates PDF document
   - Sanction Letter Generator returns document link to Master Agent
   - For rejections: Master Agent formats empathetic rejection message

6. **Session Closure**
   - Master Agent thanks customer and closes session
   - Transaction details are logged for future reference

## 3. Technical Implementation

### 3.1 Orchestration Framework

The system will use LangGraph for agent orchestration, allowing for:
- Complex conversation state management
- Conditional routing between agents
- Parallel processing of tasks when appropriate
- Persistent memory across conversation turns

### 3.2 Agent Communication Protocol

Agents will communicate using structured JSON messages containing:
- Task details and parameters
- Results and decision data
- Conversation context
- Customer information
- Next action recommendations

### 3.3 Mock API Integration

The system will integrate with three primary mock APIs:
1. **Offer Mart API**: Provides loan product details and personalized offers
2. **CRM API**: Contains customer profile information for verification
3. **Credit Bureau API**: Provides credit scores and history

### 3.4 Document Generation

The Sanction Letter Generator will use ReportLab to create professional PDF documents with:
- Tata Capital branding and formatting
- Complete loan details
- EMI schedule
- Terms and conditions
- Digital signature

## 4. Edge Case Handling

- **Credit Rejections**: Empathetic messaging with alternative suggestions
- **Missing Documents**: Clear instructions for uploading required documents
- **API Timeouts**: Graceful degradation with appropriate customer messaging
- **Loan Modifications**: Support for adjusting terms during the process
- **Conversation Interruptions**: State persistence for resuming conversations

## 5. Compliance and Security

- All conversations follow financial regulatory guidelines
- Personal data handling complies with privacy regulations
- Clear disclosure of AI assistant nature
- Transparent explanation of decision factors
- Secure document handling and transmission

## 6. Performance Metrics

- Conversion rate from chat initiation to application completion
- Average time to loan decision
- Customer satisfaction scores
- Error rates in verification and underwriting
- Successful API integration percentage