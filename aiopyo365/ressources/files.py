"""Module that provide office 365 services by exposing classes
that encapsulate GRAPH microsoft API calls.

https://docs.microsoft.com/en-us/graph/overview?view=graph-rest-1.0

available services:
    - Sharepoint
"""


import aiohttp
import os
import aiopyo365.clients.factories as factories
from dataclasses import dataclass, field
from typing import Coroutine, Generator, Literal


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

    async def upload(self, file_path: str, file_name: str) -> None:
        """Upload file to sharepoint.

        Arg(s):
            path: path of the file to be uploaded
            file_name: name to give to the file in sharepoint when uploaded

        """
        file_size = os.path.getsize(file_path)
        if file_size < 4000000:
            await self._upload_small_file(file_path, file_name)
        else:
            await self._upload_large_file(
                file_path, file_size, file_name, conflict_behavior="replace"
            )


    async def _upload_small_file(self, path: str, file_name: str) -> Coroutine:
        """Upload file less than 4 MB to sharepoint.

        ref: https://docs.microsoft.com/en-us/graph/api/driveitem-put-content?view=graph-rest-1.0&tabs=http

        Arg(s):
            path: path of the file to be uploaded
            file_name: name to give to the file in sharepoint when uploaded
        Return:
            A request Response object
        """
        endpoint = f"{self.base_url}/drive/items/root:/{file_name}:/content"
        content = self._read_file(path)
        headers = {"Content-Type": "application/octet-stream"}
        async with self.session.put(
            f"{endpoint}", headers=headers, data=content
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _upload_large_file(
        self,
        file_path: str,
        file_byte_size: int,
        filename: str,
        conflict_behavior: Literal["fail", "replace", "rename"] = "fail",
    ) -> Coroutine:
        """Upload large file (> 4MB) using an upload session. File should be less than 60MB.

        ref: https://docs.microsoft.com/en-us/graph/api/driveitem-createuploadsession?view=graph-rest-1.0#upload-bytes-to-the-upload-session

        Arg(s):
            file_path: file path to be uploaded
            file_byte_size: size of the file to be uploaded in bytes
            filename: name to give to the file in sharepoint when uploaded
            conflict_behavior: how to handle a file that has already the same name should be one of fail, replace, rename

        Return:
            A request Response object
        """
        resp = await self._create_upload_session(filename, conflict_behavior)
        upload_url = resp["uploadUrl"]
        if file_byte_size < self._max_upload_size:
            content = self._read_file(file_path)
            headers = {
                "Content-Type": "application/octet-stream",
                "Content-Length": f"{file_byte_size}",
                "Content-Range": f"bytes 0-{file_byte_size-1}/{file_byte_size}",
            }
            async with self.session.put(
                upload_url, data=content, headers=headers
            ) as resp:
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
            f"{self._base_url}/drive/items/root:/{upload_filename}:/createUploadSession",
            params=str(data),
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    def _read_file(self, path: str) -> bytes:
        """Read file as bytes

        Arg:
            path: path of the file to read


            content of the file as bytes
        """
        with open(path, "rb") as f:
            content = f.read()
            return content

    def _bytes_from_file(self, filename, chunksize) -> Generator[bytes, None, None]:

        with open(filename, "rb") as f:
            data = f.read(chunksize)
            yield data
            while data:
                data = f.read(chunksize)
                yield data