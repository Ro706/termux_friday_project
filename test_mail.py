import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

def test_login():
    email = os.getenv('SENDER_EMAIL')
    password = os.getenv('EMAIL_PASSWORD')

    if not email or not password:
        print("ERROR: Missing SENDER_EMAIL or EMAIL_PASSWORD in .env")
        return

    # Deep clean
    email = email.replace('"', '').replace("'", "").strip()
    password = password.replace('"', '').replace("'", "").strip().replace(" ", "")

    print(f"Testing Login for: {email}")
    print(f"Password Length: {len(password)} (Should be 16)")
    
    try:
        print("Connecting to Gmail (Port 465)...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(email, password)
        print("SUCCESS: Login successful! Your credentials are correct.")
        server.quit()
    except Exception as e:
        print(f"FAILURE: {e}")
        print("\nCommon Fixes:")
        print("1. Ensure 2-Step Verification is ON for " + email)
        print("2. Generate a NEW App Password specifically for this account.")
        print("3. Ensure SENDER_EMAIL in .env is EXACTLY the account that generated the password.")

if __name__ == "__main__":
    test_login()
