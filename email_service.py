import os
from typing import Dict, Any
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email configuration
EMAIL_CONFIG = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "noreply@example.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "password"),
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@example.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
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
