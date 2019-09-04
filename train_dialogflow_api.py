import os
import logging
import json
import dialogflow_v2 as dialogflow
from google.protobuf.json_format import MessageToDict

logging.basicConfig(format=u'%(process)d %(LevelName)s %(message)s')
logger = logging.getLogger('TrainLogger')
logger.setLevel(logging.INFO)

project_id = os.getenv("DIALOGFLOW_PROJECT_ID")
session_id = os.getenv("USER_CHAT_ID")

def create_intent(name, training_phrases, messages, parameters=None, project_id=project_id):
    intents_client = dialogflow.IntentsClient()
    parent = intents_client.project_agent_path(project_id)
    intent = {
        'display_name': name,
        'training_phrases': training_phrases,
        'parameters': parameters,
        'messages': messages,
    }
    intent = intents_client.create_intent(parent, intent, intent_view=dialogflow.enums.IntentView.INTENT_VIEW_FULL)
    print('1')

    return MessageToDict(intent, preserving_proto_field_name=True)


def get_intent(name, project_id=project_id):
    client = dialogflow.IntentsClient()
    parent = client.project_agent_path(project_id)
    intents = client.list_intents(parent, intent_view=dialogflow.enums.IntentView.INTENT_VIEW_FULL)
    try:
        intent = [intent for intent in intents if intent.display_name == name][0]
    except IndexError:
        return None
    return MessageToDict(intent, preserving_proto_field_name=True)


def get_dialog_response(session_id, text, language_code='ru', project_id=project_id):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    dialogflow_response = session_client.detect_intent(session=session, query_input=query_input)
    response = {
        'query_text': dialogflow_response.query_result.query_text,
        'intent': dialogflow_response.query_result.intent.display_name,
        'confidence': dialogflow_response.query_result.intent_detection_confidence,
        'response_text': dialogflow_response.query_result.fulfillment_text,
    }
    return response


def delete_intent(name, project_id=project_id):
    intent = get_intent(name, project_id)
    intent_id = intent['name'].split('/')[-1]
    intents_client = dialogflow.IntentsClient()
    intent_path = intents_client.intent_path(project_id, intent_id)
    intents_client.delete_intent(intent_path)


def train_bot(training_set_file, is_rewrite_answers=False):
    print('START')
    logger.info('Training bot process has been started')

    with open(training_set_file, 'r') as training_set_file:
        training_set = json.load(training_set_file)

    for intent_name, intent_training_set in training_set.items():
        training_phrases = []
        messages = []
        parameters = []
        logger.info(f'Starting training for set {intent_name}')
        intent = get_intent(intent_name)
        if intent:
            training_phrases.extend(intent.get('training_phrases', []))
            messages = intent.get('messages', [])
            parameters = intent.get('parameters', [])
            delete_intent(intent_name)

        training_set_questions = [{'type': 'EXAMPLE', 'parts': [{'text': question}]} for question in intent_training_set['questions']]
        training_phrases.extend(training_set_questions)

        training_set_answer = intent_training_set['answer']
        if not messages or is_rewrite_answers:
            messages = [{'text': {'text': [training_set_answer]}}]

        create_intent(intent_name, training_phrases, messages, parameters)
        logger.info(f'Bot has been trained on set {intent_name}')

    logger.info('Training bot process has been finished')
