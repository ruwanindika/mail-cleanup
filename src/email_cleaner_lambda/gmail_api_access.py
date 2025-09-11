import base64
import json
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailAPI:
    def __init__(self, SCOPES, parameter_value):
        self.SCOPES = SCOPES
        self.parameter_value = parameter_value
        self.creds = None

        # def oauth(self, parameter_value):

        self.creds = Credentials.from_authorized_user_info(
            json.loads(self.parameter_value), self.SCOPES
        )
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())

    def search_and_delete(self, seach_q, maxResults):

        number_of_emails_deleted = 0

        try:

            service = build("gmail", "v1", credentials=self.creds)
            results = (
                service.users()
                .messages()
                .list(userId="me", maxResults=maxResults, q=seach_q)
                .execute()
            )

            if "messages" in results.keys():
                for msg in results["messages"]:
                    list_emails_results = (
                        service.users()
                        .messages()
                        .get(userId="me", id=msg["id"])
                        .execute()
                    )

                    header_list = list_emails_results["payload"]["headers"]
                    for i in header_list:
                        if i["name"] == "Subject":
                            email_subject = i["value"]

                        if i["name"] == "From":
                            email_from = i["value"]

                    # print(f"{email_from} --> {email_subject}")
                    # print()

                    del_results = (
                        service.users()
                        .messages()
                        .trash(userId="me", id=msg["id"])
                        .execute()
                    )

                    if del_results:
                        number_of_emails_deleted = number_of_emails_deleted + 1

                print(seach_q, ":", number_of_emails_deleted)

            else:
                print(f"No messages for : {seach_q}")

        except HttpError as error:
            print(f"An error occurred: {error}")

        return number_of_emails_deleted

    def send_email(self, email_content):

        try:
            service = build("gmail", "v1", credentials=self.creds)
            message = EmailMessage()

            message.set_content(email_content)

            message["To"] = "ruwanindika@gmail.com"
            message["From"] = "ruwanindika@gmail.com"
            message["Subject"] = "email deletion report"

            # encoded message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {"raw": encoded_message}
            # pylint: disable=E1101
            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            # print(f'Message Id: {send_message["id"]}')
        except HttpError as error:
            print(f"An error occurred: {error}")
            send_message = None
        return send_message
