from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean, Integer, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/tata_capital_loans"
)

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    conversation_stage = Column(String, default="initial")
    decision = Column(String, default="pending")
    customer_details = Column(JSON, default=dict)
    loan_details = Column(JSON, default=dict)
    verification_status = Column(JSON, default=dict)
    underwriting_result = Column(JSON, default=dict)
    sanction_letter_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, nullable=False, index=True)
    document_type = Column(String, nullable=False)  # aadhaar, pan, salary_slip, etc.
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    document_id = Column(String, nullable=True)
    status = Column(String, default="uploaded")  # uploaded, processed, failed
    verification_result = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

class SanctionLetter(Base):
    __tablename__ = "sanction_letters"
    
    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    file_path = Column(String, nullable=False)
    loan_amount = Column(Float, nullable=True)
    interest_rate = Column(Float, nullable=True)
    tenure = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!")