import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import dotenv
import os
try:
    import pywhatkit
except ImportError:
    pywhatkit = None
import json
import re
from backend.TextToSpeech import speak
from backend.Chatbot import Chatbot

dotenv.load_dotenv()

def extract_email_info(query):
    """Uses AI to extract To, Subject, and Details from the user's natural language query."""
    prompt = (
        f"Extract email details from this query: '{query}'. "
        "Return ONLY a JSON object with keys: 'to', 'subject', and 'details'. "
        "Example JSON: {'to': 'test@gmail.com', 'subject': 'Sick Leave', 'details': 'I am ill'}"
    )
    try:
        response = Chatbot(prompt)
        json_match = re.search(r"\{.*\}", response.replace("\n", " "), re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return {"to": "", "subject": "", "details": ""}
    except Exception as e:
        print(f"Extraction Error: {e}")
        return {"to": "", "subject": "", "details": ""}

def generate_email_body_ai(subject, details):
    """Generates a professional email body and converts markdown to HTML tags."""
    prompt = (
        f"Write a professional yet warm email with the subject '{subject}'. "
        f"Context: {details}. "
        "FORMATTING RULES:\n"
        "1. Start with 'Dear [Name/Sir/Madam],'\n"
        "2. Follow with 'I hope you are doing well.'\n"
        "3. Sign off as 'Rohit Mandal'.\n"
        "4. Provide ONLY the email body text. Use standard formatting."
    )
    speak("Drafting your email and applying HTML formatting.")
    body = Chatbot(prompt)
    
    # 1. Convert **text** to <b>text</b> using Regex
    body = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', body)
    
    # 2. Convert all types of newlines to <br>
    body = body.replace('\\n', '<br>').replace('\n', '<br>')
    
    return body

def ask_confirmation(details_summary):
    # Strip tags for a clean console preview
    clean_preview = re.sub('<[^<]+?>', '', details_summary.replace('<br>', '\n'))
    print(f"\n[Preview]:\n{clean_preview}")
    speak("I have prepared the draft. Please review the content on the screen.")
    speak("Should I send this? Say yes or no.")
    choice = input("\n[Security]: Send? (yes/no): ").strip().lower()
    return "yes" in choice or "y" in choice

def send_mail(query=None):
    sender_email = os.getenv('SENDER_EMAIL', "").replace('"', '').replace("'", "").strip()
    sender_password = os.getenv('EMAIL_PASSWORD', "").replace('"', '').replace("'", "").strip().replace(" ", "")
    
    if not sender_email or not sender_password:
        speak("Email configuration is missing.")
        print("Error: SENDER_EMAIL or EMAIL_PASSWORD not found in .env")
        return
    
    # Try to extract info if a query was provided
    extracted = extract_email_info(query) if query else {"to": "", "subject": "", "details": ""}
    
    receiver_email = extracted.get("to", "")
    if not receiver_email or "@" not in str(receiver_email):
        speak("Who is the recipient?")
        receiver_email = input("Enter receiver's email address: ").strip()
    
    subject = extracted.get("subject", "")
    if not subject:
        speak("What is the subject?")
        subject = input("Enter subject: ").strip()
        
    details = extracted.get("details", "")
    if not details:
        speak("What are the details?")
        details = input("Enter specific details: ").strip()
    
    # Generate the body which already contains <b> and <br>
    body_html = generate_email_body_ai(subject, details)
    full_html = f"<html><body style='font-family: Arial, sans-serif; line-height: 1.6;'>{body_html}</body></html>"
    
    if ask_confirmation(body_html):
        message = MIMEMultipart("alternative")
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(full_html, 'html'))

        try:
            print(f"[DEBUG]: Attempting login for {sender_email}...")
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            print('Email sent successfully!')
            speak("Email has been sent.")
        except Exception as e:
            print(f"Error: {e}")
            speak("Failed to send. Check credentials.")
    else:
        speak("Operation cancelled.")

def send_whatsapp():
    if not pywhatkit:
        speak("WhatsApp automation is not supported in this environment.")
        print("Error: pywhatkit not installed or supported.")
        return

    speak("What is the phone number?")
    phone_number = input("Enter Phone Number: ").strip()
    speak("What is the message?")
    message = input("Enter Message: ").strip()

    summary = f"To WhatsApp: {phone_number}\nMessage: {message}"
    if ask_confirmation(summary):
        try:
            speak("Sending WhatsApp message.")
            pywhatkit.sendwhatmsg_instantly(phone_number, message)
        except Exception as e:
            print('Error:', str(e))
            speak("WhatsApp failed.")
    else:
        speak("Cancelled.")
