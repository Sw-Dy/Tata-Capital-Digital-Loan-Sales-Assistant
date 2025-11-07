# Parallel Processing Implementation for Loan Application System

## Overview

This implementation adds parallel processing capabilities to the loan application system, enabling the following features:

1. **Document Verification Agent** - Monitors for uploaded income proof documents, verifies them, and assigns confidence scores
2. **Sanction Letter Trigger** - Monitors for conditions to generate a sanction letter when all requirements are met
3. **State Management** - Manages conversation state persistence between the main agent and parallel processes

## Components

### State Manager

The `StateManager` class in `state_manager.py` handles state persistence between the main agent and parallel processes. It provides methods to:

- Save the conversation state to a JSON file
- Load the conversation state from a JSON file
- Convert state objects to dictionaries and vice versa
- Update state with new information from parallel processes

### Document Verification Agent

The `DocumentVerificationAgent` class in `document_verification.py` monitors for uploaded income proof documents and:

- Verifies the documents (simulated with random confidence scores)
- Updates the conversation state with verification results
- Adds messages to the conversation based on verification results

### Sanction Letter Trigger

The `SanctionLetterTrigger` class in `sanction_letter_trigger.py` monitors for conditions to generate a sanction letter when:

- Income proof verification is complete with a confidence score >= 0.5
- Underwriting decision is approved or conditionally approved
- All required customer and loan details are present

## Testing

### Test Scripts

1. **test_parallel_processing.py** - Creates a test conversation state, simulates document upload, and monitors state changes
2. **simulate_document_upload.py** - Simulates uploading a document and monitors state changes
3. **run_parallel_processes.py** - Starts all parallel processes for testing

### How to Test

#### Option 1: Using the test script

```bash
python implementation/test_parallel_processing.py
```

This will:
- Create a test conversation state
- Simulate document upload
- Start parallel processes
- Monitor state changes

#### Option 2: Using the main application with parallel processes

1. Start the main application:
```bash
python main.py
```

2. In another terminal, simulate document upload:
```bash
python implementation/simulate_document_upload.py
```

3. Monitor the logs to see the document verification and sanction letter generation process.

#### Option 3: Running parallel processes separately

1. Start the parallel processes:
```bash
python implementation/run_parallel_processes.py
```

2. Simulate document upload:
```bash
python implementation/simulate_document_upload.py
```

## Integration with Master Agent

The `MasterAgent` class in `master_agent.py` has been updated to:

- Initialize the `StateManager` in its constructor
- Start parallel processes using `_start_parallel_processes()`
- Save and load state before and after running verification, underwriting, and sanction letter agents

## Troubleshooting

- If parallel processes are not starting, check the logs for error messages
- If document verification is not working, check that the document upload simulation is working correctly
- If sanction letter generation is not working, check that all required conditions are met (verification status, confidence score, underwriting decision, customer and loan details)