
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Patient(BaseModel):
    """Model care stochează datele pacientului."""

    email: EmailStr = Field(..., description="Adresa de email validă pentru integrarea Google Calendar")

    nume: Optional[str] = Field(default=None, description="Numele pacientului (opțional)")