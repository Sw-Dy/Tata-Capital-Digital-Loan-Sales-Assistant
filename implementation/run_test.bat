@echo off
echo Starting parallel processes test...

echo Creating a clean state file...
python test_parallel_processing.py

echo Starting parallel processes...
start "Document Verification" cmd /c "python document_verification.py --state_file=test_conversation_state.json"
start "Sanction Letter Trigger" cmd /c "python sanction_letter_trigger.py --state_file=test_conversation_state.json"

echo Simulating document upload...
python simulate_document_upload.py --state_file=test_conversation_state.json

echo Test complete. Check the console outputs for results.
pause