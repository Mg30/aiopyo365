import os
import aiohttp
import pytest
from dotenv import load_dotenv

from aiopyo365.factories.drive_items import DriveItemsSitesFactory
from aiopyo365.factories.sites import SitesFactory
from aiopyo365.providers.auth import GraphAuthProvider

load_dotenv()


@pytest.fixture(scope="session")
def auth_provider():
    return GraphAuthProvider(
        client_id=os.environ["OFFICE_CLIENT_ID"],
        client_secret=os.environ["OFFICE_CLIENT_SECRET"],
        tenant_id=os.environ["OFFICE_TENANT_ID"],
    )


@pytest.mark.asyncio
async def test_search_item(auth_provider):
    auth_header = await auth_provider.auth()
    session = aiohttp.ClientSession(headers=auth_header)
    site = SitesFactory().create(session)
    resp = await site.get_sites_by_server_relative_url(
        hostname=os.environ["SHAREPOINT_HOSTNAME"],
        site_name=os.environ["SHAREPOINT_SITE"],
    )
    site_id = resp["id"]

    client = DriveItemsSitesFactory(site_id=site_id).create(session=session)
    res = await client.search_item("Traitements")
    assert res["value"]


@pytest.mark.asyncio
async def test_list_children(auth_provider):
    auth_header = await auth_provider.auth()
    session = aiohttp.ClientSession(headers=auth_header)
    site = SitesFactory().create(session)
    resp = await site.get_sites_by_server_relative_url(
        hostname=os.environ["SHAREPOINT_HOSTNAME"],
        site_name=os.environ["SHAREPOINT_SITE"],
    )
    site_id = resp["id"]

    client = DriveItemsSitesFactory(site_id=site_id).create(session=session)
    res = await client.list_children(item_id="01WC3XZVEWH2HC7QEWE5DIX4KHFWABH2TU")
    print(res)
    assert False
