from aiopyo365.providers.auth import GraphAuthProvider
from aiopyo365.services.sharepoint import SharePointService
from dotenv import load_dotenv
import pytest
import os

load_dotenv()


@pytest.fixture(scope="session")
def auth_provider():
    return GraphAuthProvider(
        client_id=os.environ["OFFICE_CLIENT_ID"],
        client_secret=os.environ["OFFICE_CLIENT_SECRET"],
        tenant_id=os.environ["OFFICE_TENANT_ID"],
    )


@pytest.fixture
def small_file_path():
    return "tests/test_data/small.txt"


@pytest.fixture
def large_file_path():
    return "tests/test_data/large_file.xlsx"


@pytest.mark.asyncio
async def test_upload_small_file(auth_provider, small_file_path):
    async with SharePointService(
        auth_provider, os.environ["SHAREPOINT_HOSTNAME"], os.environ["SHAREPOINT_SITE"]
    ) as sharepoint:
        resp = await sharepoint.upload(
            small_file_path, "small_file", conflict_behavior="replace"
        )
        assert resp["createdDateTime"]


@pytest.mark.asyncio
async def test_upload_large_file(auth_provider, large_file_path):
    async with SharePointService(
        auth_provider, os.environ["SHAREPOINT_HOSTNAME"], os.environ["SHAREPOINT_SITE"]
    ) as sharepoint:
        resp = await sharepoint.upload(
            large_file_path, "large_file", conflict_behavior="replace"
        )
        assert resp["createdDateTime"]


@pytest.mark.asyncio
async def test_download(auth_provider):
    async with SharePointService(
        auth_provider, os.environ["SHAREPOINT_HOSTNAME"], os.environ["SHAREPOINT_SITE"]
    ) as sharepoint:
        await sharepoint.download(
            item_id="01WC3XZVGGTAUUPZCRVNHJKS5AY5P7ZZW6", path="test"
        )
        assert os.path.exists("test")
        os.remove("test")


@pytest.mark.asyncio
async def test_search_item(auth_provider):
    async with SharePointService(
        auth_provider, os.environ["SHAREPOINT_HOSTNAME"], os.environ["SHAREPOINT_SITE"]
    ) as sharepoint:
        resp = await sharepoint.search_item(query="Traitements")

        assert resp["value"]


@pytest.mark.asyncio
async def test_list_files(auth_provider):
    async with SharePointService(
        auth_provider, os.environ["SHAREPOINT_HOSTNAME"], os.environ["SHAREPOINT_SITE"]
    ) as sharepoint:
        resp = await sharepoint.list_files(
            parent_id="01WC3XZVEWH2HC7QEWE5DIX4KHFWABH2TU"
        )

        assert resp["value"]
