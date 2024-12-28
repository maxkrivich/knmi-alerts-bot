import requests

from datetime import datetime, timezone

URL = "https://api.dataplatform.knmi.nl/open-data/v1"
TOKEN = (
    "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6ImE1OGI5NGZmMDY5NDRhZDNhZjFkMDBmNDBmNTQyNjBkIiwiaCI6Im11cm11cjEyOCJ9"
)


def get_report():
    session = requests.Session()
    session.headers = {"Authorization": TOKEN}

    # Get the current date and time in UTC
    current_datetime = datetime.now(timezone.utc)

    # Replace the time with 00:00:00
    midnight_datetime = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

    # Format it as an ISO 8601 string
    formatted_datetime = midnight_datetime.isoformat()

    r = session.get(
        f"{URL}/datasets/waarschuwingen_nederland_48h/versions/1.0/files",
        params={"sorting": "desc", "orderBy": "lastModified", "begin": formatted_datetime},
    )

    return r.json()


def main():
    print(get_report())


if __name__ == "__main__":
    main()
