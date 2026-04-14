import logging
import datetime
from typing import List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.config import settings
from models.prescription import ConfirmedMedication
from models.patient import Patient
from models.calendar_event import CalendarSyncResult

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CalendarService:
    """
    Serviciu responsabil cu integrarea Google Calendar.
    Gestionează autentificarea și crearea evenimentelor recurente.
    """
    SCOPES = ['https://www.googleapis.com/auth/calendar.events']
    TIMEZONE = 'Europe/Bucharest'

    def __init__(self):
        self.service = self._initialize_service()

    def _initialize_service(self):
        """Inițializează și returnează clientul Google Calendar."""
        if not settings.GOOGLE_CREDENTIALS_PATH.exists():
            logger.error(f"❌ Fișierul de credențiale lipsește: {settings.GOOGLE_CREDENTIALS_PATH}")
            return None

        try:
            creds = service_account.Credentials.from_service_account_file(
                str(settings.GOOGLE_CREDENTIALS_PATH),
                scopes=self.SCOPES
            )
            return build('calendar', 'v3', credentials=creds)
        except Exception as e:
            logger.error(f"❌ Eroare la autentificarea Google Calendar: {e}")
            return None

    def adauga_tratament_in_calendar(self, medicamente: List[ConfirmedMedication],
                                     pacient: Patient) -> CalendarSyncResult:
        """
        Primește o listă de obiecte ConfirmedMedication și creează evenimente în calendarul pacientului.
        """
        if not self.service:
            return CalendarSyncResult(
                success=False,
                eroare="Serviciul Google Calendar nu este disponibil. Verifică credențialele."
            )

        linkuri_evenimente = []
        # Setăm ca tratamentul să înceapă de mâine
        start_date = datetime.date.today() + datetime.timedelta(days=1)

        try:
            for med in medicamente:
                ore_administrare = med.ore if med.ore else ["09:00"]

                for ora in ore_administrare:
                    try:
                        h, m = map(int, ora.split(':'))
                    except ValueError:
                        logger.warning(f"⚠️ Format oră invalid '{ora}'. Fallback la 09:00.")
                        h, m = 9, 0

                    # Setăm ora specifică
                    start_time = datetime.time(h, m)
                    end_time = datetime.time(h, m + 15)  # Alocăm 15 minute

                    start_datetime = datetime.datetime.combine(start_date, start_time).isoformat()
                    end_datetime = datetime.datetime.combine(start_date, end_time).isoformat()

                    event_body = {
                        'summary': f'💊 Tratament: {med.nume} ({med.doza})',
                        'description': f'**Instrucțiuni medic/farmacist:**\n{med.instructiuni}',
                        'start': {
                            'dateTime': start_datetime,
                            'timeZone': self.TIMEZONE,
                        },
                        'end': {
                            'dateTime': end_datetime,
                            'timeZone': self.TIMEZONE,
                        },
                        'recurrence': [
                            'RRULE:FREQ=DAILY;COUNT=7'  # Default tratament de 7 zile
                        ],
                        'reminders': {
                            'useDefault': False,
                            'overrides': [
                                {'method': 'popup', 'minutes': 10},
                            ],
                        },
                    }

                    # Executăm request-ul către Google Calendar (folosim adresa de email din modelul Patient)
                    created_event = self.service.events().insert(
                        calendarId=pacient.email,
                        body=event_body
                    ).execute()

                    linkuri_evenimente.append(created_event.get('htmlLink'))

            logger.info(f"✅ S-au adăugat {len(linkuri_evenimente)} alarme pentru {pacient.email}.")
            return CalendarSyncResult(success=True, linkuri=linkuri_evenimente)

        except HttpError as http_err:
            logger.error(f"❌ Eroare API Google: {http_err}")
            return CalendarSyncResult(success=False,
                                      eroare=f"Eroare de comunicare cu Google Calendar: {http_err.reason}")
        except Exception as e:
            logger.error(f"❌ Eroare neașteptată la calendar: {e}")
            return CalendarSyncResult(success=False, eroare=str(e))


# Instanță de folosit în interfață
calendar_service = CalendarService()