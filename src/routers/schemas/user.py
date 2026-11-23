from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints 

#EmailStr validates thats whats being passed inside the email
#field actually follows the email structure and not just some 
#random text but it doesnt lowercase the email 


# we should lowercase emails because no major email provider  
#(like Gmail, Outlook, or Yahoo) treats Alex@gmail.com and  
#alex@gmail.com as separate accounts

NormalizedEmail = Annotated[EmailStr, StringConstraints(to_lower=True)]

  
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: NormalizedEmail


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    email: NormalizedEmail
    password: str = Field(max_length=128)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: NormalizedEmail | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer" 






            