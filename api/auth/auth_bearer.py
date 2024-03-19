import os
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt


class RequiredLogin(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(RequiredLogin, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        headers: HTTPAuthorizationCredentials = await super(RequiredLogin, self).__call__(request)
        if headers:
            if not headers.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme.")
            token = headers.credentials

            payload = self.verify_jwt(token)

            if payload is None:
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token.")

            return payload.get("sub")
        else:
            raise HTTPException(
                status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwt_token: str):
        try:
            payload = jwt.decode(token=jwt_token, key=os.getenv("SECRET_KEY"),
                                 algorithms=[os.getenv("ALGORITHM")])
        except Exception as e:
            print(e)
            payload = None

        return payload
