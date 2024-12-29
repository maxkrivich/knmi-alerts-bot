import requests
import os
import io
import pathlib

from datetime import datetime, timezone

from icecream import ic

URL = "https://api.dataplatform.knmi.nl/open-data/v1"
TOKEN = os.environ.get("KNMI_OPEN_DATA_API_TOKEN")


def download_report(url: str):
    resp = requests.get(url, stream=True)
    resp.raise_for_status()

    return io.BytesIO(resp.content)


def write_report(report: io.BytesIO, filename: str, path: pathlib.Path) -> str:
    full_path = path / filename
    with open(full_path, "wb") as fd:
        fd.write(report.read())
        return filename
    return None



def get_temporary_download_url(url: str) -> str:
    resp = requests.get(url, headers={"Authorization": TOKEN})
    resp.raise_for_status()

    return resp.json().get("temporaryDownloadUrl")


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
    # print(get_report())
    message = {"specversion": "1.0", "type": "nl.knmi.dataplatform.file.created.v1", "source": "https://dataplatform.knmi.nl", "id": "aedb91ce-43d2-5b2f-c7e0-df49cc44d6c5", "time": "2024-12-29T09:10:40Z", "datacontenttype": "application/json", "data": {"datasetName": "waarschuwingen_nederland_48h", "datasetVersion": "1.0", "filename": "knmi_waarschuwingen_202412290909.xml", "url": "https://api.dataplatform.knmi.nl/open-data/v1/datasets/waarschuwingen_nederland_48h/versions/1.0/files/knmi_waarschuwingen_202412290909.xml/url"}}

    ic(message)

    download_url = get_temporary_download_url(message["data"]["url"])
    ic(download_url)

    report = download_report(download_url)
    write_report(report, message["data"]["filename"], pathlib.Path.cwd() / "reports")


if __name__ == "__main__":
    main()
