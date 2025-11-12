import json
from datetime import datetime, timedelta, timezone

import pytest

from email_cleaner_lambda import gmail_api_access


class TestGmailApi:

    def test_send_email(self, mocker):

        now_utc = datetime.now(timezone.utc) + timedelta(days=1)

        # Generate a valid expiry date for the API token
        iso_string_with_z = now_utc.isoformat(timespec="milliseconds").replace(
            "+00:00", "Z"
        )

        return_value = {
            "id": "123",
            "threadId": "123",
            "labelIds": ["UNREAD", "CATEGORY_PERSONAL", "SENT", "INBOX"],
        }

        mocker.patch(
            "email_cleaner_lambda.gmail_api_access.GmailAPI.send_email",
            return_value=return_value,
        )

        parameter_value = json.dumps(
            {
                "token": "cp9N551MwPYYc9DyCzmqhY/",
                "refresh_token": "wCipCsTX5jMzEKT3ggwtDSGgk",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "8585973-Gut4pNrtpVZX3SVVoM.apps.googleusercontent.com",
                "client_secret": "GOCSPX-1S/YqyFkMoN2xLvxFYrRixJ1trE0",
                "scopes": ["https://www.googleapis.com/auth/gmail.modify"],
                "universe_domain": "googleapis.com",
                "account": "",
                "expiry": iso_string_with_z,
            }
        )

        SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
        gmail_api = gmail_api_access.GmailAPI(SCOPES, parameter_value)

        response = gmail_api.send_email("test email")

        assert response == return_value

    @pytest.mark.xfail
    def test_send_email_expired_token(self, mocker):

        now_utc = datetime.now(timezone.utc) - timedelta(days=1)

        # Generate a valid expiry date for the API token
        iso_string_with_z = now_utc.isoformat(timespec="milliseconds").replace(
            "+00:00", "Z"
        )

        return_value = {
            "id": "123",
            "threadId": "123",
            "labelIds": ["UNREAD", "CATEGORY_PERSONAL", "SENT", "INBOX"],
        }

        mocker.patch(
            "email_cleaner_lambda.gmail_api_access.GmailAPI.send_email",
            return_value=return_value,
        )

        parameter_value = json.dumps(
            {
                "token": "cp9N551MwPYYc9DyCzmqhY/",
                "refresh_token": "wCipCsTX5jMzEKT3ggwtDSGgk",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "8585973-Gut4pNrtpVZX3SVVoM.apps.googleusercontent.com",
                "client_secret": "GOCSPX-1S/YqyFkMoN2xLvxFYrRixJ1trE0",
                "scopes": ["https://www.googleapis.com/auth/gmail.modify"],
                "universe_domain": "googleapis.com",
                "account": "",
                "expiry": iso_string_with_z,
            }
        )

        SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
        gmail_api = gmail_api_access.GmailAPI(SCOPES, parameter_value)

        response = gmail_api.send_email("test email")

        assert response == return_value
