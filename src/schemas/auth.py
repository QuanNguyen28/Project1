from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from typing import Optional, List


class Token(BaseModel):

    access_token: str

    token_type: str


class TokenData(BaseModel):

    username: Optional[str] = None


class User(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    user_id: int

    username: str

    full_name: Optional[str]

    email: EmailStr

    roles: List[str]

    is_active: bool

    @field_validator("roles", mode="before")
    @classmethod
    def extract_role_names(cls, v):
        """
        Convert ORM role objects (with attribute .role_name) into a list of strings.
        """

        return [role.role_name for role in v]


class UserCreate(BaseModel):

    username: str

    password: str

    full_name: Optional[str]

    email: EmailStr
