import os
from typing import Dict, Any
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from dotenv import load_dotenv
from email.utils import formataddr

# Load environment variables
load_dotenv()

# Email configuration
EMAIL_CONFIG = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "noreply@example.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "password"),
    MAIL_FROM="hello@mmml.co.in",
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
        subtype="html",
        from_name="MMML"
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
        subtype="html",
        from_name="MMML"
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
        subtype="html",
       from_name="MMML"
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
        subtype="html",
       from_name="MMML"
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
        subtype="html",
        from_name="MMML"
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
    
async def send_registration_email(to_email: str, firstname: str = None, fullname: str = None , 
                                  event_date: str = None , event_time: str = None , 
                                  event_city: str = None , event_venue_status: str = None,
                                  event_name: str = None):
    name = firstname if firstname else fullname if fullname else "Participant"

    subject = f"Registration Confirmation | {event_name}"

    body = f"""
    <p>Dear {name},</p>

    <p>Thank you for registering for {event_name} — we’re excited to have you join us.</p>

    <p>MMML brings together growth-minded individuals who care about long-term 
    thinking, real decision-making, and learning from people who’ve actually been in the arena. 
    We’re glad you’ll be part of the conversation.</p>
    
    <p>Here are the event details:</p>
    
    <ul>
        <li>Event: {event_name}</li>
        <li>Date: {event_date}</li>
        <li>Time: {event_time}</li>
        <li>Location: {event_city}</li>
        <li>Venue: {event_venue_status}</li>
    </ul>
    
    <p>We’ll share further updates, including venue and event-related information, closer to the event.</p>
    
    <p>To stay in the loop, you can:</p>
    <ul>
        <li>Follow MMML on LinkedIn: <a href="https://www.linkedin.com/company/mmml">https://www.linkedin.com/company/mmml</a></li>
        <li>Join the MMML WhatsApp community: <a href="https://chat.whatsapp.com/BbewxC91NUAEFHOeKQkGuz">https://chat.whatsapp.com/BbewxC91NUAEFHOeKQkGuz</a></li>
    </ul>

    
    <p>We’re always looking to grow this community thoughtfully. 
    If you know friends or colleagues who’d benefit from conversations like these, 
    feel free to share the event with them.</p>

    <p>If you have any questions or need support at any point, please reach out to us at 
        <a href="mailto:hello@mmml.co.in">hello@mmml.co.in</a>
    </p>
    
    <p>Looking forward to seeing you at the event.</p>

    <p>Warm regards,<br>Team MMML</p>
    """

    message = MessageSchema(
        subject=subject,
        recipients=[to_email],
        body=body,
        subtype="html" , # can use "html" if you want rich formatting
        from_name="MMML"
    )

    await fastmail.send_message(message)
