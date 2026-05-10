"""Email sending utilities (single message and batch)."""

from __future__ import annotations

import smtplib
import ssl
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Optional


class Email:
    """Send single or batch emails via SMTP with optional attachments."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        use_ssl: bool = True,
        use_tls: bool = False,
    ) -> None:
        """Initialise the email sender with SMTP credentials.

        Args:
            smtp_host: SMTP server hostname (e.g. ``"smtp.gmail.com"``).
            smtp_port: SMTP server port (e.g. 465 for SSL, 587 for TLS).
            username:  Login username (usually your email address).
            password:  Login password or app-specific password.
            use_ssl:   Use SMTP_SSL for the connection (port 465 typical).
            use_tls:   Use STARTTLS after plain connection (port 587 typical).
                       Ignored when *use_ssl* is True.
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.use_tls = use_tls

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self) -> smtplib.SMTP | smtplib.SMTP_SSL:
        ctx = ssl.create_default_context()
        if self.use_ssl:
            server: smtplib.SMTP | smtplib.SMTP_SSL = smtplib.SMTP_SSL(
                self.smtp_host, self.smtp_port, context=ctx
            )
        else:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            if self.use_tls:
                server.starttls(context=ctx)
        server.login(self.username, self.password)
        return server

    @staticmethod
    def _build_message(
        sender: str,
        recipient: str,
        subject: str,
        body: str,
        html: bool = False,
        attachments: Optional[List[str]] = None,
    ) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = subject
        mime_type = "html" if html else "plain"
        msg.attach(MIMEText(body, mime_type, "utf-8"))

        for path in attachments or []:
            p = Path(path)
            with open(p, "rb") as f:
                part = MIMEApplication(f.read(), Name=p.name)
            part["Content-Disposition"] = f'attachment; filename="{p.name}"'
            msg.attach(part)

        return msg

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def send(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
        attachments: Optional[List[str]] = None,
        sender: Optional[str] = None,
    ) -> None:
        """Send an email to a single recipient.

        Args:
            to:          Recipient email address.
            subject:     Email subject line.
            body:        Email body (plain text or HTML).
            html:        Set to True if *body* is HTML.
            attachments: Optional list of file paths to attach.
            sender:      Sender address. Defaults to *username*.
        """
        from_addr = sender or self.username
        msg = self._build_message(
            from_addr, to, subject, body, html=html, attachments=attachments
        )
        with self._connect() as server:
            server.sendmail(from_addr, to, msg.as_string())

    def send_batch(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        html: bool = False,
        attachments: Optional[List[str]] = None,
        sender: Optional[str] = None,
    ) -> dict[str, str]:
        """Send the same email to multiple recipients.

        A single SMTP connection is reused for all recipients. Failures for
        individual recipients are collected and returned rather than raising
        immediately, so that remaining recipients are still attempted.

        Args:
            recipients:  List of recipient email addresses.
            subject:     Email subject line.
            body:        Email body (plain text or HTML).
            html:        Set to True if *body* is HTML.
            attachments: Optional list of file paths to attach.
            sender:      Sender address. Defaults to *username*.

        Returns:
            Dict mapping failed recipient addresses to their error messages.
            An empty dict means all messages were sent successfully.
        """
        from_addr = sender or self.username
        errors: dict[str, str] = {}

        with self._connect() as server:
            for to in recipients:
                try:
                    msg = self._build_message(
                        from_addr, to, subject, body,
                        html=html, attachments=attachments,
                    )
                    server.sendmail(from_addr, to, msg.as_string())
                except Exception as exc:  # noqa: BLE001
                    errors[to] = str(exc)

        return errors
