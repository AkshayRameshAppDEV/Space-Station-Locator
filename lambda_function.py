from __future__ import print_function
from botocore.vendored import requests
import json


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome to Space Station Locator !"
    speech_output = "Welcome to Space Station Locator! The International space station travels about 30000 kilometers per hour, which is really fast. If you are lucky, you will get the country's name where the space station currently is or I will tell you the latitute and longitude coordinates." \
                    " If you would like to know the location of the space station, please ask " \
                    "where is the space station"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please ask the current location of space station by asking, " \
                    "where is the space station or you can quit the app by saying stop."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Thank You!"
    speech_output = "Thank you for trying the Space Station Locator. " \
                    "Have a nice day and come back soon!"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))





def spaceStationLocatorIntent(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """
    r = requests.get("http://api.open-notify.org/iss-now.json")
    c = r.content
    card_title = "Current Location of International Space Station"
    j = json.loads(c)
    latitude = float(j['iss_position']['latitude'])
    longitude = float(j['iss_position']['longitude'])
    try:
        k = requests.get("https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat="+str(latitude)+"&lon="+str(longitude)+"")
        hot = k.content
        jack = json.loads(hot)
        dfa = jack['address']['country']
        speech_output = "You are lucky! It is in "+dfa+". If you want to know again, please ask where is the space station"
        session_attributes = {}
        reprompt_text = "Please ask the current location of space station by asking, " \
                    "where is the space station or you can quit the app by saying stop"
        should_end_session = False
        return build_response({}, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
    except KeyError:
        reprompt_text = "Please ask the current location of space station by asking, " \
                    "where is the space station or you can quit the app by saying stop"
        speech_output = "The latitude is "+str(latitude) + " and " + "the longitude is "+str(longitude) + ". If you want to know again, please ask where is the space station"
        should_end_session = False
        return build_response({}, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
        
    
   


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "spaceStationLocatorIntent":
        return spaceStationLocatorIntent(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        return get_welcome_response()


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
