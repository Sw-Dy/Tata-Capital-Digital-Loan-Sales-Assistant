// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const loanStageIndicator = document.getElementById('loanStageIndicator');
const loanDetails = document.getElementById('loanDetails');
const documentUploadForm = document.getElementById('documentUploadForm');
const uploadStatus = document.getElementById('uploadStatus');
const sanctionLetterSection = document.getElementById('sanctionLetterSection');
const downloadSanctionLetterButton = document.getElementById('downloadSanctionLetter');

// State variables
let conversationState = {
    stage: 'greeting',
    decision: 'pending',
    sanction_letter_id: null
};

// Add initial greeting message
addMessage('assistant', 'Hello! Welcome to Tata Capital. How can I assist you with your loan needs today?');

// Event Listeners
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

documentUploadForm.addEventListener('submit', uploadDocument);

downloadSanctionLetterButton.addEventListener('click', downloadSanctionLetter);

// Fetch initial state
fetchConversationState();

// Functions
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessage('user', message);
    messageInput.value = '';
    
    try {
        // Send message to API
        const response = await fetch('/api/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            throw new Error('Failed to send message');
        }
        
        const data = await response.json();
        
        // Add assistant response to chat
        addMessage('assistant', data.response);
        
        // Update conversation state
        conversationState.stage = data.conversation_stage;
        conversationState.decision = data.decision;
        
        // Update UI based on new state
        updateLoanStageIndicator();
        fetchConversationState();
        
    } catch (error) {
        console.error('Error sending message:', error);
        addMessage('system', 'Error: Failed to send message. Please try again.');
    }
}

async function uploadDocument(e) {
    e.preventDefault();
    
    const documentType = document.getElementById('documentType').value;
    const fileInput = document.getElementById('documentFile');
    const file = fileInput.files[0];
    
    if (!documentType || !file) {
        uploadStatus.textContent = 'Please select a document type and file';
        uploadStatus.className = 'upload-error';
        return;
    }
    
    // Create form data
    const formData = new FormData();
    formData.append('document_type', documentType);
    formData.append('file', file);
    
    try {
        uploadStatus.textContent = 'Uploading...';
        uploadStatus.className = '';
        
        // Send document to API
        const response = await fetch('/api/upload-document', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to upload document');
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            uploadStatus.textContent = 'Document uploaded successfully!';
            uploadStatus.className = 'upload-success';
            
            // Add system message to chat
            addMessage('system', `Uploaded ${documentType}: ${file.name}`);
            
            // Reset form
            documentUploadForm.reset();
            
            // Fetch updated state
            fetchConversationState();
        } else {
            uploadStatus.textContent = `Error: ${data.error || 'Unknown error'}`;
            uploadStatus.className = 'upload-error';
        }
        
    } catch (error) {
        console.error('Error uploading document:', error);
        uploadStatus.textContent = 'Error: Failed to upload document. Please try again.';
        uploadStatus.className = 'upload-error';
    }
}

async function fetchConversationState() {
    try {
        const response = await fetch('/api/conversation-state');
        
        if (!response.ok) {
            throw new Error('Failed to fetch conversation state');
        }
        
        const data = await response.json();
        
        // Update local state
        conversationState = {
            stage: data.conversation_stage,
            decision: data.decision,
            sanction_letter_id: data.sanction_letter_id,
            customer_details: data.customer_details,
            loan_details: data.loan_details,
            verification_status: data.verification_status,
            underwriting_result: data.underwriting_result
        };
        
        // Update UI
        updateLoanStageIndicator();
        updateLoanDetails();
        updateSanctionLetterSection();
        
    } catch (error) {
        console.error('Error fetching conversation state:', error);
    }
}

function addMessage(role, content) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    
    if (role === 'user') {
        messageElement.classList.add('user-message');
    } else if (role === 'assistant') {
        messageElement.classList.add('assistant-message');
    } else if (role === 'system') {
        messageElement.classList.add('system-message');
    }
    
    messageElement.textContent = content;
    chatMessages.appendChild(messageElement);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateLoanStageIndicator() {
    // Reset all stages
    const stages = loanStageIndicator.querySelectorAll('.stage');
    stages.forEach(stage => {
        stage.classList.remove('active', 'completed');
    });
    
    // Mark completed and active stages
    const stageOrder = ['greeting', 'intent_capture', 'sales_exploration', 'verification', 'underwriting', 'documentation', 'closure'];
    const currentStageIndex = stageOrder.indexOf(conversationState.stage);
    
    stages.forEach((stage, index) => {
        const stageName = stage.getAttribute('data-stage');
        const stageIndex = stageOrder.indexOf(stageName);
        
        if (stageIndex < currentStageIndex) {
            stage.classList.add('completed');
        } else if (stageIndex === currentStageIndex) {
            stage.classList.add('active');
        }
    });
}

function updateLoanDetails() {
    // Clear existing details
    loanDetails.innerHTML = '';
    
    // Create definition list
    const dl = document.createElement('dl');
    
    // Add customer details if available
    if (conversationState.customer_details) {
        if (conversationState.customer_details.name) {
            addDetailItem(dl, 'Customer Name', conversationState.customer_details.name);
        }
        if (conversationState.customer_details.phone) {
            addDetailItem(dl, 'Phone', conversationState.customer_details.phone);
        }
    }
    
    // Add loan details if available
    if (conversationState.loan_details) {
        if (conversationState.loan_details.amount) {
            addDetailItem(dl, 'Loan Amount', `₹${conversationState.loan_details.amount}`);
        }
        if (conversationState.loan_details.tenure) {
            addDetailItem(dl, 'Tenure', `${conversationState.loan_details.tenure} months`);
        }
        if (conversationState.loan_details.purpose) {
            addDetailItem(dl, 'Purpose', conversationState.loan_details.purpose);
        }
        if (conversationState.loan_details.interest_rate) {
            addDetailItem(dl, 'Interest Rate', `${conversationState.loan_details.interest_rate}%`);
        }
        if (conversationState.loan_details.emi) {
            addDetailItem(dl, 'EMI', `₹${conversationState.loan_details.emi}`);
        }
    }
    
    // Add decision status
    addDetailItem(dl, 'Decision', conversationState.decision.toUpperCase());
    
    loanDetails.appendChild(dl);
}

function addDetailItem(dl, term, detail) {
    const dt = document.createElement('dt');
    dt.textContent = term;
    
    const dd = document.createElement('dd');
    dd.textContent = detail;
    
    dl.appendChild(dt);
    dl.appendChild(dd);
}

function updateSanctionLetterSection() {
    if (conversationState.sanction_letter_id && conversationState.decision === 'approved') {
        sanctionLetterSection.style.display = 'block';
    } else {
        sanctionLetterSection.style.display = 'none';
    }
}

async function downloadSanctionLetter() {
    if (!conversationState.sanction_letter_id) return;
    
    try {
        // Open sanction letter in new tab
        window.open(`/api/sanction-letter/${conversationState.sanction_letter_id}`, '_blank');
    } catch (error) {
        console.error('Error downloading sanction letter:', error);
        addMessage('system', 'Error: Failed to download sanction letter. Please try again.');
    }
}

// Poll for state updates every 5 seconds
setInterval(fetchConversationState, 5000);