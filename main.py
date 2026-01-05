import os
from urllib.parse import quote_plus
from fastapi import FastAPI, HTTPException, Depends ,  Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
# CORRECT 👇
from datetime import datetime, timedelta
from dotenv import load_dotenv
import uvicorn
from email_service import send_form_submission_emails , send_registration_email
import razorpay
import enum
import json, hmac, hashlib, os, logging
from fastapi.responses import JSONResponse
from sqlalchemy import Column, Integer, String, Enum, DECIMAL, DateTime, Boolean, func , Text ,create_engine
from zoneinfo import ZoneInfo
from fastapi import BackgroundTasks
from jose import jwt
from passlib.context import CryptContext
from google.oauth2 import id_token
from google.auth.transport import requests



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.mmml.co.in",
        "https://mmml.co.in", 
        "http://localhost:3000",  # For local development
        "http://localhost:5173",  # For Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

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

IST = ZoneInfo("Asia/Kolkata")
# Database Models
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class EventRegistration(Base):
    __tablename__ = "event_registrations"
    registration_id = Column(Integer, primary_key=True, index=True)
    salutation = Column(String(10))
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
    linkedin_profile = Column(String(255))   # ✅ new column
    Venue = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)


class ContactMessage(Base):
    __tablename__ = "contact_messages"
    message_id = Column(Integer, primary_key=True, index=True)
    salutation = Column(String(10))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    company_organization = Column(String(255))
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SpeakerApplication(Base):
    __tablename__ = "speaker_applications"
    application_id = Column(Integer, primary_key=True, index=True)
    salutation = Column(String(10))
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
    salutation = Column(String(10))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
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
    salutation: str | None = None
    first_name: str
    last_name: str
    email: str
    phone_number: str
    company: str | None = None
    job_title: str | None = None

class EventRegistrationCreate(BaseModel):
    salutation: str | None = None
    first_name: str
    last_name: str
    email: str
    phone_number: str
    company: str | None = None
    job_title: str | None = None
    years_of_experience: str | None = None
    topics_of_interest: str | None = None
    dietary_restrictions: str | None = None
  


class WaitlistRegistrationCreate(BaseModel):
    salutation: str | None = None
    first_name: str
    last_name: str
    email: str
    city: str

class ContactMessageCreate(BaseModel):
    salutation: str | None = None
    first_name: str
    last_name: str
    email: str
    company_organization: str | None = None
    message: str

class SpeakerApplicationCreate(BaseModel):
    salutation: str | None = None
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
    salutation: str | None = None
    first_name: str
    last_name: str
    email: str
    phone_number: str | None = None
    profession: str
    company_organization: str | None = None
    volunteer_experience: str | None = None
    availability: str
    relevant_skills_experience: str
    areas_of_interest: str
    motivation: str

class Contact(Base):
    __tablename__ = "crm_contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    salutation = Column(Text)
    fullname = Column(Text)
    firstname = Column(Text)
    lastname = Column(Text)
    email = Column(String(250), unique=True)
    designation = Column(Text)
    company = Column(Text)
    phone = Column(Text)
    status = Column(Text)
    mmml = Column(Text)
    fintellect = Column(Text)
    location = Column(Text)
    linkedin = Column(Text)
    coupon_code = Column(Text)
    last_emailed = Column(DateTime)
    mmml_time = Column(DateTime)
    years_of_experience = Column(String(20), nullable=False)
    dietary_preference = Column(String(20), nullable=False)
    about_mmml = Column(String(20))
    mmml_membership_application=Column(Text)
    MMML_Account = Column(String(20))
    Mum = Column(String(20))
    Blr = Column(String(20))
    
class OrderRequest(BaseModel):
    amount: int  # Amount in INR paise
    
class DiscountType(str, enum.Enum):
    flat = "flat"
    percentage = "percentage"

class Coupon(Base):
    __tablename__ = "Coupons"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    discount_type = Column(Enum(DiscountType), nullable=False)
    discount_value = Column(DECIMAL(10, 2), nullable=False)
    max_usage = Column(Integer, nullable=False)
    used_count = Column(Integer, default=0)
    expiry_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

# Request schema
class ApplyCouponRequest(BaseModel):
    coupon_code: str
    amount: float

