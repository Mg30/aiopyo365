from dataclasses import dataclass, field

import aiohttp
from aiopyo365.providers.auth import GraphAuthProvider
from aiopyo365.clients.factories import DriveItemsSitesFactory


@dataclass
class SharePointService(object):
    auth_provider: GraphAuthProvider
    hostname: str
    site_name: str

    async def __aenter__(self):
        auth_header = await self.auth_provider.auth()
        self.session = aiohttp.ClientSession(headers=auth_header)
        drive_item_site = DriveItemsSitesFactory()
        self.sharepoint = await SharePointClient.create(
            self.hostname,
            self.site_name,
            session=self.session,
        )
        return self.sharepoint

    async def __aexit__(self, *err):
        await self.session.close()
        self.session = None
 