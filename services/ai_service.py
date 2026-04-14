import os
import json
import logging
from PIL import Image
import google.generativeai as genai
from google.cloud import vision
from pydantic import ValidationError

from utils.config import settings
from models.prescription import PrescriptionData
from services.data_service import DataService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AIService:
    """
    Serviciu pentru interacțiunea cu modelele de inteligență artificială (Gemini și Vision API).
    Un pattern de inițializare "Lazy" pentru nomenclatoare ca să economisească memorie.
    """

    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(settings.GOOGLE_CREDENTIALS_PATH)
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-flash-latest')  # Am actualizat la versiunea stabilă

        # Variabile pentru a stoca nomenclatoarele în memorie doar o singură dată
        self._nomenclator_meds: str = ""
        self._nomenclator_boli: str = ""

    def _get_nomenclator_meds(self) -> str:
        """Încarcă și formatează string-ul cu medicamente pentru RAG (Doar când e nevoie)."""
        if not self._nomenclator_meds:
            df_meds = DataService.load_meds_database()
            if df_meds is not None:
                # Găsim automat coloana de gramaj (dacă există)
                gramaj_col = next((col for col in ['Concentratia', 'Concentratie', 'Gramaj'] if col in df_meds.columns),
                                  None)

                if gramaj_col:
                    variante = (df_meds['Denumire comerciala'].astype(str) + " - " + df_meds[gramaj_col].astype(
                        str)).unique()
                else:
                    variante = df_meds['Denumire comerciala'].dropna().astype(str).unique()
                self._nomenclator_meds = ", ".join(variante)
                logger.info(f"✅ Nomenclator Medicamente AI încărcat ({len(variante)} variante).")
            else:
                logger.warning("⚠️ Nomenclatorul de medicamente nu a putut fi încărcat pentru AI.")
        return self._nomenclator_meds

    def _get_nomenclator_boli(self) -> str:
        """Încarcă primele caractere din PDF-ul cu boli pentru RAG."""
        if not self._nomenclator_boli and settings.PDF_PATH.exists():
            import PyPDF2
            try:
                with open(settings.PDF_PATH, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        extras = page.extract_text()
                        if extras:
                            self._nomenclator_boli += extras + "\n"
                logger.info("✅ Nomenclator Boli (PDF) încărcat în memoria AI.")
            except Exception as e:
                logger.error(f"⚠️ Eroare la citirea PDF-ului pentru AI: {e}")
        return self._nomenclator_boli

    def _extract_text_from_image(self, image_file) -> tuple[str | None, str | None]:
        """Pasul 1: OCR cu Google Cloud Vision."""
        try:
            client = vision.ImageAnnotatorClient()
            image_file.seek(0)
            content = image_file.read()
            vision_image = vision.Image(content=content)

            response = client.document_text_detection(image=vision_image)

            if response.error.message:
                return None, f"Eroare internă Google Vision: {response.error.message}"
            if not response.full_text_annotation:
                return None, "Google Vision nu a detectat text pe imagine."

            return response.full_text_annotation.text, None
        except Exception as e:
            return None, f"Eroare de conexiune la Google Cloud: {str(e)}"

    def analyze_prescription(self, image_file) -> PrescriptionData:
        """
        Pasul 2: Arhitectură hibrida.
        Returnează un model Pydantic validat (PrescriptionData)
        """
        raw_text, ocr_error = self._extract_text_from_image(image_file)
        if not raw_text:
            return PrescriptionData(eroare=f"Eșec la citirea imaginii: {ocr_error}")

        logger.info("Text extras cu Vision API cu succes. Începe analiza Gemini...")

        try:
            image_file.seek(0)
            img_for_gemini = Image.open(image_file)
        except Exception as e:
            return PrescriptionData(eroare=f"Nu am putut deschide imaginea pentru AI: {e}")

        prompt = f"""
    Ești un medic și farmacist expert. Scopul tău este să atingi acuratețe 99.9% aplicând o Validare Încrucișată (Cross-Validation).
    Ai la dispoziție IMAGINEA rețetei, TEXTUL OCR, NOMENCLATORUL DE BOLI și LISTA DE MEDICAMENTE.

        TEXT OCR BRUT:
        '''{raw_text}'''

        NOMENCLATOR BOLI (CODURI ȘI AFECȚIUNI):
        '''{self._get_nomenclator_boli()[:15000]}'''

        LISTA OFICIALĂ DE MEDICAMENTE (NUME - GRAMAJ):
        '''{self._get_nomenclator_meds()}'''

    REGULI STRICTE:
    1. CODUL DE BOALĂ:
       - Este MEREU un număr (sau mai multe) cuprins între 1 și 999.
       - Caută în IMAGINE secțiunile "Cod boală", "Diagnostic", "Dg." și extrage NUMAI numerele scrise în dreptul lor.
       - Dacă sunt mai multe coduri, separă-le prin virgulă (ex: "678, 453").
       - IGNORĂ TOTAL vârsta pacientului, numărul de înregistrare (ex: 707) sau datele calendaristice.

    2. MEDICAMENTELE (ATENȚIE MAXIMĂ!):
       - Textul OCR este plin de greșeli (ex: 'Notignal' în loc de 'Noliprel', 'Mitrowint' etc).
       - Privește IMAGINEA, citește cuvântul și CAUTĂ CEL MAI APROPIAT TERMEN în LISTA OFICIALĂ DE MEDICAMENTE de mai sus.
       - "nume_brand_citit" TREBUIE să fie EXACT un nume găsit în acea LISTĂ (fără dozaj atașat în el).
       - "doza" TREBUIE extrasă separat (ex: "5 mg", "1.5 mg").

    3. APLICĂ ACEST LANȚ DE DEDUCȚIE (Chain of Thought):
        1. (au fost deja extrase la pasul 1 din "REGULI STRICTE") DIAGNOSTIC: Caută pe foaie secțiunile "Cod boală" sau "Diagnostic" și extrage DOAR numerele (ex: 678, 453).
        2. CORELATIE MEDICALĂ: Gândește-te ce afecțiuni reprezintă acele coduri (verifică în Nomenclatorul de Boli sau folosește expertiza ta).
        3. CITIREA MEDICAMENTELOR: Privește mâzgăliturile de pe foaie și textul OCR.
        4. VALIDARE SUPREMĂ: Acel medicament mâzgălit trebuie să (A) existe în LISTA OFICIALĂ DE MEDICAMENTE și (B) să trateze logic afecțiunile identificate la pasul 2! 
       De exemplu: Dacă diagnosticul e 453/310 (Boli cardiovasculare) și OCR-ul zice "Notignal 5/1.25", tu deduci clar din LISTA OFICIALĂ că e vorba de "Noliprel - 5/1.25 mg".	

    Răspunde STRICT cu un obiect JSON valid, folosind exact această structură:
    {{
      "cod_diagnostic": "Numerele între 1-999 găsite lângă 'Cod boala'/'Diagnostic' (ex: 789, 453). Null dacă nu găsești.",
      "medicamente": [
        {{
          "nume_brand_citit": "Numele exact ales din Lista Oficială",
          "doza": "ex: 5 mg",
          "frecventa_pe_zi": "ex: 2",
          "instructiuni_pacient": "Traduce notațiile medicului într-un limbaj detaliat și clar. De exemplu, dacă medicul a scris '1-0-1', tu scrie: 'Luați un comprimat dimineața și unul seara'. Include durata tratamentului DACA este specificată (ex: 'timp de 10 zile').",
          "ore_sugerate": ["08:00", "20:00"]
        }}
      ]
    }}
    """

        try:
            response = self.model.generate_content([prompt, img_for_gemini])
            text_response = response.text.strip()

            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]

            # Pydantic face maparea și validarea automată a JSON-ului
            date_structurate = PrescriptionData.model_validate_json(text_response.strip())
            return date_structurate

        except ValidationError as ve:
            logger.error(f"Eroare de validare a structurii JSON: {ve}")
            return PrescriptionData(eroare="AI-ul a înțeles rețeta, dar a formatat greșit răspunsul JSON.")
        except json.JSONDecodeError:
            return PrescriptionData(eroare="Răspunsul AI nu este un JSON valid.")
        except Exception as e:
            return PrescriptionData(eroare=f"Eroare la Gemini: {str(e)}")

    def explain_diagnosis(self, medical_text: str) -> str:
        if not medical_text:
            return "Nu am putut extrage textul diagnosticului."
        prompt = f"""Ești un medic. Explică în 1-2 propoziții, in limbaj natural, pe intelesul unei persoane necalificate in domeniul medical, acest diagnostic extras din nomenclator: "{medical_text}"."""
        try:
            return self.model.generate_content(prompt).text.strip()
        except Exception as e:
            logger.error(f"Eroare Gemini la diagnostic: {e}")
            return "Eroare la generarea explicației."

    def get_medication_prospectus(self, med_name: str) -> str:
        """Generează un prospect pe scurt, în limbaj natural, pentru un medicament."""
        if not med_name:
            return "Nu ai selectat un medicament valid."

        prompt = f"""
    Ești un farmacist empatic și răbdător. Pacientul tău a primit o rețetă pentru medicamentul: "{med_name}".
    Te rog să îi explici pe scurt, într-un limbaj simplu (fără termeni medicali complicați), ce este acest medicament, dar bazata pe prescriptia reala, corecta si complexa a medicamentului.

    Structurează răspunsul tău fix așa, folosind bullet points:
    🎯 **Pentru ce se folosește:** (1 propoziție)
    ⚠️ **Efecte adverse comune:** (2-3 exemple cele mai întâlnite)
    🚫 **Contraindicații majore:** (când NU trebuie luat, ex: sarcină, alergii specifice)
    💡 **Sfatul farmacistului:** (o recomandare prietenoasă de administrare)

    Fii scurt, direct la obiect și prietenos!
    """
        try:
            return self.model.generate_content(prompt).text.strip()
        except Exception as e:
            logger.error(f"Eroare Gemini la prospect: {e}")
            return "Eroare la generarea prospectului."


# Creăm o singură instanță globală (Singleton-like) pe care să o poată importa interfața Streamlit
ai_service = AIService()