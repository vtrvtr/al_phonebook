# This is an example file of how to extend the database schema using pydantic model. 
from pydantic import BaseModel, EmailStr, PositiveInt, constr
from datetime import date
from typing import Optional


class Item(BaseModel):
    name: constr(max_length=100, strip_whitespace=True)  # type: ignore
    address: Optional[constr(max_length=100, strip_whitespace=False)]  # type: ignore
    email: Optional[EmailStr]
    phone_number: Optional[constr(max_length=15, strip_whitespace=True, min_length=8)]  # type: ignore
    age: Optional[PositiveInt]
    birthday: date