import pandas as pd
import PyPDF2
import logging
from typing import Optional, List, Dict, Any

from utils.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DataService:
    """
    Serviciu pentru gestionarea datelor locale (CSV, PDF).
    """

    @staticmethod
    def load_meds_database() -> Optional[pd.DataFrame]:
        """Încarcă CSV-ul cu medicamente folosind Pandas și căile absolute din setări."""
        try:
            if not settings.CSV_PATH.exists():
                logger.error(f"❌ Fișierul nu există la calea: {settings.CSV_PATH}")
                return None

            df = pd.read_csv(settings.CSV_PATH, on_bad_lines='skip', sep=None, engine='python')
            logger.info(f"✅ Baza de medicamente încărcată cu succes ({len(df)} înregistrări).")
            return df

        except Exception as e:
            logger.error(f"❌ Eroare la citirea medicamentelor: {e}")
            return None

    @staticmethod
    def find_alternatives_by_dci(dci_name: str, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Caută în DataFrame toate medicamentele care au același DCI."""
        if df is None or not dci_name:
            return []

        try:
            # Căutăm (case-insensitive) în coloana DCI
            rezultate = df[df['DCI'].str.contains(dci_name, case=False, na=False)]
            return rezultate.to_dict('records')

        except KeyError:
            logger.warning("⚠️ Nu am găsit coloana DCI în CSV. Verificați numele coloanelor!")
            return [{"eroare": "Coloana DCI lipsește din baza de date."}]
        except Exception as e:
            logger.error(f"❌ Eroare neprevăzută la căutarea alternativelor: {e}")
            return []

    @staticmethod
    def get_disease_from_pdf(disease_code: str) -> Optional[str]:
        """Caută un cod de boală și extrage exact rândul unde se află denumirea oficială."""
        if not settings.PDF_PATH.exists():
            logger.error(f"❌ Fișierul PDF nu există la calea: {settings.PDF_PATH}")
            return None

        try:
            with open(settings.PDF_PATH, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    text = reader.pages[page_num].extract_text()
                    if text:
                        randuri = text.split('\n')
                        for rand in randuri:
                            if str(disease_code).upper() in rand.upper():
                                return rand.strip()

            logger.info(f"ℹ️ Codul {disease_code} nu a fost găsit în PDF.")
            return None

        except Exception as e:
            logger.error(f"❌ Eroare la citirea PDF-ului: {e}")
            return None