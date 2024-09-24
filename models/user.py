from typing import Union
from pydantic import BaseModel, Field, ValidationError, validator
from enum import Enum
from utils.response_manipulator import CustomResponse

class AccountType(str, Enum):
    MAGIC_LINK = "magic_link"
    GOOGLE = "google"
    SSO = "sso"

class BaseUserModel(BaseModel):
    account_type: AccountType

class SSOUserModel(BaseUserModel):
    email: str = Field(..., min_length=2)
    password: str = Field(..., min_length=2)

class SocialUserModel(BaseUserModel):  # Only for Google
    account_id: str = Field(..., min_length=2)
    name: str = Field(..., min_length=2)
    email: str = Field(..., min_length=2)
    profile_image: str = Field(..., min_length=2)

    @validator('account_type')
    def validate_account_type(cls, value):
        if value != AccountType.GOOGLE:
            raise ValueError("Unsupported account type")
        return value

class MagicLinkModel(BaseUserModel):
    email: str = Field(..., min_length=2)
    
class UserModel(BaseModel):
    user: Union[MagicLinkModel, SocialUserModel, SSOUserModel]

    @validator('user', pre=True)
    def validate_user(cls, value):
        account_type = value.get("account_type")
        if account_type == AccountType.SSO:
            return SSOUserModel(**value)
        elif account_type == AccountType.GOOGLE:
            return SocialUserModel(**value)
        elif account_type == AccountType.MAGIC_LINK:
            return MagicLinkModel(**value)
        else:
            raise ValueError(f"Unsupported account type {account_type}")

class WaitListModel(BaseModel):
    email: str = Field(..., min_length=2)
    name: str = Field(..., min_length=2)
