import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import settings


def _send_html_email(to_email: str, subject: str, html_body: str) -> None:
        if not settings.mail_username or not settings.mail_password:
            raise RuntimeError("Email not configured: set MAIL_USERNAME and MAIL_PASSWORD in env/.env.")
        if not settings.mail_from:
            raise RuntimeError("Email not configured: set MAIL_FROM in env/.env.")

        msg = MIMEMultipart("alternative")
        msg["From"] = settings.mail_from
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(settings.mail_host, settings.mail_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.mail_username, settings.mail_password)
            server.sendmail(settings.mail_from, [to_email], msg.as_string())

def notify_welcome(email, verify_link: str) -> None:
        subject = "Welcome to CVGram 👋"
        body = f"""
        <html><body style="font-family: Arial, sans-serif; line-height: 1.5;">
          <h2>Welcome to CVGram!</h2>
          <p>Thanks for signing up. One quick step:</p>
          <p>
            <a href="{settings.app_base_url + '/verify-mail/' +verify_link}"
               style="display:inline-block;padding:10px 14px;text-decoration:none;border-radius:8px;">
              Verify your email
            </a>
          </p>
          <p>If you didn’t create this account, you can safely ignore this email.</p>
          <p style="font-size: 12px; opacity: 0.8;">
            Need help? Contact us at {settings.support_email}
          </p>
        </body></html>
        """
        _send_html_email(email, subject, body)

def notify_new_login(email, when_text: str, device_text: str, reset_link: str) -> None:
        subject = "New login to your CVGram account"
        body = f"""
        <html><body style="font-family: Arial, sans-serif; line-height: 1.5;">
          <p>Hi ,</p>
          <p>We noticed a new login to your CVGram account.</p>
          <ul>
            <li><strong>When:</strong> {when_text}</li>
            <li><strong>Device:</strong> {device_text}</li>
          </ul>
          <p>If this was you, you’re all set.</p>
          <p>If not, reset your password right away:</p>
          <p>
            <a href="{reset_link}"
               style="display:inline-block;padding:10px 14px;text-decoration:none;border-radius:8px;">
              Reset password
            </a>
          </p>
          <p style="font-size: 12px; opacity: 0.8;">
            Need help? {settings.support_email}
          </p>
        </body></html>
        """
        _send_html_email(email, subject, body)

def notify_password_reset(email, reset_link: str) -> None:
        subject = "Reset your CVGram password"
        body = f"""
        <html><body style="font-family: Arial, sans-serif; line-height: 1.5;">
          <p>Hi,</p>
          <p>We received a request to reset your CVGram password.</p>
          <p>
            <a href="{settings.app_base_url + '/password/reset/' +reset_link}"
               style="display:inline-block;padding:10px 14px;text-decoration:none;border-radius:8px;">
              Reset password
            </a>
          </p>
          <p>If you didn’t request this, you can ignore this email.</p>
          <p style="font-size: 12px; opacity: 0.8;">
            Need help? {settings.support_email}
          </p>
        </body></html>
        """
        _send_html_email(email, subject, body)