# Response schema
class ApplyCouponResponse(BaseModel):
    status_code: int
    message: str
    final_amount: float
    
class ProcessedPayment(Base):
    __tablename__ = "processed_payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String(100), unique=True, nullable=False)  # Razorpay ID
    created_at = Column(DateTime, default=datetime.utcnow)
    
class MembershipApplicationCreate(BaseModel):
    full_name: str
    email: str
    company: str
    title: str
    linkedin: str | None = None
    
class AuthRequest(BaseModel):
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    token: str  # OAuth access token from frontend
    
class LoggedInUserResponse(BaseModel):
    salutation: str | None
    first_name: str | None
    last_name: str | None
    email: str
    phone: str | None
    company: str | None
    designation: str | None
    location: str | None
    linkedin: str | None
    years_of_experience: str | None
    dietary_preference: str | None


class CheckAccountRequest(BaseModel):
    email: str


# Create Database Tables
Base.metadata.create_all(bind=engine)

# ---------- CONFIG ----------
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGO = os.getenv("JWT_ALGORITHM", "HS256")
pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")  # add to .env
import requests as http

def verify_google_token(token: str):
    resp = http.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {token}"}
    )

    if resp.status_code != 200:
        return None
    return resp.json()



# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGO)

def get_current_user_email(authorization: str = Header(...)) -> str:
    try:
        token = authorization.replace("Bearer ", "")
        print("Token received:", token)
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET_KEY"),
            algorithms=os.getenv("JWT_ALGORITHM", "HS256")
        )
        print("Decoded payload:", payload)
        return payload.get("email")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to MMML Backend API", "docs": "/docs"}


@app.get("/fetch-logged-in-user/")
def get_logged_in_user(
    email: str = Depends(get_current_user_email),
    db: Session = Depends(lambda: SessionLocal())
):
    contact = (
        db.query(Contact)
        .filter(
            Contact.email == email,
            Contact.MMML_Account.ilike("Yes")
        )
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=403,
            detail="User does not have an active MMML account"
        )

    return {
        "status_code": 200,
        "data": {
            "salutation": contact.salutation,
            "first_name": contact.firstname,
            "last_name": contact.lastname,
            "email": contact.email,
            "phone": contact.phone,
            "company": contact.company,
            "designation": contact.designation,
            "location": contact.location,
            "linkedin": contact.linkedin,
            "years_of_experience": contact.years_of_experience,
            "dietary_preference": contact.dietary_preference,
        },
    }

@app.post("/check-account/")
def check_account(
    payload: CheckAccountRequest,
    db: Session = Depends(lambda: SessionLocal())
):
    contact = (
        db.query(Contact)
        .filter(Contact.email == payload.email)
        .first()
    )

    if not contact:
        return {
            "status_code": 200,
            "data": {
                "exists": False,
                "has_mmml_account": False,
            },
        }

    return {
        "status_code": 200,
        "data": {
            "exists": True,
            "has_mmml_account": (
                contact.MMML_Account is not None
                and contact.MMML_Account.lower() == "yes"
            ),
        },
    }
    
    
