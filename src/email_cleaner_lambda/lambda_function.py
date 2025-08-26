import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def lambda_handler(event, context):
    result = "Hello World 123"
    return {
        'statusCode' : 200,
        'body': result
    }