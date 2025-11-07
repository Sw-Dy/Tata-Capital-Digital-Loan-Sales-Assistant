# Tata Capital Digital Loan Sales Assistant

An end-to-end Agentic AI architecture for a web-based digital loan sales assistant for Tata Capital, designed to increase revenue by autonomously processing personal loan applications from start to sanction.

## Project Overview

This project implements a multi-agent AI system that can engage users from digital ads, understand their needs, and autonomously process personal loan applications. The system includes a Master Agent that orchestrates multiple Worker Agents for KYC verification, credit evaluation, eligibility validation, and sanction letter generation.

### Key Features

- **Natural Conversation Flow**: The system maintains a natural and persuasive conversation flow similar to a human sales representative.
- **Autonomous Processing**: Handles each stage of the loan process from welcoming the customer to generating a sanction letter.
- **Multi-Agent Architecture**: Uses specialized agents for different tasks, coordinated by a Master Agent.
- **Mock API Integration**: Includes synthetic but realistic data and mock APIs for demonstration purposes.
- **Edge Case Handling**: Handles various scenarios including credit rejections, missing salary slips, API timeouts, and loan modifications.

## System Architecture

The system is built on a multi-agent architecture with the following components:

### Master Agent

The central orchestrator that manages the customer conversation, understands intent, handles context, and delegates subtasks to Worker Agents.

### Worker Agents

1. **Sales Agent**: Explores customer needs, retrieves offers, and negotiates loan terms.
2. **Verification Agent**: Checks KYC details using the CRM API and flags inconsistencies.
3. **Underwriting Agent**: Fetches credit scores and applies eligibility rules to make approval decisions.
4. **Sanction Letter Generator**: Produces professional PDF letters for approvals and empathetic responses for rejections.

### Mock APIs

1. **Offer Mart API**: Provides personalized loan offers.
2. **CRM API**: Provides customer details and KYC status.
3. **Credit Bureau API**: Provides credit scores and history.
4. **Document Storage**: Handles document uploads and retrieval.

## Project Structure

```
├── architecture_overview.md     # Detailed architecture documentation
├── conversation_flows.md        # Example conversation scenarios
├── diagrams/                    # Architecture diagrams
│   └── architecture_diagram.svg # Visual representation of the system
├── implementation/              # Core implementation files
│   ├── master_agent.py          # Master Agent implementation
│   ├── sales_agent.py           # Sales Agent implementation
│   ├── verification_agent.py    # Verification Agent implementation
│   ├── underwriting_agent.py    # Underwriting Agent implementation
│   ├── sanction_letter_generator.py # Sanction Letter Generator implementation
│   ├── mock_apis.py             # Mock API implementations
│   └── mock_data.py             # Mock data structures
├── main.py                      # Main entry point for the application
├── master_agent_design.md       # Detailed design of the Master Agent
├── worker_agents_design.md      # Detailed design of the Worker Agents
└── README.md                    # This file
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required packages (install via `pip install -r requirements.txt`):
  - langchain
  - langgraph
  - reportlab (for PDF generation)
  - fastapi (for web interface)
  - uvicorn (for serving the API)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Demo

To run the demonstration of the Tata Capital Digital Loan Sales Assistant:

```
python main.py
```

This will simulate three conversation scenarios:
1. Successful Loan Application (Pre-approved)
2. Loan Application Requiring Salary Slip
3. Loan Application Rejection

## Implementation Details

### Conversation Flow

The overall orchestration flow begins with the customer landing on the chat interface. The Master Agent welcomes them and triggers the following sequence:

1. The Sales Agent collects information about loan amount, tenure, and purpose.
2. The Verification Agent validates KYC details.
3. The Underwriting Agent makes an approval decision based on credit score and eligibility rules.
4. The Sanction Letter Generator produces and shares the document link or provides a rejection message.
5. The Master Agent closes the session, thanking the customer and logging the transaction.

### Eligibility Rules

The system applies the following eligibility rules:

- If the requested amount is within the pre-approved limit, the loan is approved instantly.
- If within twice the limit, the agent requests a salary slip and approves only if the EMI is less than or equal to 50% of the salary.
- If the requested amount exceeds twice the limit or the credit score is below 700, the loan is rejected.

### Error Handling

The system handles various edge cases including:

- Credit rejections with personalized messages
- Missing salary slips with appropriate prompts
- API timeouts with retry mechanisms
- User-initiated loan modifications

## Future Enhancements

- Integration with real APIs
- Web interface implementation using Streamlit or React
- Database integration for persistent storage
- Enhanced security features
- Additional loan products and features

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Acknowledgments

- Tata Capital for the problem statement
- LangGraph and LangChain for the orchestration framework
- ReportLab for PDF generation capabilities