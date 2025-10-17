
import time
from typing import Dict, Optional

import jwt
from decouple import config
from datetime import datetime, timedelta, timezone



JWT_SECRET = config("MUSEOFILE_SECRET")
JWT_ALGORITHM = config("MUSEOFILE_ALGORITHM")
JWT_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES" ))


def token_response(token: str):
    return {"access_token": token}

def sign_jwt(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)

def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}