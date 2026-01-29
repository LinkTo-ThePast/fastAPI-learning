from pydantic import BaseModel
from fastapi import APIRouter
from typing import Optional, Dict, Any



class EmailValidationSchema(BaseModel):
	email: str

class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

router = APIRouter()

@router.post("/validate-email", response_model=ResponseModel)
async def validate_email(
	request: EmailValidationSchema
):
    try:
        user = "user 1";
        if not user:
            raise Exception("we couldn't find an user!")
        print("generate OTP")
        OTP = "otp secret"
        print(f"sending email to {request.email} with OTP: {OTP}")
    except Exception as e:
        print(f"Something happen! {e}")