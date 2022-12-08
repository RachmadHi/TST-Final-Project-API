import time
import jwt
from decouple import config
from typing import Dict

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")

def respons_token(token : str):
    return {
        "access_token" : token
    }

def signJSONWebToken(user_id : str) -> Dict[str, str]:
    payload = {
        "user_id" : user_id,
        "expire_date" : time.time() + 1200
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm = JWT_ALGORITHM)
    return respons_token(token)

def decodeJSONWebToken(token : str) -> dict:
    try :
        decode_token = jwt.decode(token, JWT_SECRET, algorithm = JWT_ALGORITHM)
        return decode_token if decode_token["expire_date"] >= time.time() else None
    except :
        return {}
