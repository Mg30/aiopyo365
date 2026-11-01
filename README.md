# aiopyo365

**Project background:** aiopyo365 was started in December 2022, when Microsoft's
official Python SDK was still in
[public preview](https://devblogs.microsoft.com/microsoft365dev/introducing-the-microsoft-graph-python-sdk-now-available-for-public-preview/).
It provides a lightweight asynchronous client focused on selected Microsoft Graph
and SharePoint operations. For new integrations, consider the
[official Microsoft Graph Python SDK](https://github.com/microsoftgraph/msgraph-sdk-python),
which reached
[general availability in November 2023](https://devblogs.microsoft.com/microsoft365dev/introducing-the-microsoft-graph-python-sdk/).

An asynchronous Python client for selected
[Microsoft Graph v1.0](https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0)
resources, built on `aiohttp`. It provides client-credentials authentication,
SharePoint site lookup, and drive item operations such as listing, searching,
uploading, and downloading files. It is not a complete Microsoft Graph SDK.

## Installation and compatibility

```bash
pip install aiopyo365==0.1.1a0
```

The published package is an **alpha release**. Package metadata declares Python
**>=3.8.1,<4.0**. The repository's release workflow builds on Python 3.8 but does
not run tests or publish to PyPI. It uses the retired `ubuntu-18.04` runner;
there is no current CI compatibility matrix to substantiate broader support.

## Application registration

Register an application in Microsoft Entra ID and supply its tenant ID, client
ID, and client secret through your environment:

- `TENANT_ID`
- `CLIENT_ID`
- `CLIENT_SECRET`

The bundled `GraphAuthProvider` uses the **client credentials** grant and the
`https://graph.microsoft.com/.default` scope. Configure the Microsoft Graph
**application permissions** needed for your chosen operations and obtain admin
consent. Delegated user sign-in is not implemented by this provider.

See [application registration](https://learn.microsoft.com/en-us/graph/auth-register-app-v2)
and [application-only access](https://learn.microsoft.com/en-us/graph/auth-v2-service).
Do not commit credentials or print authorization headers.

## First request: look up a SharePoint site

Also set `SHAREPOINT_HOSTNAME` (for example, `contoso.sharepoint.com`) and
`SHAREPOINT_SITE` (the site name under `/sites/`). Save this as `example.py`
and run `python example.py` after configuring the application permissions:

```python
import asyncio
import os

import aiohttp

from aiopyo365.factories.sites import SitesFactory
from aiopyo365.providers.auth import GraphAuthProvider


async def main():
    auth_provider = GraphAuthProvider(
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        tenant_id=os.environ["TENANT_ID"],
    )
    headers = await auth_provider.auth()
    async with aiohttp.ClientSession(headers=headers) as session:
        sites = SitesFactory().create(session=session)
        site = await sites.get_sites_by_server_relative_url(
            hostname=os.environ["SHAREPOINT_HOSTNAME"],
            site_name=os.environ["SHAREPOINT_SITE"],
        )
        print(site["id"])


if __name__ == "__main__":
    asyncio.run(main())
```

`ClientSession` is an asynchronous context manager; do not `await` its constructor.
The example performs a read and closes the HTTP session on exit.

## Resources and factories

The public import path is spelled `ressources` for compatibility:

```python
from aiopyo365.ressources.files import DriveItems
from aiopyo365.factories.drive_items import DriveItemsSitesFactory
```

`DriveItemsSitesFactory(site_id=...).create(session=session)` configures the base
URL for a site's drive. Direct `DriveItems` usage requires an authenticated
`aiohttp.ClientSession` and an appropriate Graph base URL. Factories also exist
for groups, drives, users, and `/me`; `/me` requires delegated authentication and
cannot be used with the bundled client-credentials provider.

## SharePoint service

`SharePointService` combines site discovery and drive operations and owns its HTTP
session. This function reads an existing folder using its drive item ID:

```python
from aiopyo365.services.sharepoint import SharePointService


async def list_folder(auth_provider, hostname, site_name, folder_item_id):
    async with SharePointService(auth_provider, hostname, site_name) as sharepoint:
        page = await sharepoint.list_files(folder_item_id)
        return page["value"]
```

Methods return Graph response data. Collection calls return one page; callers
must handle `@odata.nextLink` when present. The service also exposes `upload`,
`download`, and `search_item`. Review their implementation before using them for
writes; uploads use memory buffers and are not a resumable transfer engine.
Existing HTTP sessions retain the authorization header supplied at creation, so
long-running jobs must manage session and token renewal explicitly.

## Development

```bash
poetry install
```

The existing tests connect to Microsoft Graph and some upload files. They require
`OFFICE_CLIENT_ID`, `OFFICE_CLIENT_SECRET`, and `OFFICE_TENANT_ID`, as well as the
SharePoint identifiers used in the test files. Run them only against an application
and site intended for testing. README examples do not imply a successful live
Graph test or support for every Graph endpoint.
