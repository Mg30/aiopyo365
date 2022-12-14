""" This module provide auth strategy to indentify with Microsft Graph API.

Exemple :  GraphAuthProvider provide an async auth provider

ref : https://docs.microsoft.com/en-us/graph/auth/?context=graph%2Fapi%2F1.0&view=graph-rest-1.0
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict
import aiohttp


@dataclass
class GraphAuthProvider(object):
    """Provide authentification against Microsoft Graph api using
    aiohttp module.
    It exposes a property auth_header that return a dict with authorization infos
    {"authorization": "token_type access_token"}
    It handle refreshing the token when it is expired.
    """

    client_id: str
    client_secret: str
    tenant_id: str
    _scope: str = field(init=False, default="https://graph.microsoft.com/.default")
    _access_token: str = field(init=False, default="")
    _token_type: str = field(init=False)
    _grant_type: str = field(init=False, default="client_credentials")
    _expiration_time: datetime = field(init=False, default_factory=datetime.now)

    async def auth(self) -> Dict[str, str]:
        """Exposes a property auth_header that return a dict with authorization infos
        handle refreshing the token when it is expired.

        Returns:
            Dict[str, str]: authorization infos
        """
        if not self._access_token or self._is_token_expire():
            await self._fetch_access_token()
        return {"authorization": f"{self._token_type} {self._access_token}"}

    def __post_init__(self):
        self._auth_endpoint = (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        )

    def _is_token_expire(self, time: datetime = datetime.now()) -> bool:
        """Checks if the token is expired

        Args:
            time (datetime, optional): time to check against. Defaults to datetime.now().

        Returns:
            bool: token is expired or not
        """
        return time > self._expiration_time

    async def _fetch_access_token(self) -> None:
        """Handle fetching the token by calling the Microsoft Auth Endpoint

        Raises:
            ValueError: aiohttp.response.text()
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        form_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": self._grant_type,
            "scope": self._scope,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self._auth_endpoint, data=form_data, headers=headers
            ) as resp:
                if resp.status != 200:
                    raise ValueError(await resp.text())
                else:
                    data = await resp.json()
                    self._access_token = data["access_token"]
                    self._expiration_time = datetime.now() + timedelta(
                        seconds=data["expires_in"]
                    )
                    self._token_type = data["token_type"]
