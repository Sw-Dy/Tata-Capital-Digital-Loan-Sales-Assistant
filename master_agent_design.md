# Master Agent Design

## 1. Overview

The Master Agent serves as the central orchestrator for the Tata Capital Digital Loan Sales Assistant. It manages the overall conversation flow, maintains context, and delegates specialized tasks to Worker Agents while ensuring a coherent and natural customer experience.

## 2. Core Responsibilities

- **Conversation Management**: Maintain the overall dialogue with the customer
- **Context Tracking**: Store and update customer information and conversation state
- **Intent Detection**: Identify customer needs and objectives
- **Task Delegation**: Assign specific tasks to appropriate Worker Agents
- **Response Integration**: Combine outputs from Worker Agents into coherent responses
- **Decision Making**: Apply business rules to determine next steps
- **Compliance Enforcement**: Ensure all interactions follow financial regulations

## 3. State Management

### 3.1 Conversation State

```python
class ConversationState:
    def __init__(self):
        self.customer_id = None
        self.conversation_id = str(uuid.uuid4())
        self.conversation_history = []
        self.current_stage = "GREETING"
        self.customer_intent = None
        self.customer_profile = {}
        self.loan_details = {}
        self.verification_status = {}
        self.underwriting_result = {}
        self.document_links = {}
        self.active_agent = None
```

### 3.2 Stage Transitions

The Master Agent manages the following conversation stages:

1. **GREETING**: Initial welcome and customer identification
2. **INTENT_CAPTURE**: Understanding customer's loan requirements
3. **SALES_EXPLORATION**: Exploring loan options and terms
4. **VERIFICATION**: Validating customer identity and details
5. **UNDERWRITING**: Evaluating loan eligibility
6. **DOCUMENTATION**: Generating and sharing official documents
7. **CLOSURE**: Concluding the conversation

## 4. Orchestration Logic

### 4.1 Agent Selection Logic

```python
def select_next_agent(self, conversation_state):
    current_stage = conversation_state.current_stage
    
    if current_stage == "GREETING":
        # After greeting, move to intent capture
        return None, "INTENT_CAPTURE"
        
    elif current_stage == "INTENT_CAPTURE":
        # After capturing intent, delegate to Sales Agent
        return "SALES_AGENT", "SALES_EXPLORATION"
        
    elif current_stage == "SALES_EXPLORATION":
        # After sales exploration, move to verification
        if conversation_state.loan_details.get("amount") and \
           conversation_state.loan_details.get("tenure"):
            return "VERIFICATION_AGENT", "VERIFICATION"
        else:
            # Continue with sales if loan details are incomplete
            return "SALES_AGENT", "SALES_EXPLORATION"
            
    elif current_stage == "VERIFICATION":
        # After verification, move to underwriting
        if conversation_state.verification_status.get("verified", False):
            return "UNDERWRITING_AGENT", "UNDERWRITING"
        else:
            # Continue with verification if not verified
            return "VERIFICATION_AGENT", "VERIFICATION"
            
    elif current_stage == "UNDERWRITING":
        # After underwriting, move to documentation if approved
        if conversation_state.underwriting_result.get("decision") == "APPROVED":
            return "SANCTION_LETTER_GENERATOR", "DOCUMENTATION"
        else:
            # Move to closure if rejected
            return None, "CLOSURE"
            
    elif current_stage == "DOCUMENTATION":
        # After documentation, move to closure
        return None, "CLOSURE"
        
    elif current_stage == "CLOSURE":
        # End of conversation
        return None, None
```

### 4.2 Task Delegation

```python
def delegate_task(self, agent_name, conversation_state):
    if agent_name == "SALES_AGENT":
        return self.delegate_to_sales_agent(conversation_state)
        
    elif agent_name == "VERIFICATION_AGENT":
        return self.delegate_to_verification_agent(conversation_state)
        
    elif agent_name == "UNDERWRITING_AGENT":
        return self.delegate_to_underwriting_agent(conversation_state)
        
    elif agent_name == "SANCTION_LETTER_GENERATOR":
        return self.delegate_to_sanction_letter_generator(conversation_state)
        
    else:
        return None
```

## 5. Agent Communication Protocol

### 5.1 Task Assignment Format

