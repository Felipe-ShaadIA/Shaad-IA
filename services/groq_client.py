from groq import Groq
from config.settings import GROQ_API_KEY

_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=GROQ_API_KEY)
    return _client

def reset_client():
    global _client
    _client = None