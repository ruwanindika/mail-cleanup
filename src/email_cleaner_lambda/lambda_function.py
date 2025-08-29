import json

import boto3
from botocore.exceptions import ClientError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def send_email(body_text):
    ses_client = boto3.client('ses')

    sender_email = "ruwanindika@gmail.com"
    recipient_email = "recipient@example.com"
    subject = "Email deletion report"

    try:
        response = ses_client.send_email(
            Source=sender_email,
            Destination={
                'ToAddresses': ["ruwanindika@gmail.com"]
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Text': {
                        'Data': body_text
                    }
                }
            }
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
        return {
            'statusCode': 200,
            'body': 'Email sent successfully!'
        }
    except Exception as e:
        print(f"Error sending email: {e}")
        return {
            'statusCode': 500,
            'body': f'Error sending email: {e}'
        }


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

                print(f"{email_from} --> {email_subject}")
                print()

                del_results = (
                    service.users()
                    .messages()
                    .trash(userId="me", id=msg["id"])
                    .execute()
                )

                if del_results:
                    number_of_emails_deleted = number_of_emails_deleted + 1


                print(del_results)
                print()

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
        "from:Rewards@email.dansnews.com.au",
        "from:noreply@redditmail.com",
        "from:ouchi-sagashi@openhouse-group.com",
        "from:mailrobot@internations.org",
        "from:mail@sg.rentalcars.com",
        "from:info@dailystoic.com",
        "from:subscriptions@message.bloomberg.com",
        "from:boconlinebanking@boc.lk",
        "from:developer@insideapple.apple.com",
        "from:hi@io.hatch.team",
        "from:HNBAlerts@hnb.lk",
        "from:no-reply@mail.instagram.com",
        "from:no-reply@mail.goodreads.com",
        "from:groups-noreply@linkedin.com",
        "from:flysmilesupdates@srilankan.com",
        "from:noreply@glassdoor.com",
        "from:noreply@ondemandmsg.sbs.com.au",
        "from:HGOneRewards@mc.ihg.com",
        "from:jobalerts-noreply@linkedin.com",
        "from:eBay@e.reply.ebay.com.au",
        "from:velocity@email.velocityfrequentflyer.com",
        "from:no-reply@news.spotifymail.com",
        "from:arnesandNobleEmail@email.bn.com",
        "from:newsletters@cnet.online.com",
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
        "from:naturescapes@engage.nationalparks.nsw.gov.au",
        "from:notification@facebookmail.com",
    ]

    for i in query_list:
        mails_deleted = search_and_delete(i, creds, maxResults)

        number_of_emails_deleted = number_of_emails_deleted + mails_deleted
        
        if mails_deleted>0:
            email_report_list.append({"filter":i,"deleted":mails_deleted})


    print(f"Number of emails deleted : {number_of_emails_deleted}")


    email_string = f"Number of emails deleted : {number_of_emails_deleted}\n\n{str(email_report_list)}"
    
    send_email(email_string)