@app.post("/auth")
def login_or_signup(payload: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    # User exists → LOGIN
    if user is not None :
        if user.password is None:
            raise HTTPException(status_code=400, detail="Password not set for this user")
        if not pwd.verify(payload.password, user.password):
            
            raise HTTPException(status_code=400, detail="Incorrect password")
        
        token = create_token({"user_id": user.user_id, "email": user.email , "new_user": False})
        return {
            "status_code": 200,
            "message": "Login successful",
            "token": token
        }

    # User not exists → SIGNUP
    hashed_pass = pwd.hash(payload.password)
    new_user = User(email=payload.email, password=hashed_pass)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_token({"user_id": new_user.user_id, "email": new_user.email , "new_user": True})

    return {
        "status_code": 200,
        "message": "Account created",
        "token": token
    }

@app.post("/auth/google")
def google_login(payload: GoogleAuthRequest, db: Session = Depends(get_db)):
    google_data = verify_google_token(payload.token)

    if not google_data:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    email = google_data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not found in Google token")

    user = db.query(User).filter(User.email == email).first()

    # Existing user → LOGIN
    if user:
        token = create_token({"user_id": user.user_id, "email": user.email , "new_user":False})
        return {
            "status_code": 200,
            "message": "Login successful",
            "token": token
        }

    # New user → SIGNUP without password
    new_user = User(email=email, password="google_oauth")  # placeholder
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_token({"user_id": new_user.user_id, "email": new_user.email , "new_user":True})
    return {
        "status_code": 201,
        "message": "Account created",
        "token": token
    }


# API Endpoints
@app.post("/auth/google")
def google_login(payload: GoogleAuthRequest, db: Session = Depends(get_db)):
    google_data = verify_google_token(payload.token)

    if not google_data:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    email = google_data.get("email")
    name = google_data.get("name") or email.split("@")[0]

    user = db.query(User).filter(User.email == email).first()

    if user:
        token = create_token({"user_id": user.user_id, "email": user.email, "new_user": False})
        return {
            "status_code": 200,
            "message": f"Welcome back {name}",
            "token": token
        }

    new_user = User(email=email, password="google_oauth")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_token({"user_id": new_user.user_id, "email": new_user.email, "new_user": True})

    return {
        "status_code": 201,
        "message": "Account created",
        "token": token
    }


razorpay_client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET")))


@app.post("/create-order/")
def create_order(order: OrderRequest):
    try:
        logger.info("Incoming create-order request: %s", order.dict())

        # # Validate amount
        # if order.amount not in [49900]:
        #     logger.warning("Invalid subscription amount: %s", order.amount)
        #     raise HTTPException(status_code=400, detail="Invalid subscription amount")

        # Prepare order payload
        order_data = {
            "amount": order.amount,  # Amount in paise
            "currency": "INR",
            "payment_capture": 1
        }
        logger.info("Order payload: %s", order_data)

        # Call Razorpay
        order_response = razorpay_client.order.create(data=order_data)
        logger.info("Razorpay response: %s", order_response)

        return {
            "id": order_response["id"],
            "currency": order_response["currency"],
            "amount": order_response["amount"],
            "status": order_response["status"]
        }

    except HTTPException as e:
        logger.error("HTTP Exception: %s", str(e.detail))
        raise
    except razorpay.errors.BadRequestError as e:
        logger.error("Razorpay BadRequestError: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error while creating order")
        raise HTTPException(status_code=500, detail="Failed to create order")





@app.post("/apply", response_model=ApplyCouponResponse)
def apply_coupon(data: ApplyCouponRequest, db: Session = Depends(get_db)):
    coupon = db.query(Coupon).filter(Coupon.code == data.coupon_code).first()

    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid coupon code")
    if not coupon.is_active:
        raise HTTPException(status_code=400, detail="Coupon is inactive")
    if coupon.expiry_date < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Coupon has expired")
    if coupon.used_count >= coupon.max_usage:
        raise HTTPException(status_code=400, detail="Coupon usage limit reached")
    # Apply discount
    if coupon.discount_type == DiscountType.flat:
        discount = float(coupon.discount_value)
    else:  # percentage
        discount = (float(coupon.discount_value) / 100) * data.amount

    final_amount = max(0, data.amount - discount)

    return {
        "status_code": 200,
        "message": f"Discount of {discount} applied",
        "final_amount": final_amount
    }
    
@app.post("/post-login-registration/")
def post_login_registration(
    reg: EventRegistrationCreate,
    db: Session = Depends(get_db)
):
    existing_contact = db.query(Contact).filter(
        Contact.email == reg.email
    ).first()

    # ---------------- EXISTING CONTACT ----------------
    if existing_contact:
        existing_contact.MMML_Account = "Yes"
        db.commit()
        db.refresh(existing_contact)

        return {
            "status": "success",
            "message": "Existing contact updated with MMML account",
            "data": {"id": existing_contact.id}
        }

    # ---------------- NEW CONTACT ----------------
    new_contact = Contact(
        salutation=reg.salutation,
        firstname=reg.first_name,
        lastname=reg.last_name,
        fullname=f"{reg.first_name} {reg.last_name}",
        email=reg.email,
        phone=reg.phone_number,
        company=reg.company,
        designation=reg.job_title,
        years_of_experience=reg.years_of_experience or "0",
        dietary_preference=reg.dietary_restrictions or "none",
        MMML_Account="Yes",
    )

    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    return {
        "status": "success",
        "message": "New contact created with MMML account",
        "data": {"id": new_contact.id}
    }


@app.post("/event-registration-webhook/")
async def event_registration_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_razorpay_signature: str = Header(None, alias="X-Razorpay-Signature"),
    db: Session = Depends(get_db),
):
    logger.info("---- EVENT REGISTRATION WEBHOOK HIT ----")

    # Read raw body
    raw_body = await request.body()
    if not x_razorpay_signature:
        logger.warning("Missing Razorpay signature header.")
        return JSONResponse(
            status_code=400, 
            content={"status": "error", "detail": "Missing Razorpay signature"},
        )

    # Verify signature
    RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")
    expected_signature = hmac.new(
        key=RAZORPAY_WEBHOOK_SECRET.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, x_razorpay_signature):
        logger.error("Signature mismatch.")
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": "Invalid signature"},
        )

    # Parse JSON
    try:
        payload = json.loads(raw_body)
    except Exception as e:
        logger.exception("JSON parse error: %s", e)
        return JSONResponse(
            status_code=400,
            content={"status": "ignored", "detail": "Bad JSON"},
        )
        
    event_type = payload.get("event")
    if event_type != "payment.captured":
        logger.info("Ignoring non-captured event: %s", event_type)
        return JSONResponse(status_code=200, content={"status": "ignored", "detail": "non-captured event"})
    payment_data = (
        payload.get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )
    payment_id = payment_data.get("id")
    
    existing_payment = db.query(ProcessedPayment).filter(
        ProcessedPayment.payment_id == payment_id
    ).first()
    
    if existing_payment:
        logger.info("Duplicate webhook for payment_id %s ignored", payment_id)
        return JSONResponse(status_code=200, content={"status": "success", "detail": "already processed"})


    notes = payment_data.get("notes", {}) or {}

    # Extract data from notes
    email = notes.get("email")
    first_name = notes.get("first_name")
    last_name = notes.get("last_name")
    venue = notes.get("venue")
    date = notes.get("date")
    time = notes.get("time")
    extra_raw = notes.get("extra")
    extra = {}

    logger.info("RAW EXTRA RECEIVED: %s", extra_raw)

    if extra_raw:
        # Case 1 – already dict
        if isinstance(extra_raw, dict):
            extra = extra_raw
        else:
            try:
                extra = json.loads(extra_raw)
            except Exception as e:
                logger.warning("FAILED normal JSON parse: %s", e)

                # Case 2 – single quotes → fix
                try:
                    fixed = extra_raw.replace("'", '"')
                    extra = json.loads(fixed)
                except Exception as e2:
                    logger.error("FAILED fallback JSON parse: %s", e2)
                    extra = {}
            
    salutation = extra.get("salutation")
    phone_number = extra.get("phone_number")
    company = extra.get("company")
    job_title = extra.get("job_title")
    years_of_experience = extra.get("years_of_experience")
    topics_of_interest = extra.get("topics_of_interest")
    dietary_restrictions = extra.get("dietary_restrictions")
    referral_source = extra.get("referral_source")
    linkedin_profile = extra.get("linkedin_profile")
    coupon_code = extra.get("coupon_code")
    venue_info = extra.get("venue_info")
    
    logger.info("FINAL FIELD VALUES BEING SAVED: %s", {
        "salutation": salutation,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "venue": venue,
        "phone_number": phone_number,
        "years_of_experience": years_of_experience,
        "topics_of_interest": topics_of_interest,
        "dietary_restrictions": dietary_restrictions,
        "referral_source": referral_source,
        "linkedin_profile": linkedin_profile,
        "coupon_code": coupon_code,
        "venue_info": venue_info,
    })
    
    if not email:
        logger.warning("Missing email in webhook notes.")
        return JSONResponse(
            status_code=200,  # 200 so Razorpay doesn’t retry endlessly
            content={"status": "ignored", "reason": "missing email"},
        )

    try:
            # Start transaction
        with db.begin_nested():
            if coupon_code:
                updated = db.query(Coupon).filter(
                    Coupon.code == coupon_code,
                    Coupon.used_count < Coupon.max_usage
                ).update({Coupon.used_count: Coupon.used_count + 1})
            
                if not updated:
                    logger.warning("Coupon %s usage exceeded or not found", coupon_code)

            # Check duplicate registration
            existing_registration = db.query(EventRegistration).filter(
                EventRegistration.email == email,
                EventRegistration.Venue == venue
            ).first()

            if existing_registration:
                logger.info("User already registered: %s", email)

            if not existing_registration:
                db_registration = EventRegistration(
                    salutation=salutation,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=phone_number,
                    company=company,
                    job_title=job_title,
                    years_of_experience=years_of_experience,
                    topics_of_interest=topics_of_interest,
                    dietary_restrictions=dietary_restrictions,
                    referral_source=referral_source,
                    linkedin_profile = linkedin_profile,
                    Venue = venue,
                )
                db.add(db_registration)

            # Create Contact if not exists
            existing_contact = db.query(Contact).filter(Contact.email == email).first()
            if not existing_contact:
                db_contact = Contact(
                    fullname=f"{first_name} {last_name}",
                    salutation=salutation,
                    firstname=first_name,
                    lastname=last_name,
                    email=email,
                    phone=phone_number,
                    company=company,
                    designation=job_title,
                    mmml="Yes",
                    mmml_time = datetime.now(IST),
                    coupon_code = coupon_code,
                    years_of_experience = years_of_experience,
                    dietary_preference = dietary_restrictions,
                    about_mmml = referral_source,
                    linkedin=linkedin_profile,
                    Mum = 'Yes' if venue == 'Mumbai' else 'No',
                    Blr = 'Yes' if venue == 'Bangalore' else 'No',
                )
                db.add(db_contact)
            else :
                existing_contact.mmml_time = datetime.now(IST)  # ✅ update timestamp
                existing_contact.mmml = 'Yes' 
                existing_contact.coupon_code=coupon_code
                existing_contact.Mum = 'Yes' if venue == 'Mumbai' else existing_contact.Mum
                existing_contact.Blr = 'Yes' if venue == 'Bangalore' else existing_contact.Blr
                logger.info("Updated mmmL time for exisiting user %s", datetime.now(IST))
        
            db_payment = ProcessedPayment(payment_id=payment_id)
            db.add(db_payment)
        db.commit()  # ensures all changes are persisted    
        logger.info("Event Registration successful for %s", email)
        fullname=f"{first_name} {last_name}"
        event_name = "MMML " +  (venue if venue else "Event")
        event_date = date if date else "to be announced"
        event_time = time if time else "to be announced"
        event_city = venue if venue else "to be announced"
        event_venue_status = venue_info if venue_info else "to be announced"
        background_tasks.add_task(send_registration_email, email, first_name, fullname,
                                  event_date, event_time, event_city, event_venue_status, event_name)
        
        return JSONResponse(
            status_code=200,
            content={"status": "success", "detail": "user registered"},
        )

    except Exception as e:
        logger.exception("DB update failed: %s", e)
        return JSONResponse(
            status_code=200,
            content={"status": "ignored", "detail": "DB update failed"},
        )

