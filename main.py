import os
from urllib.parse import quote_plus
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from datetime import datetime
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Database Configuration (MySQL)
def build_mysql_url_from_env() -> str:
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME")
    
    if not all([db_user, db_password, db_host, db_name]):
        raise ValueError("Missing required database credentials in .env file. Please set DB_USER, DB_PASSWORD, DB_HOST, and DB_NAME")
    
    safe_password = quote_plus(db_password)
    return f"mysql+pymysql://{db_user}:{safe_password}@{db_host}:{db_port}/{db_name}"

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", build_mysql_url_from_env())

connect_args = {}
db_ssl_ca = os.getenv("DB_SSL_CA") 
if db_ssl_ca:
    connect_args["ssl"] = {"ca": db_ssl_ca}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    company = Column(String(255))
    job_title = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class EventRegistration(Base):
    __tablename__ = "event_registrations"
    registration_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    company = Column(String(255))
    job_title = Column(String(255))
    years_of_experience = Column(String(50))
    topics_of_interest = Column(Text)
    dietary_restrictions = Column(Text)
    referral_source = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class WaitlistRegistration(Base):
    __tablename__ = "waitlist_registrations"
    waitlist_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    company = Column(String(255))
    job_title = Column(String(255))
    reason_to_attend = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class ContactMessage(Base):
    __tablename__ = "contact_messages"
    message_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    company_organization = Column(String(255))
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SpeakerApplication(Base):
    __tablename__ = "speaker_applications"
    application_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    linkedin_profile = Column(String(255))
    area_of_expertise = Column(String(100), nullable=False)
    proposed_topic_title = Column(String(255), nullable=False)
    topic_description = Column(Text, nullable=False)
    speaking_experience = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class SponsorshipInquiry(Base):
    __tablename__ = "sponsorship_inquiries"
    inquiry_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    contact_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    company_website = Column(String(255))
    interested_sponsorship_level = Column(String(100))
    marketing_objectives = Column(Text, nullable=False)
    budget_range = Column(String(50))
    timeline = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class PartnershipProposal(Base):
    __tablename__ = "partnership_proposals"
    proposal_id = Column(Integer, primary_key=True, index=True)
    organization_name = Column(String(255), nullable=False)
    contact_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    organization_website = Column(String(255))
    partnership_type = Column(String(100), nullable=False)
    partnership_proposal = Column(Text, nullable=False)
    audience_community = Column(Text)
    resources_contributed = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class VolunteerApplication(Base):
    __tablename__ = "volunteer_applications"
    application_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(20))
    profession = Column(String(255), nullable=False)
    company_organization = Column(String(255))
    volunteer_experience = Column(String(50))
    availability = Column(String(50), nullable=False)
    relevant_skills_experience = Column(Text, nullable=False)
    areas_of_interest = Column(Text, nullable=False)
    motivation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models for Request Validation
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    company: str | None = None
    job_title: str | None = None

class EventRegistrationCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    company: str | None = None
    job_title: str | None = None
    years_of_experience: str | None = None
    topics_of_interest: str | None = None
    dietary_restrictions: str | None = None
    referral_source: str | None = None

class WaitlistRegistrationCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    company: str | None = None
    job_title: str | None = None
    reason_to_attend: str

class ContactMessageCreate(BaseModel):
    full_name: str
    email: str
    company_organization: str | None = None
    message: str

class SpeakerApplicationCreate(BaseModel):
    full_name: str
    email: str
    company: str
    job_title: str
    linkedin_profile: str | None = None
    area_of_expertise: str
    proposed_topic_title: str
    topic_description: str
    speaking_experience: str | None = None

class SponsorshipInquiryCreate(BaseModel):
    company_name: str
    contact_name: str
    email: str
    phone: str | None = None
    company_website: str | None = None
    interested_sponsorship_level: str | None = None
    marketing_objectives: str
    budget_range: str | None = None
    timeline: str | None = None

class PartnershipProposalCreate(BaseModel):
    organization_name: str
    contact_name: str
    email: str
    phone: str | None = None
    organization_website: str | None = None
    partnership_type: str
    partnership_proposal: str
    audience_community: str | None = None
    resources_contributed: str | None = None

class VolunteerApplicationCreate(BaseModel):
    full_name: str
    email: str
    phone_number: str | None = None
    profession: str
    company_organization: str | None = None
    volunteer_experience: str | None = None
    availability: str
    relevant_skills_experience: str
    areas_of_interest: str
    motivation: str

# Create Database Tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to MMML Backend API - with deploy workflow 2", "docs": "/docs"}

# API Endpoints
@app.post("/users/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"user_id": db_user.user_id}

@app.post("/event-registrations/")
async def create_event_registration(registration: EventRegistrationCreate, db: Session = Depends(get_db)):
    db_registration = EventRegistration(**registration.model_dump())
    db.add(db_registration)
    db.commit()
    db.refresh(db_registration)
    return {"registration_id": db_registration.registration_id}

@app.post("/waitlist-registrations/")
async def create_waitlist_registration(registration: WaitlistRegistrationCreate, db: Session = Depends(get_db)):
    db_registration = WaitlistRegistration(**registration.model_dump())
    db.add(db_registration)
    db.commit()
    db.refresh(db_registration)
    return {"waitlist_id": db_registration.waitlist_id}

@app.post("/contact-messages/")
async def create_contact_message(message: ContactMessageCreate, db: Session = Depends(get_db)):
    db_message = ContactMessage(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return {"message_id": db_message.message_id}

@app.post("/speaker-applications/")
async def create_speaker_application(application: SpeakerApplicationCreate, db: Session = Depends(get_db)):
    db_application = SpeakerApplication(**application.model_dump())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return {"application_id": db_application.application_id}

@app.post("/sponsorship-inquiries/")
async def create_sponsorship_inquiry(inquiry: SponsorshipInquiryCreate, db: Session = Depends(get_db)):
    db_inquiry = SponsorshipInquiry(**inquiry.model_dump())
    db.add(db_inquiry)
    db.commit()
    db.refresh(db_inquiry)
    return {"inquiry_id": db_inquiry.inquiry_id}

@app.post("/partnership-proposals/")
async def create_partnership_proposal(proposal: PartnershipProposalCreate, db: Session = Depends(get_db)):
    db_proposal = PartnershipProposal(**proposal.model_dump())
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    return {"proposal_id": db_proposal.proposal_id}

@app.post("/volunteer-applications/")
async def create_volunteer_application(application: VolunteerApplicationCreate, db: Session = Depends(get_db)):
    db_application = VolunteerApplication(**application.model_dump())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return {"application_id": db_application.application_id}

if __name__ == "__main__":
    print("🚀 Starting MMML Backend Server...")
    print("📖 API Documentation available at: http://localhost:8000/docs")
    print("🌐 Server will be running at: http://localhost:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)