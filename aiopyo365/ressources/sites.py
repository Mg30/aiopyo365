import aiohttp
from dataclasses import dataclass
from typing import Coroutine


@dataclass
class Site(object):
    """Class to interact with Site ressource.
    A site resource represents a team site in SharePoint.

    https://learn.microsoft.com/en-us/graph/api/resources/site?view=graph-rest-1.0
    """

    base_url: str
    session: aiohttp.ClientSession

    async def get_sites_by_server_relative_url(
        self, hostname: str, site_name: str
    ) -> Coroutine:
        """Retrieve properties and relationships for a site resource.

        https://learn.microsoft.com/en-us/graph/api/site-get?view=graph-rest-1.0&tabs=http

        Args:
            hostname (str): Sharepoint hostname ex: contoso.sharepoint.com
            site_name (str): server-relative URL for a site resource

        Returns:
            Coroutine: containnig the response of the query
        """
        async with self.session.get(
            f"{self.base_url}/sites/{hostname}:/sites/{site_name}"
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_tenant_root_site(self) -> Coroutine:
        """Retrieve properties and relationships for the root SharePoint site within a tenant.

        Returns:
            Coroutine: containnig the response of the query
        """
        async with self.session.get(f"{self.base_url}/sites/root") as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_group_team_site(self, group_id: str) -> Coroutine:
        """Retrieve properties and relationships for a team site for a group:

        Args:
            group_id (str): id of the group to acess

        Returns:
            Coroutine: containnig the response of the query
        """
        async with self.session.get(
            f"{self.base_url}/groups/{group_id}/sites/root"
        ) as resp:
            resp.raise_for_status()
            return await resp.json()
