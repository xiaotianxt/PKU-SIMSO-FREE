import json
from datetime import datetime, timedelta


def prettify(data):
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)


def format_date(delta=1):
    return (datetime.now() + timedelta(days=delta)).strftime('%Y%m%d')