```json
{
  "task_id": "uuid-string",
  "agent_name": "AGENT_NAME",
  "task_type": "TASK_TYPE",
  "conversation_context": {
    "conversation_id": "uuid-string",
    "customer_id": "customer-id",
    "conversation_history": ["array of previous messages"]
  },
  "customer_profile": {
    "name": "Customer Name",
    "age": 35,
    "city": "Mumbai",
    "phone": "+91XXXXXXXXXX"
  },
  "task_parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### 5.2 Task Response Format

```json
{
  "task_id": "uuid-string",
  "agent_name": "AGENT_NAME",
  "task_type": "TASK_TYPE",
  "status": "COMPLETED",
  "result": {
    "customer_response": "Message to be shown to customer",
    "internal_data": {
      "key1": "value1",
      "key2": "value2"
    },
    "next_action": "RECOMMENDED_NEXT_ACTION"
  }
}
```

## 6. LLM Prompting Strategy

### 6.1 System Prompt

```
You are the Master Agent for Tata Capital's Digital Loan Sales Assistant. Your role is to orchestrate a natural, helpful conversation with customers seeking personal loans. You will:

1. Maintain a friendly, professional tone representing Tata Capital
2. Detect customer intent and needs
3. Delegate specialized tasks to Worker Agents
4. Integrate responses from Worker Agents into a coherent conversation
5. Apply business rules to determine next steps
6. Ensure all interactions comply with financial regulations

You have access to the following Worker Agents:
- Sales Agent: Explores loan options and negotiates terms
- Verification Agent: Validates customer identity and details
- Underwriting Agent: Evaluates loan eligibility
- Sanction Letter Generator: Creates official documentation

Your persona is that of a trustworthy Tata Capital Smart Assistant who helps users transparently through the loan application process.
```

### 6.2 Few-Shot Examples

The Master Agent will be provided with examples of successful conversations to guide its responses, including:

- Greeting and intent detection
- Smooth transitions between agents
- Handling customer questions
- Managing conversation context
- Appropriate closure of conversations

## 7. Implementation with LangGraph

### 7.1 Node Structure

```python
from langgraph.graph import StateGraph

# Define the state schema
class AgentState(TypedDict):
    conversation_state: ConversationState
    messages: list[dict]
    next_agent: str

# Create nodes for each agent and processing step
def master_agent(state):
    # Master agent processing logic
    return {"conversation_state": updated_state, "next_agent": next_agent}

def sales_agent(state):
    # Sales agent processing logic
    return {"messages": [sales_response]}

def verification_agent(state):
    # Verification agent processing logic
    return {"messages": [verification_response]}

def underwriting_agent(state):
    # Underwriting agent processing logic
    return {"messages": [underwriting_response]}

def sanction_letter_generator(state):
    # Document generation logic
    return {"messages": [documentation_response]}
```

### 7.2 Graph Definition

```python
# Create the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("master_agent", master_agent)
workflow.add_node("sales_agent", sales_agent)
workflow.add_node("verification_agent", verification_agent)
workflow.add_node("underwriting_agent", underwriting_agent)
workflow.add_node("sanction_letter_generator", sanction_letter_generator)

# Define edges
workflow.add_edge("master_agent", "sales_agent")
workflow.add_edge("master_agent", "verification_agent")
workflow.add_edge("master_agent", "underwriting_agent")
workflow.add_edge("master_agent", "sanction_letter_generator")
workflow.add_edge("sales_agent", "master_agent")
workflow.add_edge("verification_agent", "master_agent")
workflow.add_edge("underwriting_agent", "master_agent")
workflow.add_edge("sanction_letter_generator", "master_agent")

# Define conditional routing
def route_to_next_agent(state):
    return state["next_agent"]

workflow.add_conditional_edges(
    "master_agent",
    route_to_next_agent,
    {
        "sales_agent": "sales_agent",
        "verification_agent": "verification_agent",
        "underwriting_agent": "underwriting_agent",
        "sanction_letter_generator": "sanction_letter_generator",
        "END": END
    }
)

# Compile the graph
app = workflow.compile()
```

## 8. Error Handling and Recovery

### 8.1 Conversation Repair Strategies

- **Context Loss**: Ability to recover conversation context from history
- **Misrouted Tasks**: Logic to detect and correct agent selection errors
- **Customer Confusion**: Clarification prompts when customer intent is unclear
- **API Failures**: Graceful degradation and retry mechanisms

### 8.2 Fallback Responses

The Master Agent will have a set of fallback responses for scenarios where:
- Worker Agents fail to provide a response
- Customer requests are outside the scope of the system
- Technical issues prevent normal operation

## 9. Monitoring and Logging

### 9.1 Conversation Metrics

- **Turn Count**: Number of conversation turns
- **Stage Duration**: Time spent in each conversation stage
- **Agent Utilization**: Frequency and duration of Worker Agent invocations
- **Completion Rate**: Percentage of conversations reaching closure

### 9.2 Audit Trail

Detailed logging of:
- All agent decisions and transitions
- Customer information accessed
- API calls made
- Documents generated

This audit trail ensures compliance with financial regulations and provides data for system improvement.