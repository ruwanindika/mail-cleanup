import base64
import json
from email.message import EmailMessage

import boto3
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def send_email_aws(body_text):
    ses_client = boto3.client("ses")

    sender_email = "ruwanindika@gmail.com"
    recipient_email = "recipient@example.com"
    subject = "Email deletion report"

    try:
        response = ses_client.send_email(
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


def update_token_in_parameter_store(ssm_client, new_value):
    parameter_name = "mail_credentials"

    parameter_type = "SecureString"

    try:
        response = ssm_client.put_parameter(
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


def get_secret(ssm_client):

    parameter_name = "mail_credentials"
    try:
        response = ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=True,  # Set to True for SecureString parameters
        )
        parameter_value = response["Parameter"]["Value"]
    except ssm_client.exceptions.ParameterNotFound:
        print(f"Parameter '{parameter_name}' not found.")
    except Exception as e:
        print(f"Error retrieving parameter: {e}")

    return parameter_value


def search_and_delete(seach_q, creds, maxResults):

    number_of_emails_deleted = 0

    try:

        service = build("gmail", "v1", credentials=creds)
        results = (
            service.users()
            .messages()
            .list(userId="me", maxResults=maxResults, q=seach_q)
            .execute()
        )

        if "messages" in results.keys():
            for msg in results["messages"]:
                list_emails_results = (
                    service.users().messages().get(userId="me", id=msg["id"]).execute()
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

            # print(del_results)
            # print()

        else:
            print(f"No messages for : {seach_q}")

    except HttpError as error:
        print(f"An error occurred: {error}")

    return number_of_emails_deleted


def oauth(SCOPES, parameter_value):
    creds = None

    creds = Credentials.from_authorized_user_info(json.loads(parameter_value), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    return creds


def send_email(creds, email_content):

    try:
        service = build("gmail", "v1", credentials=creds)
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
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        # print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message


def lambda_handler(event, context):

    email_report_list = []

    number_of_emails_deleted = 0

    ssm_client = boto3.client("ssm")

    parameter_value = get_secret(ssm_client)

    SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

    creds = oauth(SCOPES, parameter_value)

    update_token_in_parameter_store(ssm_client, creds.to_json())

    maxResults = 500

    query_list = [
        "from:info@fastimpressions.com.au",
        "from:ebill@dialog.lk",
        "from:openhouse-group.com",
        "from:Sandaru.Gunasekara@sgs.com",
        "from:deals@livingsocial.com",
        "from:subscriptions@message.bloomberg.com",
        "from:boconlinebanking@boc.lk",
        "from:HNBAlerts@hnb.lk",
        "from:no-reply@mail.instagram.com",
        "from:no-reply@mail.goodreads.com",
        "from:groups-noreply@linkedin.com",
        "from:flysmilesupdates@srilankan.com",
        "from:noreply@ondemandmsg.sbs.com.au",
        "from:jobalerts-noreply@linkedin.com",
        "from:velocity@e.velocityfrequentflyer.com",
        "from:newsletters@fishpond.com.au",
        "from:eservice@mh1.evaair.com",
        "from:info@mailer.netflix.com",
        "from:comment-reply@wordpress.com",
        "from:no-reply@primevideo.com",
        "from:noreply@news.delonghi.com",
        "from:promo@oncredit.lk",
        "from:no-reply@extremecloudiq.com",
        "from:no-reply@e.siriusxm.com",
        "from:web.jms@keells.com",
        "from:invitationtoapply-au@match.indeed.com",
        "from:no-reply@channels.primevideo.com",
        "from:hello@email.m.bigw.com.au",
        "from:ana-asia-oceania@121.ana.co.jp",
        "from:update+mihpmuki@facebookmail.com",
        "from:sampathotp@sampath.lk",
        "subject: email deletion report from:ruwanindika@gmail.com to:ruwanindika@gmail.com",
        "from:carsales@mail.carsales.com.au",
        "from:shipment-tracking@amazon.com.au",
        "from:store-news@amazon.com.au",
        "from:flybuys@edm.flybuys.com.au",
        "from:smbc_info@msg.smbc.co.jp",
        "from:myqinfo@info.chamberlain.com",
        "from:didi@jp.didiglobal.com",
        "from:order-update@amazon.com.au older_than:15d",
        "from:estatement@info.nationstrust.com",
        "from:estatements@ndbbank.com",
        "from:newsletter@m.finder.com.au",
        "from:noreply@mail.schoolbytes.education older_than:60d",
        "from:donotreply@afterpay.com older_than:30d",
        "from auto-confirm@amazon.com.au older_than:15d",
        "from:no-reply@amazon.com.au older_than:15d",
        "from:eBayDeals@e.deals.ebay.com.au",
        "from:qantasff@e.qantas.com",
        "from:jobs-listings@linkedin.com",
        "from:promotion@aliexpress.com",
        "from:notifications-noreply@linkedin.com older_than:15d",
        "from:store-news@amazon.co.jp older_than:5d",
        "from:auto-confirm@amazon.co.jp older_than:15d",
        "from:shipment-tracking@amazon.co.jp older_than:15d",
        "from:aquinasadmin@aquinas.edu.au subject:Schedule Report",
        "from:no-reply@employmenthero.com subject:Security alert older_than:15d",
        "from:messages-noreply@linkedin.com older_than:15d",
        "from:Retail@shinseibank.com older_than:15d",
        "from:contacts@email.woolworthsrewards.com.au older_than:15d",
        "from:eBay@e.reply.ebay.com.au older_than:15d",
        "from:noreply@youtube.com older_than:30d",
        "from:contacts@email.everydayrewards.com.au older_than:2d",
    ]

    for i in query_list:
        mails_deleted = search_and_delete(i, creds, maxResults)

        number_of_emails_deleted = number_of_emails_deleted + mails_deleted

        if mails_deleted > 0:
            email_report_list.append({"filter": i, "deleted": mails_deleted})

    print(f"Total Number of emails deleted : {number_of_emails_deleted}")

    email_report_string = ""

    for j in email_report_list:
        email_report_string = email_report_string + "\n" + str(j)

    print(email_report_string)

    email_string = f"Number of emails deleted : {number_of_emails_deleted}\n\n{email_report_string}"

    send_email(creds, email_string)
