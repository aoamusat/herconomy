import requests
from typing import Any, Dict
from django.contrib.auth import get_user_model

User = get_user_model()


def call_webhook(url: str, payload: Dict[str, Any]) -> Any:
    """
    Call a webhook with the given payload

    :param url: The URL of the webhook
    :param payload: The payload to send with the POST request
    :return: The response from the webhook
    """
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx and 5xx)
        return response.status_code  # Return the response JSON data
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the request
        print(f"Error calling webhook: {e}")
        return None


def resolve_account(account_number: str) -> User:
    try:
        return User.get_by_account_number(account_number)
    except User.DoesNotExist:
        return None
