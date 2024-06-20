import os.path
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
jam_cred='token.json'
virg_cred='virg_token.json'
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/','https://www.googleapis.com/auth/drive']
user_token=virg_cred
if os.path.exists(user_token):
    CREDS = Credentials.from_authorized_user_file(user_token, SCOPES)
GMAIL_SERVICE = build("gmail", "v1", credentials=CREDS)
GDRIVE_SERVICE=build("drive", "v3", credentials=CREDS)
MAXIMUM = 500
def main():
    """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(user_token):
        creds = Credentials.from_authorized_user_file(user_token, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(user_token, "w") as token:
            token.write(creds.to_json())
main()

def search_emails(query, labels=None):
    email_messages = []
    next_page_token = None
    message_response = GMAIL_SERVICE.users().messages().list(
        userId='me',
        labelIds=labels,
        includeSpamTrash=True,
        q=query,
        maxResults=MAXIMUM
    ).execute()
    email_messages = message_response.get('messages')
    next_page_token = message_response.get('nextPageToken')

    while next_page_token:
        message_response = GMAIL_SERVICE.users().messages().list(
            userId='me',
            labelIds=labels,
            q=query,
            maxResults=MAXIMUM,
            includeSpamTrash=True,
            pageToken=next_page_token
        ).execute()
        email_messages.extend(message_response['messages'])
        next_page_token = message_response.get('nextPageToken')
        print('Page Token: {0}'.format(next_page_token))
        time.sleep(0.5)
    return email_messages

def delete_emails(email_results):
    count = 0
    for email_result in email_results:
        count += 1
        print(count)
        GMAIL_SERVICE.users().messages().delete(
            userId='me',
            id=email_result['id']
        ).execute()
def find_and_delete(queries):
    for query in queries:
        email_results = search_emails(query)
        if email_results:
            print(len(email_results))
            delete_emails(email_results)
        else:
            print('all gone')
keywords=['gbs','plus']
queries = [f"older_than:2m AND {x} -from:kasson@gmail.com" for x in keywords]
find_and_delete(queries)

def list_gdrive_file_size():
    results = (
        GDRIVE_SERVICE.files()
        .list(pageSize=500, fields="nextPageToken, files(size, name,id)")
        .execute()
    )
    items = results.get("files", [])

    if not items:
        print("No files found.")
        return
    print("Files:")
    for item in items:
        if 'size' in item and int(item['size'])/1000000>1:
            print(f"{item['name']} {int(item['size'])/1000000}M")
