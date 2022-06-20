from . import config
import os
from google.cloud import language_v1 as language


def setup():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(config.get_credentials()['google_nlp'])
    global CLIENT
    CLIENT = language.LanguageServiceClient()


def create_document(text):
    doc = language.types.Document(
        content=text,
        language='pt',
        type='PLAIN_TEXT',
    )
    return doc

def analyze_sentiment(text):
    sentiment = CLIENT.analyze_sentiment(
        request={"document": create_document(text)}
    ).document_sentiment
    return sentiment

def analyze_synatx(text):
    syntax = CLIENT.analyze_syntax(
        request={"document": create_document(text)}
    ).tokens
    return syntax

def analyze_entities(text):
    entities = CLIENT.analyze_entities(
        request={"document": create_document(text)}
    ).entities
    return entities
