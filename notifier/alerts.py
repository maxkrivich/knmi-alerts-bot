import datetime
import os

import requests
from loguru import logger

API_BASE = os.getenv("API_URL")


def to_psql_datetime(date: str) -> str:
    dt = datetime.datetime.fromisoformat(date)

    return dt.strftime("%Y-%m-%d %H:%M:%S.%f %z")[:-3]


def to_psql_date(date: str) -> str:
    dt = datetime.datetime.fromisoformat(date)

    return dt.strftime("%Y-%m-%d")


def get_alert_for_the_region(region: str, issue_date: str | None = None) -> dict:  # not sure about date type here
    """Get alert for the region"""

    if issue_date is None:
        issue_date = datetime.datetime.now().isoformat()

    r = requests.get(
        f"{API_BASE}/alerts",
        params={"region": f"eq.{region}", "issue_date": f"eq.{to_psql_date(issue_date)}"},
        headers={"Content-Type": "application/json"},
        timeout=5,
    )

    r.raise_for_status()
    return r.json()


def create_report_for_the_region(region: str, alerts: list) -> bool:
    """Create report for the region"""

    now = datetime.datetime.now().isoformat()

    alert_parameters = {
        "region": region,
        "issue_date": to_psql_date(now),
        "alerts": alerts,  ## time to have json line {"phenomenon": {data about it}}
        "created_at": to_psql_datetime(now),
        "updated_at": to_psql_datetime(now),
    }

    r = requests.post(
        f"{API_BASE}/alerts",
        json=alert_parameters,
        headers={"Content-Type": "application/json"},
        timeout=5,
    )

    if r.status_code == 409:
        logger.info(f"Report for {region} already exists")
        return False

    r.raise_for_status()
    return True


def update_report_for_the_region(region: str, issue_date: str, alerts: list) -> bool:  # not sure about date type here
    """"""

    now = datetime.datetime.now().isoformat()

    alert_parameters = {
        "alerts": alerts,  # think how to update the json here, append to the json idk
        "updated_at": to_psql_datetime(now),
    }

    r = requests.patch(
        f"{API_BASE}/alerts",
        params={"region": f"eq.{region}", "issue_date": f"eq.{to_psql_date(issue_date)}"},
        json=alert_parameters,
        headers={"Content-Type": "application/json"},
        timeout=5,
    )

    r.raise_for_status()
    return True
