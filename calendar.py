'''
in this module we handle everything related to the Google Calendar API
'''
import webbrowser
from oauth2client import client
import httplib2
import apiclient

JSON_EVENT_NAME = 'summary'
CLIENT_ID_PATH = 'client_id.json'
GOOGLE_CALENDAR_API_SCOPE = 'https://www.googleapis.com/auth/calendar'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'  #  meaning it will open a webbrowser, the user will accept access and paste a code into the program

def add_to_calendar(json_lectures):
    # make requests to the API using the interface provided
    calendar_service = get_service_object()
    # loop through the lectures that are alreay made in JSON and simply push them to the calendar
    for lecture in json_lectures:
        calendar_service.events().insert(calendarId='primary', body=lecture).execute()
        print("Event created: {}".format(lecture[JSON_EVENT_NAME]))

    print('\nDone! Added {} lectures to your Google Calendar! :)'.format(len(json_lectures)))

def get_service_object():
    flow, auth_code = acquire_authorization()

    access_token = acquire_access_token(flow=flow, authorization_code=auth_code)

    service_object = build_service_object(access_token=access_token)

    return service_object

def acquire_authorization():
    flow = client.flow_from_clientsecrets(CLIENT_ID_PATH, scope=GOOGLE_CALENDAR_API_SCOPE, redirect_uri=REDIRECT_URI)
    auth_url = flow.step1_get_authorize_url()  # the url that will be opened to the user
    # open the site that prompts the user to allow access
    webbrowser.open_new(auth_url)

    print("After allowing the application in Google, you should be supplied with an authorization code.")
    print("Please paste it here: ")
    return flow, input()


def acquire_access_token(flow, authorization_code: str):
    # step two, acquite access token
    print("Acquiring access token...")
    # exchange the authorization token for an access token
    return flow.step2_exchange(authorization_code)

def build_service_object(access_token):
    # build a Http object to call Google APIs
    http_auth = access_token.authorize(httplib2.Http())

    # build service object
    return apiclient.discovery.build('calendar', 'v3', http=http_auth)

