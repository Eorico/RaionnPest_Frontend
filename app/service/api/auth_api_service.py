import requests

from .base import BaseApiService, IAuthService

# Shared, user-facing wording for the failures the API can return.
_OFFLINE_MSG = ("Cannot reach the server. Check your internet connection "
                "and try again.")
_TIMEOUT_MSG = "The server took too long to respond. Please try again."
_GENERIC_MSG = "Something went wrong on the server. Please try again."


def _detail(response) -> str:
    """
    Pull the human-readable reason out of a failed response.

    The API answers every error with {"detail": "..."} — including 429s from the
    rate limiter — but an empty body or an HTML error page must not raise here,
    so fall back to a plain message instead.
    """
    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict):
        for key in ("detail", "message", "title"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    if response.status_code == 429:
        return "Too many attempts. Please wait a minute and try again."
    if response.status_code >= 500:
        return _GENERIC_MSG
    text = (response.text or "").strip()
    return text[:300] if text else f"Request failed ({response.status_code})."


def _network_message(error: Exception) -> str:
    if isinstance(error, requests.exceptions.Timeout):
        return _TIMEOUT_MSG
    if isinstance(error, requests.exceptions.ConnectionError):
        return _OFFLINE_MSG
    return str(error) or _GENERIC_MSG


class AuthApiService(BaseApiService, IAuthService):

    def login_service(self, username: str, password: str) -> tuple[bool, str]:
        try:
            response = self._session.post(
                f"{self._base_url}/auth/login",
                json={"username": username, "password": password},
                timeout=5,
            )
            if response.status_code == 200:
                token = None
                try:
                    token = response.json().get("access_token")
                except ValueError:
                    pass
                if token:
                    self._session.headers.update(
                        {"Authorization": f"Bearer {token}"})
                return True, "Login Successful"
            if response.status_code in (400, 401, 404):
                return False, "Incorrect username or password."
            return False, _detail(response)
        except Exception as e:
            return False, _network_message(e)

    def register_service(self, username: str, password: str,
                         email: str) -> tuple[bool, str]:
        try:
            response = self._session.post(
                f"{self._base_url}/auth/register",
                json={"username": username, "password": password, "email": email},
                timeout=10,
            )
            if response.status_code == 201:
                return True, "Registered successfully"
            return False, _detail(response)
        except Exception as e:
            return False, _network_message(e)

    def forgot_password_service(self, username: str) -> tuple[bool, str]:
        try:
            response = self._session.post(
                f"{self._base_url}/auth/forgot-password",
                json={"username": username},
                timeout=20,          # sending the OTP e-mail can be slow
            )
            if response.status_code == 200:
                try:
                    message = response.json().get("message", "")
                except ValueError:
                    message = ""
                return True, str(message or "Code sent")
            return False, _detail(response)
        except Exception as e:
            return False, _network_message(e)

    def reset_password_service(self, username: str, otp: str,
                               new_password: str) -> tuple[bool, str]:
        try:
            response = self._session.post(
                f"{self._base_url}/auth/reset-password",
                json={"username": username, "otp": otp,
                      "new_password": new_password},
                timeout=10,
            )
            if response.status_code == 200:
                return True, "Password reset successfully"
            return False, _detail(response)
        except Exception as e:
            return False, _network_message(e)

    def logout_service(self) -> None:
        self._session.headers.pop("Authorization", None)
