import os

BOT_TOKEN = os.getenv('BOT_TOKEN', False)
bot_user_name = "uslugebot"
BOT_DEPLOYMENT_URL = "https://usluge-bot.herokuapp.com"

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', False)
SENTRY_DSN = os.getenv('SENTRY_DSN', False)

GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID = os.getenv('GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID', False)
GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY = os.getenv('GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY', False)
GOOGLE_SERVICE_ACCOUNT_CLIENT_ID = os.getenv('GOOGLE_SERVICE_ACCOUNT_CLIENT_ID', False)
GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL = os.getenv('GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL', False)

GOOGLE_SERVICE_ACCOUNT_CREDENTIALS = {
  "type": "service_account",
  "project_id": "atila-352102",
  "private_key_id": GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID,
  "private_key": f"-----BEGIN PRIVATE KEY-----{GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY}-----END PRIVATE KEY-----\n",
  "client_email": GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL,
  "client_id": GOOGLE_SERVICE_ACCOUNT_CLIENT_ID,
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/usluge-bot%40atila-352102.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', False)
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', False)
WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER', False)

MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', False)
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', False)
MONGODB_URL = os.getenv('MONGODB_URL', False)
