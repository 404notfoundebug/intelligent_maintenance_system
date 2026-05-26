from pydantic import BaseModel

from app.schemas.user import CurrentUserResponse


class LoginRequest(BaseModel):
    username: str
    password: str


class OAuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponseData(BaseModel):
    access_token: str
    token_type: str
    user: CurrentUserResponse


class LoginResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: LoginResponseData


class CurrentUserApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: CurrentUserResponse
