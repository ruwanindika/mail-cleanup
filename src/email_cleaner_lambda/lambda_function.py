import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import boto3
from botocore.exceptions import ClientError

def get_secret():

    secret_name = "gmail-api-credentials"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']

    return json.loads(secret)


def main(seach_q, creds, maxResults):

    try:
        # Call the Gmail API

        service = build("gmail", "v1", credentials=creds)
        results = (
            service.users()
            .messages()
            .list(userId="me", maxResults=maxResults, q=seach_q)
            .execute()
        )
        # results2 = service.users().getProfile(userId="me").execute()
        # result_messages = service.users().messages().list(userId="me",maxResults=10).execute()
        # result_filter = service.users().settings().filters().list(userId="me").execute()

        labels = results.get("labels", [])

        print()
        if "messages" in results.keys():
            for msg in results["messages"]:
                #   print(msg)
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

                del_results = (
                    service.users()
                    .messages()
                    .trash(userId="me", id=msg["id"])
                    .execute()
                )
                # print(del_results)
                print()

            if not labels:
                print("No labels found.")
                return
            print("Labels:")
            for label in labels:
                print(label["name"])
        else:
            print(f"No messages for : {seach_q}")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


def oauth(SCOPES):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            secret_string = get_secret()
            flow = InstalledAppFlow.from_client_config(secret_string, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def lambda_handler(event, context):

    SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

    creds = oauth(SCOPES)

    maxResults = 5000

    query_list = [
        "from:Rewards@email.dansnews.com.au",
        "from:noreply@redditmail.com",
        "from:ouchi-sagashi@openhouse-group.com",
        "from:mailrobot@internations.org",
        "from:mail@sg.rentalcars.com",
        "from:info@dailystoic.com",
        "from:subscriptions@message.bloomberg.com",
        "from:scott.r.baxter@raywhite.com",
        "from:webmaster@tutorialspoint.com",
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
        "from:Coursera@m.learn.coursera.org",
        "from:jobalerts-noreply@linkedin.com",
        "from:eBay@e.reply.ebay.com.au",
        "from:email@e.livingsocial.com.au",
        "from:msgalert@whereareyounow.com",
        "from:benjamin@authenticeducation.com.au",
        "from:velocity@email.velocityfrequentflyer.com",
        "from:no-reply@news.spotifymail.com",
        "from:notification+mihpmuki@facebookmail.com",
        "from:tagged@taggedmail.com",
        "from:arnesandNobleEmail@email.bn.com",
        "from:mail@messaging.zoosk.com",
        "from:info@twitter.com",
        "from:noreply@r.grouponmail.com.au",
        "from:email@e.ourdeal.com.au",
        "from:news@n.anything.lk",
        "from:newsletters@cnet.online.com",
        "from:mapmyfitness@mapmyfitness.underarmour.com",
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
    ]

    for i in query_list:
        main(i, creds, maxResults)
