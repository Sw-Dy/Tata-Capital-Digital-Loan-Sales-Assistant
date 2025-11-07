import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

# Add implementation directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'implementation'))

# Import components
from implementation.master_agent import MasterAgent, ConversationState, ConversationStage, Decision
from implementation.state_manager import StateManager
from implementation.auth import (
    verify_password, get_password_hash, create_access_token, 
    verify_token, get_current_user, User, Token, UserCreate,
    SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
)
from implementation.database import get_db, create_tables
from implementation.db_service import DatabaseService, get_database_service

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('output', 'web_app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('tata_capital_web')

# Ensure required directories exist
for d in ['output', 'static', 'templates', 'uploads']:
    os.makedirs(d, exist_ok=True)

# FastAPI app
app = FastAPI(title="Tata Capital Digital Loan Sales Assistant")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize MasterAgent
gemini_api_key = os.environ.get("GEMINI_API_KEY")
master_agent = MasterAgent(gemini_api_key=gemini_api_key)
state_manager = StateManager("implementation/conversation_state.json")

# Create database tables on startup
create_tables()

# In-memory user storage (replace with database in production)
users_db = {}
user_conversations = {}  # Store conversation state per user

# ------------------- Models -------------------
class MessageRequest(BaseModel):
    message: str

class MessageResponse(BaseModel):
    response: str
    conversation_stage: str
    decision: str

class DocumentUploadResponse(BaseModel):
    status: str
    document_id: Optional[str] = None
    error: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

# ------------------- Routes -------------------

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/message")
async def process_message(request: MessageRequest):
    """Process a user message and return a response"""
    try:
        result = master_agent.process_message(request.message)

        # 🛡️ Validate the output
        if result is None:
            raise ValueError("MasterAgent returned None")

        # If model returned plain text
        if isinstance(result, str):
            return {
                "response": result,
                "conversation_stage": "unknown",
                "decision": "pending"
            }

        # If model returned a dict-like response
        if isinstance(result, dict):
            response_text = result.get("response", "No response generated")
            stage = result.get("stage", "unknown")
            decision = result.get("decision", "pending")

            return {
                "response": response_text,
                "conversation_stage": stage,
                "decision": decision
            }

        # Fallback
        raise TypeError(f"Unexpected return type from MasterAgent: {type(result)}")

    except Exception as e:
        logger.exception("Error processing message:")
        return JSONResponse(status_code=500, content={"detail": f"Error: {str(e)}"})


@app.post("/api/upload-document", response_model=DocumentUploadResponse)
async def upload_document(document_type: str = Form(...), file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        result = master_agent.process_document(file_path, document_type)

        if result.get("status") == "processed":
            # Add system message to conversation
            if isinstance(master_agent.state, dict):
                if "messages" not in master_agent.state:
                    master_agent.state["messages"] = []
                master_agent.state["messages"].append({"role": "system", "content": f"Uploaded {document_type}: {file_path}"})
            else:
                master_agent.state.add_message("system", f"Uploaded {document_type}: {file_path}")
            return DocumentUploadResponse(status="success", document_id=result.get("document_id"))
        else:
            return DocumentUploadResponse(status="error", error=result.get("error", "Unknown error"))

    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@app.get("/api/conversation-state")
async def get_conversation_state():
    """Get the current conversation state"""
    try:
        # Handle both dictionary and object state access
        if isinstance(master_agent.state, dict):
            state_dict = {
                "customer_details": master_agent.state.get("customer_details", {}),
                "loan_details": master_agent.state.get("loan_details", {}),
                "conversation_stage": master_agent.state.get("stage", "unknown"),
                "decision": master_agent.state.get("decision", "pending"),
                "verification_status": master_agent.state.get("verification_status", {}),
                "underwriting_result": master_agent.state.get("underwriting_result", {}),
                "sanction_letter_id": master_agent.state.get("sanction_letter_id"),
                "messages": [
                    {
                        "role": msg.get("role", ""),
                        "content": msg.get("content", ""),
                        "timestamp": msg.get("timestamp", datetime.now().isoformat())
                    } for msg in master_agent.state.get("messages", [])[-10:]
                ]
            }
        else:
            # Object access
            state_dict = {
                "customer_details": master_agent.state.customer_details,
                "loan_details": master_agent.state.loan_details,
                "conversation_stage": master_agent.state.stage.value,
                "decision": master_agent.state.decision.value,
                "verification_status": master_agent.state.verification_status,
                "underwriting_result": master_agent.state.underwriting_result,
                "sanction_letter_id": master_agent.state.sanction_letter_id,
                "messages": [
                    {
                        "role": msg["role"],
                        "content": msg["content"],
                        "timestamp": msg.get("timestamp", datetime.now().isoformat())
                    } for msg in master_agent.state.messages[-10:]
                ]
            }
        return JSONResponse(content=state_dict)
    except Exception as e:
        logger.error(f"Error getting conversation state: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting conversation state: {str(e)}")


@app.get("/api/sanction-letter/{sanction_letter_id}")
async def get_sanction_letter(sanction_letter_id: str):
    """Fetch sanction letter PDF"""
    try:
        sanction_letter_path = f"output/sanction_letter_{sanction_letter_id}.pdf"
        if not os.path.exists(sanction_letter_path):
            raise HTTPException(status_code=404, detail="Sanction letter not found")

        return FileResponse(
            path=sanction_letter_path,
            filename=f"sanction_letter_{sanction_letter_id}.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        logger.error(f"Error getting sanction letter: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting sanction letter: {str(e)}")


@app.post("/api/reset-conversation")
async def reset_conversation():
    """Reset conversation"""
    try:
        global master_agent
        master_agent = MasterAgent(gemini_api_key=gemini_api_key)
        return {"status": "success", "message": "Conversation reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resetting conversation: {str(e)}")


# ------------------- Authentication Routes -------------------

@app.post("/api/auth/register", response_model=AuthResponse)
async def register(user_data: UserRegister, db_service: DatabaseService = Depends(get_database_service)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = db_service.create_user(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password,
            phone=user_data.phone
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": new_user.id})
        
        # Return user data without password
        user_response = {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "phone": new_user.phone
        }
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error registering user: {str(e)}")


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(user_data: UserLogin, db_service: DatabaseService = Depends(get_database_service)):
    """Login user"""
    try:
        # Find user by email
        db_user = db_service.get_user_by_email(user_data.email)
        if not db_user or not verify_password(user_data.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create access token
        access_token = create_access_token(data={"sub": db_user.id})
        
        # Return user data without password
        user_response = {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "phone": db_user.phone
        }
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error logging in user: {str(e)}")


@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user), 
                               db_service: DatabaseService = Depends(get_database_service)):
    """Get current user information"""
    try:
        user = db_service.get_user_by_email(current_user["sub"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone
        }
        
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting user info: {str(e)}")


@app.post("/api/auth/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Logged out successfully"}


# ------------------- Protected Routes -------------------

@app.post("/api/protected/message")
async def process_message_protected(
    request: MessageRequest,
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """Process a user message with authentication"""
    try:
        user_id = current_user["sub"]
        
        # Get or create conversation for user
        conversation = db_service.get_conversation_by_user_id(user_id)
        if not conversation:
            conversation = db_service.create_conversation(user_id)
        
        # Add user message to database
        db_service.add_message(conversation.id, "user", request.message)
        
        # Process message through master agent
        result = master_agent.process_message(request.message)

        # Validate the output
        if result is None:
            raise ValueError("MasterAgent returned None")

        # Handle different response types
        if isinstance(result, str):
            response_text = result
            stage = "unknown"
            decision = "pending"
        elif isinstance(result, dict):
            response_text = result.get("response", "No response generated")
            stage = result.get("stage", "unknown")
            decision = result.get("decision", "pending")
        else:
            raise TypeError(f"Unexpected return type from MasterAgent: {type(result)}")

        # Add assistant response to database
        db_service.add_message(conversation.id, "assistant", response_text)
        
        # Update conversation state
        if stage != "unknown":
            db_service.update_conversation(
                conversation.id,
                stage=stage,
                state=json.dumps({"decision": decision})
            )
        
        return {
            "response": response_text,
            "conversation_stage": stage,
            "decision": decision
        }

    except Exception as e:
        logger.exception("Error processing message:")
        return JSONResponse(status_code=500, content={"detail": f"Error: {str(e)}"})


@app.post("/api/protected/upload-document")
async def upload_document_protected(
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """Upload and process a document with authentication"""
    try:
        user_id = current_user["sub"]
        
        # Get or create conversation for user
        conversation = db_service.get_conversation_by_user_id(user_id)
        if not conversation:
            conversation = db_service.create_conversation(user_id)
        
        # Save file
        file_path = os.path.join("uploads", str(user_id), file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Create document record
        document = db_service.create_document(
            conversation_id=conversation.id,
            document_type=document_type,
            file_name=file.filename,
            file_path=file_path
        )

        # Process document
        result = master_agent.process_document(file_path, document_type)

        # Update document status
        db_service.update_document(
            document.id,
            status="processed" if result.get("status") == "processed" else "error",
            processed_data=json.dumps(result)
        )

        # Add system message to conversation
        db_service.add_message(
            conversation.id,
            "system",
            f"Uploaded {document_type}: {file.filename}"
        )

        if result.get("status") == "processed":
            return DocumentUploadResponse(status="success", document_id=str(document.id))
        else:
            return DocumentUploadResponse(status="error", error=result.get("error", "Unknown error"))

    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@app.get("/api/protected/conversation-state")
async def get_conversation_state_protected(
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """Get the current conversation state with authentication"""
    try:
        user_id = current_user["sub"]
        
        # Get conversation for user
        conversation = db_service.get_conversation_by_user_id(user_id)
        if not conversation:
            return JSONResponse(content={
                "conversation_id": None,
                "customer_details": {},
                "loan_details": {},
                "conversation_stage": "initial",
                "decision": "pending",
                "verification_status": {},
                "underwriting_result": {},
                "sanction_letter_id": None,
                "messages": []
            })
        
        # Get messages
        messages = db_service.get_messages_by_conversation(conversation.id)
        
        # Parse state JSON
        state_data = json.loads(conversation.state) if conversation.state else {}
        
        state_dict = {
            "conversation_id": conversation.id,
            "customer_details": state_data.get("customer_details", {}),
            "loan_details": state_data.get("loan_details", {}),
            "conversation_stage": conversation.stage,
            "decision": state_data.get("decision", "pending"),
            "verification_status": state_data.get("verification_status", {}),
            "underwriting_result": state_data.get("underwriting_result", {}),
            "sanction_letter_id": state_data.get("sanction_letter_id"),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in reversed(messages[-10:])
            ]
        }
        
        return JSONResponse(content=state_dict)
    except Exception as e:
        logger.error(f"Error getting conversation state: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting conversation state: {str(e)}")


@app.post("/api/protected/reset-conversation")
async def reset_conversation_protected(
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """Reset conversation with authentication"""
    try:
        user_id = current_user["sub"]
        
        # Get conversation for user
        conversation = db_service.get_conversation_by_user_id(user_id)
        if conversation:
            # Clear messages and reset state
            db_service.clear_messages(conversation.id)
            db_service.update_conversation(
                conversation.id,
                stage="initial",
                state="{}"
            )
        
        return {"status": "success", "message": "Conversation reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resetting conversation: {str(e)}")


# ------------------- Run App -------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_app:app", host="0.0.0.0", port=8000, reload=True)
