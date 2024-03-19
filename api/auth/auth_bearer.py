import os
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt


class RequiredLogin(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(RequiredLogin, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        jwt_from_header: HTTPAuthorizationCredentials = await super(RequiredLogin, self).__call__(request)

        if jwt_from_header:
            if not jwt_from_header.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme.")
            payload = self.verify_jwt(jwt_from_header.credentials)
            if payload is None:
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token.")

            return payload.get("sub")
        else:
            raise HTTPException(
                status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str):
        try:
            payload = jwt.decode(jwtoken, os.getenv("SECRET_KEY"),
                                 algorithms=[os.getenv("ALGORITHM")])
        except:
            payload = None
        # print(payload)
        return payload
