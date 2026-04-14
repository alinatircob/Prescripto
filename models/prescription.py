
from pydantic import BaseModel, Field
from typing import List, Optional

class PrescribedMedication(BaseModel):
    """Model pentru medicamentul extras brut de AI din imagine."""
    nume_brand_citit: str = Field(..., description="Numele exact ales din Lista Oficială")
    doza: Optional[str] = Field(default="", description="Dozajul prescris")
    frecventa_pe_zi: Optional[str] = Field(default="", description="Frecvența administrării")
    instructiuni_pacient: Optional[str] = Field(default="", description="Instrucțiuni traduse din notațiile medicului")
    ore_sugerate: List[str] = Field(default_factory=list, description="Orele sugerate pentru administrare")

class PrescriptionData(BaseModel):
    """Model pentru întregul rezultat returnat de Gemini."""
    cod_diagnostic: Optional[str] = Field(default=None, description="Codul de boală (ex: 453)")
    medicamente: List[PrescribedMedication] = Field(default_factory=list)
    eroare: Optional[str] = Field(default=None, description="Mesaj de eroare în caz de eșec OCR sau AI")

class ConfirmedMedication(BaseModel):
    """Model pentru medicamentul validat și confirmat de utilizator pentru Calendar."""
    nume: str
    doza: str
    instructiuni: str
    ore: List[str] = Field(default_factory=list)