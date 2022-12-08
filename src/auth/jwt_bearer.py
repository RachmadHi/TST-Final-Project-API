from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt_handler import decodeJSONWebToken

class JSONWebTokenBearer(HTTPBearer):
    def __init__(self, auto_Error : bool = True):
        super(JSONWebTokenBearer, self).__init__(auto_error = auto_Error)

    async def __call__(self, request: Request):
        credentials : HTTPAuthorizationCredentials = await super(JSONWebTokenBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer" :
                raise HTTPException(status_code = 403, detail = "Invalid token or expired token")
            return credentials.credentials
        else :
             raise HTTPException(status_code = 403, detail = "Invalid token or expired token")
    
    def verify_JSONWebToken(self, jwtoken : str):
        isTokenValid : bool = False
        payload = decodeJSONWebToken(jwtoken)
        if payload:
            isTokenValid = True
        return isTokenValid