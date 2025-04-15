import os.path
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# go to google cloud console and download client secret rename it credentials.json then run
# delete this if you lose authentication
jam_cred = 'token.json'
virg_cred = 'virg_token.json'
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/drive',
          "https://www.googleapis.com/auth/youtube.force-ssl"]
user_token = jam_cred
if os.path.exists(user_token):
    CREDS = Credentials.from_authorized_user_file(user_token, SCOPES)

MAXIMUM = 500


def authenticate():
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
        print(1)
        with open(user_token, "w") as token:
            token.write(creds.to_json())


def search_emails(query, gmail_service, labels=None):
    email_messages = []
    next_page_token = None
    message_response = gmail_service.users().messages().list(
        userId='me',
        labelIds=labels,
        includeSpamTrash=True,
        q=query,
        maxResults=MAXIMUM
    ).execute()
    email_messages = message_response.get('messages')
    next_page_token = message_response.get('nextPageToken')

    while next_page_token:
        message_response = gmail_service.users().messages().list(
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


def delete_emails(email_results, gmail_service):
    count = 0
    for email_result in email_results:
        count += 1
        print(count)
        gmail_service.users().messages().delete(
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


def list_gdrive_file_size(gdrive_service):
    results = (
        gdrive_service.files()
        .list(pageSize=500, fields="nextPageToken, files(size, name,id)")
        .execute()
    )
    items = results.get("files", [])

    if not items:
        print("No files found.")
        return
    print("Files:")
    for item in items:
        if 'size' in item and int(item['size']) / 1000000 > 1:
            print(f"{item['name']} {int(item['size']) / 1000000}M")

def delete_video_from_playlist(youtube, playlist_item_id):
    try:
        youtube.playlistItems().delete(id=playlist_item_id).execute()
        print(f"Deleted playlist item: {playlist_item_id}")
    except Exception as e:
        print(e)
def empty_playlist(youtube, playlist_title):
    request = youtube.playlistItems().list(
        part="id,snippet",
        maxResults=50,
        playlistId=get_playlist_id(youtube,playlist_title)
    )
    response = request.execute()

    for item in response["items"]:
        delete_video_from_playlist(youtube, item['id'])

    # print("Video not found in playlist")
def list_playlist_vids(youtube, playlist_id):
    request = youtube.playlistItems().list(
        part="id,snippet",
        maxResults=50,
        playlistId=playlist_id
    )
    response = request.execute()
    # return response['items']
    return tuple(f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}" for item in response['items'])
def get_playlist_id(youtube,playlist_title):
    request = youtube.playlists().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=25
    )
    response = request.execute()
    for item in response["items"]:
        if item['snippet']['title']==playlist_title:
            return item['id']

def get_playlist_url(youtube,playlist_title):
    request = youtube.playlists().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=25
    )
    response = request.execute()
    for item in response["items"]:
        if item['snippet']['title'] == playlist_title:
            return f"https://youtube.com/playlist?list={item['id']}"

def main():
    authenticate()
    GMAIL_SERVICE = build("gmail", "v1", credentials=CREDS)
    GDRIVE_SERVICE = build("drive", "v3", credentials=CREDS)
    YOUTUBE = build("youtube", "v3", credentials=CREDS)

    return GMAIL_SERVICE,GDRIVE_SERVICE,YOUTUBE
    # keywords = ['gbs', 'plus']
    # queries = [f"older_than:2m AND {x} -from:kasson@gmail.com" for x in keywords]
    # find_and_delete(queries)


if __name__ == '__main__':
    main()