# @app.get("/send-email/")
# async def send_email():
#     first_name = "Virat"
#     last_name = "Kohli"
#     fullname=f"{first_name} {last_name}"
#     email="pratik.ashah676@gmail.com"
#     await send_registration_email(email,first_name,fullname)
#     return {"message": "Email has been sent"}

from sqlalchemy.exc import IntegrityError


@app.get("/test-email")
async def test_email(background_tasks: BackgroundTasks):
    background_tasks.add_task(
        send_registration_email,
        to_email="professionalbuzz@gmail.com",
        firstname="Chintan",
        event_date="15 March 2026",
        event_time="10:00 AM",
        event_city="Bangalore",
        event_venue_status="To be announced",
        event_name="MMML Bangalore"
    )

    return {"status": "ok", "message": "Test email triggered"}


@app.post("/waitlist-registrations/")
async def create_waitlist_registration(
    reg: WaitlistRegistrationCreate,
    db: Session = Depends(get_db)
):
    # check duplicate
    exists = db.query(Contact).filter(Contact.email == reg.email).first()
    if exists:
        exists.status = "waitlisted"
        try:
            db.commit()
            db.refresh(exists)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update status")

        return {
            "status_code": 200,
            "message": "Existing contact updated to waitlisted",
            "data": {"id": exists.id}
        }

    # create contact
    contact = Contact(
        salutation=reg.salutation,
        firstname=reg.first_name,
        lastname=reg.last_name,
        fullname=f"{reg.first_name} {reg.last_name}",
        email=reg.email,
        location=reg.city,
        status="waitlisted",
        years_of_experience="0",          # default since NOT NULL
        dietary_preference="none"         # default since NOT NULL
    )

    # save
    try:
        db.add(contact)
        db.commit()
        db.refresh(contact)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to save")

    return {
        "status_code": 201,
        "message": "Waitlist entry created",
        "data": {"id": contact.id}
    }

