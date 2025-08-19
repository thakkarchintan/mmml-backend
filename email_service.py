import os
from typing import Dict, Any
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get SMTP settings
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))

# Determine SSL/TLS settings based on port
if MAIL_PORT == 587:
    # For port 587, use STARTTLS
    MAIL_STARTTLS = True
    MAIL_SSL_TLS = False
elif MAIL_PORT == 465:
    # For port 465, use SSL
    MAIL_STARTTLS = False
    MAIL_SSL_TLS = True
else:
    # For other ports, try STARTTLS by default
    MAIL_STARTTLS = True
    MAIL_SSL_TLS = False

# Email configuration with proper SSL/TLS settings
EMAIL_CONFIG = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "noreply@example.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "password"),
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@example.com"),
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
    USE_CREDENTIALS=True
)

# Initialize FastMail
fastmail = FastMail(EMAIL_CONFIG)

# Admin email address
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@mmml.com")

# Email templates
def get_email_template(template_name: str, context: Dict[str, Any]) -> str:
    """Render email template with given context"""
    template_dir = Path(__file__).parent / "email_templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(f"{template_name}.html")
    return template.render(**context)

async def send_user_confirmation_email(user_email: str, user_name: str, form_type: str, form_data: Dict[str, Any]):
    """Send confirmation email to user"""
    subject = f"Thank you for your {form_type} submission"
    
    # Create email context
    context = {
        "user_name": user_name,
        "form_type": form_type,
        "form_data": form_data,
        "submission_date": form_data.get("created_at", "today")
    }
    
    # Render email body
    html_content = get_email_template("user_confirmation", context)
    
    message = MessageSchema(
        subject=subject,
        recipients=[user_email],
        body=html_content,
        subtype="html"
    )
    
    await fastmail.send_message(message)

async def send_admin_notification_email(form_type: str, form_data: Dict[str, Any]):
    """Send notification email to admin"""
    subject = f"New {form_type} submission received"
    
    # Create email context
    context = {
        "form_type": form_type,
        "form_data": form_data,
        "submission_date": form_data.get("created_at", "today")
    }
    
    # Render email body
    html_content = get_email_template("admin_notification", context)
    
    message = MessageSchema(
        subject=subject,
        recipients=[ADMIN_EMAIL],
        body=html_content,
        subtype="html"
    )
    
    await fastmail.send_message(message)

async def send_registration_acknowledgement_email(user_email: str, first_name: str, event_date: str):
    """Send acknowledgement email after registration submission"""
    subject = f"Thank you for registering for MMML {event_date}"
    
    # Create email context
    context = {
        "first_name": first_name,
        "event_date": event_date
    }
    
    # Render email body
    html_content = get_email_template("registration_acknowledgement", context)
    
    message = MessageSchema(
        subject=subject,
        recipients=[user_email],
        body=html_content,
        subtype="html"
    )
    
    await fastmail.send_message(message)

async def send_registration_approved_email(user_email: str, first_name: str, event_date: str, secure_spot_link: str):
    """Send approval email with secure spot link"""
    subject = f"Your MMML {event_date} Registration is Approved 🎉"
    
    # Create email context
    context = {
        "first_name": first_name,
        "event_date": event_date,
        "secure_spot_link": secure_spot_link
    }
    
    # Render email body
    html_content = get_email_template("registration_approved", context)
    
    message = MessageSchema(
        subject=subject,
        recipients=[user_email],
        body=html_content,
        subtype="html"
    )
    
    await fastmail.send_message(message)

async def send_registration_rejected_email(user_email: str, first_name: str, event_date: str):
    """Send rejection email with reapplication option"""
    subject = f"Update on Your MMML {event_date} Registration"
    
    # Create email context
    context = {
        "first_name": first_name,
        "event_date": event_date
    }
    
    # Render email body
    html_content = get_email_template("registration_rejected", context)
    
    message = MessageSchema(
        subject=subject,
        recipients=[user_email],
        body=html_content,
        subtype="html"
    )
    
    await fastmail.send_message(message)

async def send_form_submission_emails(user_email: str, user_name: str, form_type: str, form_data: Dict[str, Any]):
    """Send emails to both user and admin for form submission"""
    try:
        # Send confirmation to user
        await send_user_confirmation_email(user_email, user_name, form_type, form_data)
        
        # Send notification to admin
        await send_admin_notification_email(form_type, form_data)
        
        return True
    except Exception as e:
        print(f"Error sending emails: {e}")
        return False
