from google.cloud import secretmanager
import os

PROJECT_ID = os.environ['PROJECT_ID']
# Secret manager
secret_client = secretmanager.SecretManagerServiceClient()

def get_secret(key):
    SLACK_SIGN_SECRET_ROURCE_ID = {"name": f"projects/{PROJECT_ID}/secrets/{key}/versions/latest"}
    return secret_client.access_secret_version(SLACK_SIGN_SECRET_ROURCE_ID).payload.data.decode("utf-8")