import aiohttp
from dataclasses import dataclass
from aiopyo365.ressources.sites import Site
from aiopyo365.factories.abstract import AbstractFactory


@dataclass
class SitesFactory(AbstractFactory):
    """Factory that provide a Sites object to interact with a site resource.
    A site ressource provides metadata and relationships for a SharePoint site.
    """

    def create(self, session: aiohttp.ClientSession) -> Site:
        """Create the Site object to o interact with a site resource.

        Args:
            session (aiohttp.ClientSession): ClientSession object from aiohttp

        Returns:
            Site: object to a interact with a site resource
        """
        return Site(base_url=self._base_url, session=session)
