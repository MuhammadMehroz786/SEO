import smtplib
import logging
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.conf import settings

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self, config):
        self.config = config

    def send(self, to_email: str, subject: str, body: str):
        if self.config.preferred_method == "gmail":
            self._send_gmail(to_email, subject, body)
        else:
            self._send_smtp(to_email, subject, body)

    def _send_smtp(self, to_email: str, subject: str, body: str):
        msg = MIMEMultipart()
        msg["From"] = self.config.smtp_from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(self.config.smtp_username, self.config.smtp_password)
            server.sendmail(self.config.smtp_from_email, to_email, msg.as_string())
        logger.info("Sent email via SMTP to %s", to_email)

    def _send_gmail(self, to_email: str, subject: str, body: str):
        import google.auth.transport.requests
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials(
            token=None,
            refresh_token=self.config.gmail_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )
        request = google.auth.transport.requests.Request()
        creds.refresh(request)

        service = build("gmail", "v1", credentials=creds)

        msg = MIMEText(body, "plain")
        msg["From"] = self.config.gmail_email
        msg["To"] = to_email
        msg["Subject"] = subject

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        logger.info("Sent email via Gmail to %s", to_email)


def get_gmail_auth_url(store_id: int) -> str:
    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/gmail.send"],
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        state=str(store_id),
    )
    return auth_url


def exchange_gmail_code(code: str, store) -> str:
    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/gmail.send"],
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    flow.fetch_token(code=code)
    creds = flow.credentials

    from googleapiclient.discovery import build as g_build
    service = g_build("oauth2", "v2", credentials=creds)
    user_info = service.userinfo().get().execute()
    gmail_email = user_info.get("email", "")

    from backlinks.models import EmailConfig
    config, _ = EmailConfig.objects.get_or_create(store=store)
    config.gmail_refresh_token = creds.refresh_token
    config.gmail_email = gmail_email
    config.preferred_method = "gmail"
    config.save()
    return gmail_email
