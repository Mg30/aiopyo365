""" API to Microsoft Graph resources types for working with files:

Drive - Represents a logical container of files, like a document library or a user's OneDrive.
DriveItem - Represents an item within a drive, like a document, photo, video, or folder.

https://learn.microsoft.com/en-us/graph/api/resources/onedrive?view=graph-rest-1.0
"""


import aiohttp
from dataclasses import dataclass, field
from typing import Coroutine, Literal


@dataclass
class DriveItems(object):
    """Class that encapsulate API calls to deals with drive items ressource.
     ref : https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0

    Arg(s):
        auth_client: a client with Microsoft graph auth capabilities
        hostname: name of the host like contoso.com
        site_name: name of sharepoint site to interact with

    """

    base_url: str
    session: aiohttp.ClientSession
    _max_upload_size: int = field(init=False, default=60000000)

    async def list_children(self, item_id: str) -> Coroutine:
        """List all children items from item_id.

        ref: https://docs.microsoft.com/en-us/graph/api/driveitem-list-children?view=graph-rest-1.0&tabs=http

        Args:
            item_id: id of item to list children for
        Return:
            A Coroutine
        """
        async with self.session.get(
            f"{self.base_url}/drive/items/{item_id}/children"
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def search_item(self, query: str) -> Coroutine:
        """Search item according to query.

        ref: https://docs.microsoft.com/en-us/graph/api/driveitem-search?view=graph-rest-1.0&tabs=http
        Arg(s):
            query: what to search for in sharepoint from root
        Return:
            A Coroutine
        """
        async with self.session.get(
            f"{self.base_url}/drive/root/search(q='{query}')"
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def upload_small_file(self, content: bytes, file_name: str) -> Coroutine:
        """Upload file less than 4 MB to sharepoint.

        ref: https://docs.microsoft.com/en-us/graph/api/driveitem-put-content?view=graph-rest-1.0&tabs=http

        Arg(s):
            content: content of the file as bytes
            file_name: name to give to the file in sharepoint when uploaded
        Return:
            A request Response object
        """
        endpoint = f"{self.base_url}/drive/items/root:/{file_name}:/content"
        headers = {"Content-Type": "application/octet-stream"}
        async with self.session.put(
            f"{endpoint}", headers=headers, data=content
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def upload_large_file(
        self,
        content: bytes,
        file_byte_size: int,
        filename: str,
        conflict_behavior: Literal["fail", "replace", "rename"] = "fail",
    ) -> Coroutine:
        """Upload large file (> 4MB) using an upload session. File should be less than 60MB.
        ref: https://docs.microsoft.com/en-us/graph/api/driveitem-createuploadsession?view=graph-rest-1.0#upload-bytes-to-the-upload-session

        Arg(s):
            content: content of the file as bytes
            file_byte_size: size of the file to be uploaded in bytes
            filename: name to give to the file in sharepoint when uploaded
            conflict_behavior: how to handle a file that has already the same name should be one of fail, replace, rename

        Return:
            A request Response object
        """
        resp = await self._create_upload_session(filename, conflict_behavior)
        upload_url = resp["uploadUrl"]
        headers = {
            "Content-Type": "application/octet-stream",
            "Content-Length": f"{file_byte_size}",
            "Content-Range": f"bytes 0-{file_byte_size-1}/{file_byte_size}",
        }
        async with self.session.put(upload_url, data=content, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _create_upload_session(
        self,
        upload_filename: str,
        conflict_behavior: Literal["fail", "replace", "rename"],
    ) -> Coroutine:
        """Create an upload session in ordre to upload file larger than 4 MB.

        ref: https://docs.microsoft.com/en-us/graph/api/driveitem-createuploadsession?view=graph-rest-1.0#create-an-upload-session

        Arg(s):
            upload_filename: name to give in sharepoint to the file uploaded
            conflict_behavior: how to handle a file that has already the same name should be one of fail, replace, rename

        Return
            A request Response object
        """
        data = {
            "item": {
                "@microsoft.graph.conflictBehavior": conflict_behavior,
            }
        }
        async with self.session.post(
            f"{self.base_url}/drive/items/root:/{upload_filename}:/createUploadSession",
            params=str(data),
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def download_file(self, item_id):
        async with self.session.get(f"{self.base_url}/drive/items/{item_id}?select=id,@microsoft.graph.downloadUrl") as resp:
            if resp.status == 200:
                response_json = await resp.json()
                download_url = response_json["@microsoft.graph.downloadUrl"]
                async with self.session.get(download_url) as download_resp:
                    return await download_resp.read()
            else:
                raise ValueError(f"{resp.text}")