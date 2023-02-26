from datetime import datetime, timedelta

CREATE_TIME = (datetime.now() + timedelta(minutes=10)).isoformat(timespec="minutes")
CLOSE_TIME = (datetime.now() + timedelta(hours=1)).isoformat(timespec="minutes")
