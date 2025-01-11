import requests

API_BASE = "http://db_api:3000"


def update_user_region(telegram_id: str, region: str):
    user_props = {"region": region}

    r = requests.patch(
        f"{API_BASE}/users",
        params={"telegram_id": f"eq.{telegram_id}"},
        headers={"Content-Type": "application/json"},
        json=user_props,
        timeout=5,
    )

    r.raise_for_status()


def update_user_mute_code(telegram_id: str, mute_code: str):
    user_props = {f"notify_{mute_code.lower()}": False}

    r = requests.patch(
        f"{API_BASE}/users",
        params={"telegram_id": f"eq.{telegram_id}"},
        headers={"Content-Type": "application/json"},
        json=user_props,
        timeout=5,
    )

    r.raise_for_status()


def soft_delete_user(telegram_id: str):
    user_props = {"is_deleted": True}

    r = requests.patch(
        f"{API_BASE}/users",
        params={"telegram_id": f"eq.{telegram_id}"},
        headers={"Content-Type": "application/json"},
        json=user_props,
        timeout=5,
    )

    r.raise_for_status()


def create_or_update_user(user_props: dict) -> bool:
    r = requests.post(
        f"{API_BASE}/users",
        headers={"Content-Type": "application/json"},
        json=user_props,
        timeout=5,
    )

    if r.status_code == 409:
        r = requests.patch(
            f"{API_BASE}/users",
            params={"telegram_id": f"eq.{user_props['telegram_id']}"},
            headers={"Content-Type": "application/json"},
            json=user_props,
            timeout=5,
        )

        r.raise_for_status()
    else:
        r.raise_for_status()
