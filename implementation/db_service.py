from sqlalchemy.orm import Session
from .database import User, Conversation, Message, Document, SanctionLetter, get_db
from datetime import datetime
import uuid
import json

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    # User operations
    def create_user(self, name: str, email: str, hashed_password: str, phone: str = None):
        user = User(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            hashed_password=hashed_password,
            phone=phone
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: str):
        return self.db.query(User).filter(User.id == user_id).first()
    
    # Conversation operations
    def create_conversation(self, user_id: str):
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def get_conversation_by_user_id(self, user_id: str):
        return self.db.query(Conversation).filter(Conversation.user_id == user_id).first()
    
    def update_conversation(self, conversation_id: str, **kwargs):
        conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            for key, value in kwargs.items():
                if hasattr(conversation, key):
                    setattr(conversation, key, value)
            conversation.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(conversation)
        return conversation
    
    # Message operations
    def add_message(self, conversation_id: str, role: str, content: str):
        message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_messages_by_conversation(self, conversation_id: str, limit: int = 50):
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.desc()).limit(limit).all()
    
    # Document operations
    def create_document(self, conversation_id: str, document_type: str, file_name: str, file_path: str):
        document = Document(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            document_type=document_type,
            file_name=file_name,
            file_path=file_path
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def update_document(self, document_id: str, **kwargs):
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if document:
            for key, value in kwargs.items():
                if hasattr(document, key):
                    setattr(document, key, value)
            if 'status' in kwargs and kwargs['status'] == 'processed':
                document.processed_at = datetime.now()
            self.db.commit()
            self.db.refresh(document)
        return document
    
    def get_documents_by_conversation(self, conversation_id: str):
        return self.db.query(Document).filter(Document.conversation_id == conversation_id).all()
    
    # Sanction letter operations
    def create_sanction_letter(self, conversation_id: str, user_id: str, file_path: str, 
                             loan_amount: float = None, interest_rate: float = None, tenure: int = None):
        sanction_letter = SanctionLetter(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            user_id=user_id,
            file_path=file_path,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            tenure=tenure
        )
        self.db.add(sanction_letter)
        self.db.commit()
        self.db.refresh(sanction_letter)
        return sanction_letter
    
    def get_sanction_letter_by_id(self, sanction_letter_id: str):
        return self.db.query(SanctionLetter).filter(SanctionLetter.id == sanction_letter_id).first()
    
    def get_sanction_letters_by_user(self, user_id: str):
        return self.db.query(SanctionLetter).filter(SanctionLetter.user_id == user_id).all()

# Dependency for FastAPI
def get_database_service(db: Session = Depends(get_db)):
    return DatabaseService(db)