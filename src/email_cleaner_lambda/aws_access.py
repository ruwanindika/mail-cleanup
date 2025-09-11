import boto3


class AwsAccess:

    def __init__(self):
        self.ssm_client = boto3.client("ssm")
        self.ses_client = boto3.client("ses")

    def send_email_aws(self, body_text):

        sender_email = "ruwanindika@gmail.com"
        recipient_email = "recipient@example.com"
        subject = "Email deletion report"

        try:
            response = self.ses_client.send_email(
                Source=sender_email,
                Destination={"ToAddresses": ["ruwanindika@gmail.com"]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": body_text}},
                },
            )
            print(f"Email sent! Message ID: {response['MessageId']}")
            return {"statusCode": 200, "body": "Email sent successfully!"}
        except Exception as e:
            print(f"Error sending email: {e}")
            return {"statusCode": 500, "body": f"Error sending email: {e}"}

    def update_token_in_parameter_store(self, new_value):
        parameter_name = "mail_credentials"

        parameter_type = "SecureString"

        try:
            response = self.ssm_client.put_parameter(
                Name=parameter_name,
                Value=new_value,
                Type=parameter_type,
                Overwrite=True,  # Set to True to update an existing parameter
            )
            print(
                f"Parameter '{parameter_name}' updated successfully. Version: {response['Version']}"
            )
            return {"statusCode": 200, "body": f"Parameter '{parameter_name}' updated."}
        except Exception as e:
            print(f"Error updating parameter: {e}")
            return {"statusCode": 500, "body": f"Error updating parameter: {e}"}

    def get_secret(self, parameter_name):

        try:
            response = self.ssm_client.get_parameter(
                Name=parameter_name,
                WithDecryption=True,  # Set to True for SecureString parameters
            )
            parameter_value = response["Parameter"]["Value"]
        except self.ssm_client.exceptions.ParameterNotFound:
            print(f"Parameter '{parameter_name}' not found.")
        except Exception as e:
            print(f"Error retrieving parameter: {e}")

        return parameter_value
