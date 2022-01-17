from pydantic import BaseModel, EmailStr, constr, PositiveInt 
from typing import Optional

class Item(BaseModel):
    name: constr(max_length=100, strip_whitespace=True)  # type: ignore
    email: Optional[EmailStr]
    phone_number: Optional[constr(max_length=15, strip_whitespace=True, min_length=8)]  # type: ignore
    age: Optional[PositiveInt]
    secondary_email: EmailStr = "foo@bar.com"