import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database settings
    DB_NAME = os.getenv('DB_NAME', 'nlp_messages')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    # NLP settings
    SPACY_MODEL = os.getenv('SPACY_MODEL', 'en_core_web_lg')
    
    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Scoring settings
    SCORING_THRESHOLD_LOW = float(os.getenv('SCORING_THRESHOLD_LOW', 5))
    SCORING_THRESHOLD_MEDIUM = float(os.getenv('SCORING_THRESHOLD_MEDIUM', 10))
    SCORING_THRESHOLD_HIGH = float(os.getenv('SCORING_THRESHOLD_HIGH', 20))

settings = Settings()