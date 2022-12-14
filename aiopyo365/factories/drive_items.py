import aiohttp
from dataclasses import dataclass
from aiopyo365.ressources.files import DriveItems
from aiopyo365.factories.abstract import AbstractFactory


@dataclass
class DriveItemsSitesFactory(AbstractFactory):
    """Factory that provide a DriveItem object
    able to interact with site drive.
    """

    site_id: str

    def create(self, session: aiohttp.ClientSession) -> DriveItems:
        url = f"{self._base_url}/sites/{self.site_id}"
        return DriveItems(
            base_url=url,
            session=session,
        )


@dataclass
class DriveItemsGroupsFactory(AbstractFactory):
    """Factory that provide a DriveItem object
    able to interact with group drive.
    """

    group_id: str

    def create(self, session: aiohttp.ClientSession) -> DriveItems:
        url = f"{self._base_url}/groups/{self.group_id}"
        return DriveItems(base_url=url, session=session)


@dataclass
class DriveItemsDrivesFactory(AbstractFactory):
    """Factory that provide a DriveItem object
    able to interact with drives drive.
    """

    drive_id: str

    def create(self, session: aiohttp.ClientSession) -> DriveItems:
        url = f"{self._base_url}/drives/{self.drive_id}"
        return DriveItems(base_url=url, session=session)


@dataclass
class DriveItemsMeFactory(AbstractFactory):
    """Factory that provide a DriveItem object
    able to interact with me drive.
    """

    def create(self, session: aiohttp.ClientSession) -> DriveItems:
        url = f"{self._base_url}/me"
        return DriveItems(base_url=url, session=session)


@dataclass
class DriveItemsUsersFactory(AbstractFactory):
    """Factory that provide a DriveItem object
    able to interact with users drive.
        _type_: _description_
    """

    user_id: str

    def create(self, session: aiohttp.ClientSession) -> DriveItems:
        url = f"{self._base_url}/users/{self.user_id}"
        return DriveItems(base_url=url, session=session)
