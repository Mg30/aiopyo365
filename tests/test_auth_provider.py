from datetime import datetime, timedelta
from aiopyo365.providers.auth import GraphAuthProvider
from dotenv import load_dotenv
import os
import pytest
import asyncio

load_dotenv()


def test_graph_auth_provider_init():
    try:
        GraphAuthProvider(
            client_id=os.environ["OFFICE_CLIENT_ID"],
            client_secret=os.environ["OFFICE_CLIENT_SECRET"],
            tenant_id=os.environ["OFFICE_TENANT_ID"],
        )
    except Exception:
        pytest.fail("Fail init")


@pytest.fixture(scope="session")
def graph_auth_provider():
    return GraphAuthProvider(
        client_id=os.environ["OFFICE_CLIENT_ID"],
        client_secret=os.environ["OFFICE_CLIENT_SECRET"],
        tenant_id=os.environ["OFFICE_TENANT_ID"],
    )


@pytest.mark.asyncio
async def test_fetch_access_token(graph_auth_provider):
    try:
        await graph_auth_provider._fetch_access_token()
    except Exception:
        pytest.fail("Fail fetch token")


@pytest.mark.asyncio
async def test_auth_header_is_present(graph_auth_provider):
    auth = await graph_auth_provider.auth()
    assert auth["authorization"]


def test_expiration_time_token_is_false(graph_auth_provider):
    asyncio.run(graph_auth_provider._fetch_access_token())
    assert not graph_auth_provider._is_token_expire()


def test_expiration_time_token_is_true(graph_auth_provider):
    asyncio.run(graph_auth_provider._fetch_access_token())
    time_to_test = datetime.now() + timedelta(hours=6)
    assert graph_auth_provider._is_token_expire(time_to_test)