@app.post("/membership-applications/")
def submit_membership_application(
    data: MembershipApplicationCreate,
    db: Session = Depends(get_db)
):
    # check duplicate
    exists = db.query(Contact).filter(Contact.email == data.email).first()
    if exists:
        exists.mmml_membership_application = "membership_waitlisted"
        try:
            db.commit()
            db.refresh(exists)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update status")

        return {
            "status_code": 200,
            "message": "Existing contact updated to waitlisted",
            "data": {"id": exists.id}
        }

    # split full name
    parts = data.full_name.strip().split(" ")
    firstname = parts[0]
    lastname = " ".join(parts[1:]) if len(parts) > 1 else ""

    # save into crm_contacts
    entry = Contact(
        fullname=data.full_name,
        firstname=firstname,
        lastname=lastname,
        email=data.email,
        company=data.company,
        linkedin=data.linkedin,
        mmml_membership_application="membership_waitlisted",  # important flag
        years_of_experience="0",
        dietary_preference="none",
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return {
        "status_code": 201,
        "message": "Membership Application submitted successfully",
        "data": {"id": entry.id}
    }



@app.post("/contact-messages/")
async def create_contact_message(message: ContactMessageCreate, db: Session = Depends(get_db)):
    db_message = ContactMessage(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    user_name = f"{message.first_name} {message.last_name}"
    form_data = {
        "salutation": message.salutation,
        "first_name": message.first_name,
        "last_name": message.last_name,
        "email": message.email,
        "company_organization": message.company_organization,
        "message": message.message,
        "created_at": db_message.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    await send_form_submission_emails(
        user_email=message.email,
        user_name=user_name,
        form_type="Contact Message",
        form_data=form_data
    )
    
    return {"message_id": db_message.message_id}

@app.post("/speaker-applications/")
async def create_speaker_application(application: SpeakerApplicationCreate, db: Session = Depends(get_db)):
    existing_registration = db.query(SpeakerApplication).filter(
        SpeakerApplication.email == application.email
    ).first()
    
    if existing_registration:
        return {"status": 405, "detail": "User already exists"}

    if not existing_registration:
        db_application = SpeakerApplication(**application.model_dump())
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
    else:
        db_application = existing_registration

    # existing_contact = db.query(Contact).filter(
    #     Contact.email == application.email
    # ).first()
    
    # if not existing_contact:
    #     db_contact = Contact(
    #         fullname=application.full_name,
    #         salutation=application.salutation,
    #         firstname=None,
    #         lastname=None,
    #         email=application.email,
    #         phone=None,
    #         company=application.company,
    #         designation=application.job_title,
    #         mmml_time = datetime.now(IST),
    #         # mmml='Yes',
    #     )
    #     db.add(db_contact)
    #     db.commit()
    #     db.refresh(db_contact)
    # else :
    #     existing_contact.mmml_time = datetime.now(IST)  # ✅ update timestamp
    #     db.commit()
    
    form_data = {
        "salutation": application.salutation,
        "full_name": application.full_name,
        "email": application.email,
        "company": application.company,
        "job_title": application.job_title,
        "linkedin_profile": application.linkedin_profile,
        "area_of_expertise": application.area_of_expertise,
        "proposed_topic_title": application.proposed_topic_title,
        "topic_description": application.topic_description,
        "speaking_experience": application.speaking_experience,
        "created_at": db_application.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    await send_form_submission_emails(
        user_email=application.email,
        user_name=application.full_name,
        form_type="Speaker Application",
        form_data=form_data
    )
    
    return {"application_id": db_application.application_id}

@app.post("/sponsorship-inquiries/")
async def create_sponsorship_inquiry(inquiry: SponsorshipInquiryCreate, db: Session = Depends(get_db)):
    db_inquiry = SponsorshipInquiry(**inquiry.model_dump())
    db.add(db_inquiry)
    db.commit()
    db.refresh(db_inquiry)
    
    form_data = {
        "company_name": inquiry.company_name,
        "contact_name": inquiry.contact_name,
        "email": inquiry.email,
        "phone": inquiry.phone,
        "company_website": inquiry.company_website,
        "interested_sponsorship_level": inquiry.interested_sponsorship_level,
        "marketing_objectives": inquiry.marketing_objectives,
        "budget_range": inquiry.budget_range,
        "timeline": inquiry.timeline,
        "created_at": db_inquiry.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    await send_form_submission_emails(
        user_email=inquiry.email,
        user_name=inquiry.contact_name,
        form_type="Sponsorship Inquiry",
        form_data=form_data
    )
    
    return {"inquiry_id": db_inquiry.inquiry_id}

@app.post("/partnership-proposals/")
async def create_partnership_proposal(proposal: PartnershipProposalCreate, db: Session = Depends(get_db)):
    db_proposal = PartnershipProposal(**proposal.model_dump())
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    
    form_data = {
        "organization_name": proposal.organization_name,
        "contact_name": proposal.contact_name,
        "email": proposal.email,
        "phone": proposal.phone,
        "organization_website": proposal.organization_website,
        "partnership_type": proposal.partnership_type,
        "partnership_proposal": proposal.partnership_proposal,
        "audience_community": proposal.audience_community,
        "resources_contributed": proposal.resources_contributed,
        "created_at": db_proposal.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    await send_form_submission_emails(
        user_email=proposal.email,
        user_name=proposal.contact_name,
        form_type="Partnership Proposal",
        form_data=form_data
    )
    
    return {"proposal_id": db_proposal.proposal_id}

@app.post("/volunteer-applications/")
async def create_volunteer_application(application: VolunteerApplicationCreate, db: Session = Depends(get_db)):
    existing_registration = db.query(VolunteerApplication).filter(
        VolunteerApplication.email == application.email
    ).first()
    
    if existing_registration:
        return {"status": 405, "detail": "User already exists"}

    if not existing_registration:
        db_application = VolunteerApplication(**application.model_dump())
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
    else:
        db_application = existing_registration

    # existing_contact = db.query(Contact).filter(
    #     Contact.email == application.email
    # ).first()
    
    # if not existing_contact:
    #     db_contact = Contact(
    #         fullname=f"{application.first_name} {application.last_name}",
    #         salutation=application.salutation,
    #         firstname=application.first_name,
    #         lastname=application.last_name,
    #         email=application.email,
    #         phone=application.phone_number,
    #         company=application.company_organization,
    #         designation=application.profession,
    #         mmml_time = datetime.now(IST),
    #         # mmml='Yes',
    #     )
    #     db.add(db_contact)
    #     db.commit()
    #     db.refresh(db_contact)
    # else :
    #     existing_contact.mmml_time = datetime.now(IST)  # ✅ update timestamp
    #     db.commit()
    
    user_name = f"{application.first_name} {application.last_name}"

    form_data = {
        "salutation": application.salutation,
        "first_name": application.first_name,
        "last_name": application.last_name,
        "email": application.email,
        "phone_number": application.phone_number,
        "profession": application.profession,
        "company_organization": application.company_organization,
        "volunteer_experience": application.volunteer_experience,
        "availability": application.availability,
        "relevant_skills_experience": application.relevant_skills_experience,
        "areas_of_interest": application.areas_of_interest,
        "motivation": application.motivation,
        "created_at": db_application.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    
    
    await send_form_submission_emails(
        user_email=application.email,
        user_name=user_name,
        form_type="Volunteer Application",
        form_data=form_data
    )
    
    return {"application_id": db_application.application_id}

if __name__ == "__main__":
    print("🚀 Starting MMML Backend Server...")
    print("📖 API Documentation available at: http://localhost:8000/docs")
    print("🌐 Server will be running at: http://localhost:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)    