import json

import boto3
from moto import mock_aws

import email_cleaner_lambda.aws_access as aws_access


@mock_aws
class TestAwsClass:
    def ssm_setup(self):
        # Set up the mock SSM environment
        self.update_token = {
            "token": "cp9N551MwPYYc9DyCzmqhY/",
            "refresh_token": "wCipCsTX5jMzEKT3ggwtDSGgk",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "Gut4pNrtpVZX3SVVoM.apps.googleusercontent.com",
            "client_secret": "1S/YqyFkMoN2xLvxFYrRixJ1trE0",
            "scopes": ["https://www.googleapis.com/auth/gmail.modify"],
            "universe_domain": "googleapis.com",
            "account": "",
            "expiry": "2025-11-06T13:28:00.555555Z",
        }

        ssm_client = boto3.client("ssm")
        ssm_client.put_parameter(
            Name="mail_credentials",
            Description="refresh token",
            Value=json.dumps(self.update_token),
            Type="SecureString",
        )

        return ssm_client

    def ses_setup(self):

        ses_client = boto3.client("ses")
        ses_client.verify_email_identity(EmailAddress="ruwanindika@gmail.com")

    def test_aws_parameter_store_access(self):
        print(" --> Testing refresh token access")

        self.ssm_setup()

        aws_access_obj = aws_access.AwsAccess()

        parameter_value = aws_access_obj.get_secret("mail_credentials")

        assert parameter_value == json.dumps(self.update_token)

    def test_aws_parameter_store_access_exception(self):
        print(" --> Testing refresh token access")

        self.ssm_setup()

        aws_access_obj = aws_access.AwsAccess()

        parameter_value = aws_access_obj.get_secret("mail_credentials1")

        # print("parameter_value-->", parameter_value)

        assert parameter_value == "Parameter 'mail_credentials1' not found."

    def test_aws_parameter_store_update(self):
        print(" --> Testing updating token")

        self.ssm_setup()

        aws_access_obj = aws_access.AwsAccess()

        return_val = aws_access_obj.update_token_in_parameter_store(
            json.dumps(self.update_token)
        )

        assert return_val == {
            "statusCode": 200,
            "body": "Parameter 'mail_credentials' updated.",
        }

    def test_aws_parameter_store_update_exception(self):
        print(" --> Testing updating token")

        self.ssm_setup()

        aws_access_obj = aws_access.AwsAccess()

        return_val = aws_access_obj.update_token_in_parameter_store(
            json.dumps(self.update_token), "mail_credentials1"
        )

        print("return_val - akjshdjkasd -->", return_val)

        # assert return_val == {
        #     "statusCode": 200,
        #     "body": "Parameter 'mail_credentials' updated.",
        # }

    def test_send_email_aws(self):

        self.ses_setup()

        aws_access_obj = aws_access.AwsAccess()

        email_response = aws_access_obj.send_email_aws("email test")

        assert email_response == {"statusCode": 200, "body": "Email sent successfully!"}

    def test_send_email_aws_excetion(self):

        self.ses_setup()

        aws_access_obj = aws_access.AwsAccess()

        email_response = aws_access_obj.send_email_aws(
            "email test", sender_email="ruwanindika@gmail.con"
        )

        assert email_response == {
            "statusCode": 500,
            "body": "Error sending email: An error occurred (MessageRejected) when calling the SendEmail operation: Email address not verified ruwanindika@gmail.con",
        }
