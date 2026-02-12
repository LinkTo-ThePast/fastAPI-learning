from datetime import datetime
from zoneinfo import ZoneInfo

APP_TIME = ZoneInfo("America/Mexico_City")
UTC_TIMEZONE = ZoneInfo("UTC")

def now_mexico() -> datetime:
  return datetime.now(APP_TIME)