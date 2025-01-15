import os

import requests

API_BASE = os.getenv("API_URL")


def update_user_region(telegram_id: str, region: str):
    """Update user region

    Args:
        telegram_id (str): Telegram id of the user
        region (str): Region of the user
    """
    user_props = {"region": region}

    r = requests.patch(
        f"{API_BASE}/users",
        params={"telegram_id": f"eq.{telegram_id}"},
        headers={"Content-Type": "application/json"},
        json=user_props,
        timeout=5,
    )

    r.raise_for_status()


def update_user_mute_code(telegram_id: str, mute_code: str, value: bool = False):
    """Set mute code for the user

    Args:
        telegram_id (str): Telegram id of the user
        mute_code (str): Mute code
        value (bool, optional): Mute value. Defaults to False.
    """
    user_props = {f"notify_{mute_code.lower()}": value}

    r = requests.patch(
        f"{API_BASE}/users",
        params={"telegram_id": f"eq.{telegram_id}"},
        headers={"Content-Type": "application/json"},
        json=user_props,
        timeout=5,
    )

    r.raise_for_status()


def soft_delete_user(telegram_id: str):
    """Soft delete user

    Args:
        telegram_id (str): Telegram id of the user
    """
    user_props = {"is_deleted": True}

    r = requests.patch(
        f"{API_BASE}/users",
        params={"telegram_id": f"eq.{telegram_id}"},
        headers={"Content-Type": "application/json"},
        json=user_props,
        timeout=5,
    )

    r.raise_for_status()


def create_or_update_user(user_props: dict):
    """Create or update user

    Args:
        user_props (dict): User properties
    """
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
