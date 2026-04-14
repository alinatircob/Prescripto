
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CalendarEventRequest(BaseModel):
    """Model pentru structura unui eveniment ce trebuie creat în Google Calendar."""
    summary: str = Field(..., description="Titlul evenimentului (ex: 💊 Tratament: Noliprel)")
    description: str = Field(default="", description="Instrucțiunile de administrare pentru pacient")
    start_time: datetime = Field(..., description="Momentul de start al alarmei")
    end_time: datetime = Field(..., description="Momentul de final al alarmei (de obicei start_time + 15 min)")
    recurrence_rule: str = Field(default="RRULE:FREQ=DAILY;COUNT=7", description="Regula de recurență (ex: zilnic timp de 7 zile)")

class CalendarSyncResult(BaseModel):
    """Model pentru rezultatul final returnat de serviciul de calendar către interfața Streamlit."""
    success: bool = Field(..., description="Indică dacă programarea a reușit cu succes")
    linkuri: List[str] = Field(default_factory=list, description="Lista URL-urilor către evenimentele din calendar")
    eroare: Optional[str] = Field(default=None, description="Mesajul de eroare detaliat în caz de eșec")