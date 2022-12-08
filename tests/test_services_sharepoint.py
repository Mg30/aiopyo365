from aiopyo365.auth_providers import GraphAuthProvider
from aiopyo365.services import SharePointService
from aiopyo365.clients import SharePointClient
from dotenv import load_dotenv
import pytest
import os
import aiohttp

load_dotenv()


@pytest.fixture(scope="session")
def auth_provider():
    return GraphAuthProvider(
        client_id=os.environ["OFFICE_CLIENT_ID"],
        client_secret=os.environ["OFFICE_CLIENT_SECRET"],
        tenant_id=os.environ["OFFICE_TENANT_ID"],
    )


@pytest.mark.asyncio
async def test_sharepoint_client_init(auth_provider):
    try:
        auth_header = await auth_provider.auth()
        session = aiohttp.ClientSession(headers=auth_header)
        sharepoint = await SharePointClient.create(
            os.environ["SHAREPOINT_HOSTNAME"],
            os.environ["SHAREPOINT_SITE"],
            session=session,
        )
        await session.close()
    except Exception:
        pytest.fail("Fail init")


@pytest.fixture
def small_file_path():
    return "tests/test_data/small.txt"


@pytest.fixture
def large_file_path():
    return "tests/test_data/large_file.xlsx"


@pytest.mark.asyncio
async def test_upload_large_file(auth_provider, large_file_path):
    async with SharePointService(
        auth_provider, os.environ["SHAREPOINT_HOSTNAME"], os.environ["SHAREPOINT_SITE"]
    ) as sharepoint:
        file_size = os.path.getsize(large_file_path)
        resp = await sharepoint._upload_large_file(
            large_file_path, file_size, "large_file"
        )
        print(resp)
