from __future__ import annotations

import base64
import json
from email.message import EmailMessage
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def send_json_email(
    to_address: str,
    report: dict[str, object],
    credentials: str,
    token: str,
) -> None:
    creds = _load_credentials(credentials, token)
    from googleapiclient.discovery import build

    message = EmailMessage()
    message["To"] = to_address
    message["Subject"] = "InternalGameJSON"
    message.set_content(json.dumps(report, ensure_ascii=False))
    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
    build("gmail", "v1", credentials=creds).users().messages().send(
        userId="me", body={"raw": encoded}
    ).execute()


def _load_credentials(credentials_path: str, token_path: str):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    token_file = Path(token_path)
    creds = (
        Credentials.from_authorized_user_file(token_file, SCOPES)
        if token_file.exists()
        else None
    )
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json(), encoding="utf-8")
    return creds
