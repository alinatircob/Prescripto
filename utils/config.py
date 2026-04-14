# Fișier: src/utils/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Determinăm calea absolută către rădăcina proiectului
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


class Settings:
    """Clasă centralizată pentru configurările aplicației."""
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Căi dinamice către fișiere
    GOOGLE_CREDENTIALS_PATH: Path = BASE_DIR / "credentials.json"
    CSV_PATH: Path = BASE_DIR / "data" / "medicamente.csv"
    PDF_PATH: Path = BASE_DIR / "data" / "coduri_boala.pdf"

    @classmethod
    def validate(cls):
        """Validează dacă avem tot ce ne trebuie pentru a rula aplicația."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("❌ Eroare: Nu am găsit GEMINI_API_KEY în fișierul .env.")

        if not cls.GOOGLE_CREDENTIALS_PATH.exists():
            print("⚠️ Avertisment: credentials.json lipsește. Integrarea Google Calendar va eșua.")


# Instanțiem și validăm setările la import
settings = Settings()
settings.validate()