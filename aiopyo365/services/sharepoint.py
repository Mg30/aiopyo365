import aiohttp
import os
from aiopyo365.providers.auth import GraphAuthProvider
from aiopyo365.factories.drive_items import DriveItemsSitesFactory
from aiopyo365.factories.sites import SitesFactory
from aiopyo365.ressources.files import DriveItems
from aiopyo365.ressources.sites import Site
from dataclasses import dataclass, field
from typing import Coroutine


@dataclass
class SharePointService(object):
    auth_provider: GraphAuthProvider
    hostname: str
    site_name: str
    _site_client: Site = field(init=False)
    _drive_items_client: DriveItems = field(init=False)
    session: aiohttp.ClientSession = field(init=False)

    async def __aenter__(self):
        auth_header = await self.auth_provider.auth()
        self.session = aiohttp.ClientSession(headers=auth_header)

        self._site_client = SitesFactory().create(session=self.session)
        site_id = await self.get_site_id()

        self._drive_items_client = DriveItemsSitesFactory(site_id=site_id).create(
            session=self.session
        )
        return self

    async def __aexit__(self, *err):
        await self.session.close()
        self.session = None

    async def get_site_id(self) -> str:
        """Couritne to fetch the site id given hostname and site_name

        Returns:
            str: representing the side id
        """
        resp = await self._site_client.get_sites_by_server_relative_url(
            hostname=self.hostname, site_name=self.site_name
        )
        return resp["id"]

    async def upload(
        self, file_path: str, file_name: str, conflict_behavior="fail"
    ) -> Coroutine:
        """Upload file to sharepoint

        Arg(s):
            path: path of the file to be uploaded
            file_name: name to give to the file in sharepoint when uploaded

        """
        content = self._read_file_as_bytes(file_path)
        file_byte_size = os.path.getsize(file_path)
        if file_byte_size < 4000000:
            return await self._drive_items_client.upload_small_file(content, file_name)
        else:
            return await self._drive_items_client.upload_large_file(
                content, file_byte_size, file_name, conflict_behavior=conflict_behavior
            )

    def _read_file_as_bytes(self, path: str) -> bytes:
        """Read a file at path and return its content as bytes

        Args:
            path (str): to the file to read content from

        Returns:
            bytes: content of the file
        """
        with open(path, "rb") as f:
            content = f.read()
            return content
