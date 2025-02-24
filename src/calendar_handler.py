from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
import os.path
import pickle
from paths_config import BASE_DIR
import logging

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token.pickle')

class CalendarHandler:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        try:
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'rb') as token:
                    self.creds = pickle.load(token)

            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                    self.creds = flow.run_local_server(port=0)
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(self.creds, token)

            self.service = build('calendar', 'v3', credentials=self.creds)
        except Exception as e:
            logging.error(f"Error en la autenticación: {str(e)}")
            raise Exception("Error en la autenticación con Google Calendar. Verifica tus credenciales y permisos.")

    def get_todays_events(self):
        try:
            # Refresh credentials if expired
            if self.creds and self.creds.expired and self.creds.refresh_token:
                from google.auth.transport.requests import Request
                self.creds.refresh(Request())
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(self.creds, token)
                    
            # Usar hora local en lugar de UTC
            now = datetime.datetime.now()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + datetime.timedelta(days=1)
            
            # Convertir a formato ISO 8601 con zona horaria local
            time_zone = datetime.datetime.now().astimezone().tzinfo
            start_of_day = start_of_day.astimezone(time_zone)
            end_of_day = end_of_day.astimezone(time_zone)

            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_of_day.isoformat(),
                timeMax=end_of_day.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            formatted_events = []
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                if 'T' in start:  # Evento con hora específica
                    start_time = datetime.datetime.fromisoformat(start).strftime('%H:%M')
                    end_time = datetime.datetime.fromisoformat(end).strftime('%H:%M')
                    time_str = f"{start_time} - {end_time}"
                else:  # Evento de todo el día
                    time_str = 'Todo el día'
                
                formatted_events.append({
                    'time': time_str,
                    'summary': event['summary'],
                    'is_all_day': 'T' not in start
                })
            
            # Ordenar eventos: primero los de todo el día, luego por hora
            formatted_events.sort(key=lambda x: (not x['is_all_day'], x['time']))
            return formatted_events
            
        except Exception as e:
            logging.error(f"Error obteniendo eventos del calendario: {str(e)}")
            return []
