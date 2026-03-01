import base64
import os.path
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]

def send_email(service, to, subject, body):
    message = EmailMessage()

    message["To"] = to
    message["From"] = "me"
    message["Subject"] = subject

    # Plain text fallback (strip tags if you want something smarter)
    message.set_content("This email requires an HTML-capable client.")

    # HTML body
    message.add_alternative(body, subtype="html")

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    create_message = {"raw": encoded_message}

    send_message = service.users().messages().send(
        userId="me", body=create_message
    ).execute()

    print("Message Id:", send_message["id"])

def generate_creds():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server()
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        return build("gmail", "v1", credentials=creds)
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


if __name__ == "__main__":
    creds = generate_creds()
    send_email(creds, "adar.wasserman@gmail.com", "Test Mail", "This is working!")
