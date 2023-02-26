# aiopyo365

Async wrapper for Python >= 3.8 around [Microsoft v1.0 graph API](https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0&preserve-view=true).


## Installation

`pip install aiopyo365`


## Requirements

python 3.8 or greater

### Application registration
Microsoft Graph APi requires to be authentificated. You will need to 
have a [registred application](https://learn.microsoft.com/en-us/graph/auth-register-app-v2) in Azure that will provide you: 
* client id 
* client secret

You will also need to have the [required permissions](https://learn.microsoft.com/en-us/graph/permissions-reference) to be able to interact with  [the desired ressources](https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0&preserve-view=true). 


## Installation
#TODO

## Authentification

To authentificate you can use the `GraphAuthProvider` class in the `providers.auth module`.

here is how to use this class. it assumes that you have set the folowing environnement variables :

* CLIENT_ID
* CLIENT_SECRET
* TENANT_ID

The class provide a method to fetch the token in the
form of a `dict`.

```python
import asyncio
from aiopyo365.providers.auth import GraphAuthProvider

async def fetch_auth_header():
    auth_provider =  GraphAuthProvider(
            client_id=os.environ["CLIENT_ID"],
            client_secret=os.environ["CLIENT_SECRET"],
            tenant_id=os.environ["TENANT_ID"],
        )
    return await auth_provider.auth()


if __name__ == '__main__':
    auth_header = asyncio.run(fetch_auth_header())
    print(auth_header)


# output : {"authorization": "<token type> <token>"}
```

## Ressources
The library tries to resemble the organization of the graph API documentation.

for instance in the Graph documentation you will find the [`DriveItems`](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0) under the `Files` section.  
In  `aiopyo365`: 
```python
from aiopyo365.ressources.files import DriveItems
```
If you want to work directly with ressources class you will need to instanciate a `aiohttp session` with `auth header` and instanciate the client class.

```python
import asyncio
import aiohttp
from aiopyo365.ressources.files import DriveItems

async def upload_smallfile(content,file_name):
    auth_provider =  GraphAuthProvider(
            client_id=os.environ["CLIENT_ID"],
            client_secret=os.environ["CLIENT_SECRET"],
            tenant_id=os.environ["TENANT_ID"],
        )
    auth_header = await auth_provider.auth()
    session = await aiohttp.ClientSession(headers=auth_header)
    drive_items_client = DriveItems(base_url="url", session=session)
    await drive_items_client.upload_small_file(content, file_name)
    
```
You can also use factories
to work with variant of ressources
here we work with a driveItems dedicated to SharePoint (site).

```python
import asyncio
import aiohttp
import os
from aiopyo365.providers.auth import GraphAuthProvider
from aiopyo365.factories.drive_items import DriveItemsSitesFactory

async def upload_smallfile(content,file_name):
    auth_provider =  GraphAuthProvider(
            client_id=os.environ["CLIENT_ID"],
            client_secret=os.environ["CLIENT_SECRET"],
            tenant_id=os.environ["TENANT_ID"],
        )
    auth_header = await auth_provider.auth()
    session = await aiohttp.ClientSession(headers=auth_header)
    drive_items_client = DriveItemsSitesFactory(site_id="site_id").create(session=session)
    await drive_items_client.upload_small_file(content, file_name)
    
```

## Services

`aiopyo365` provide also service class that encapsulate many ressource to match business logic. It hides dealing with instanciate class client and so on.
Let's reuse the upload of a file example from above and use the `SharePointService`

```python
import os
from aiopyo365.providers.auth import GraphAuthProvider
from aiopyo365.services.sharepoint import SharePointService

async def upload_smallfile(content,file_name):
    auth_provider =  GraphAuthProvider(
            client_id=os.environ["CLIENT_ID"],
            client_secret=os.environ["CLIENT_SECRET"],
            tenant_id=os.environ["TENANT_ID"],
        )
    async with SharePointService(auth_provider,"SHAREPOINT_HOSTNAME","SHAREPOINT_SITE") as sharepoint:
        resp = await sharepoint.upload(
            small_file_path, "small_file", conflict_behavior="replace"
        )
        assert resp["createdDateTime"]
    
```