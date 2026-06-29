"""Connector implementations for each approved tendering platform.

Each government/PSU portal has its own auth model, API (or lack of one),
and listing format, so the actual HTTP/scraping logic belongs in a
follow-up change made together with whoever holds credentials/API access
for that portal. Wiring fabricated endpoint URLs or response shapes here
would be worse than not having them: it would silently return nothing (or
break) and look like a working integration.

What this module provides now is the connector *shape* -- one class per
portal, registered with the factory, each reading its own connection
settings and raising a clear SourceConfigurationError until configured. To
go live for a given portal: fill in `fetch_new_tenders` with that portal's
documented search/listing API call, mapping its response fields onto
DiscoveredTender.
"""

import httpx

from app.core.config import Settings
from app.models.domain import DiscoveredTender, TenderSourceName
from app.sources.base import TenderSource
from app.sources.errors import SourceConfigurationError


class _ConfigurableHttpSource(TenderSource):
    """Shared scaffolding for portals reachable over a configured HTTP API.

    Subclasses set `name` and `_settings_attr` (the Settings field holding
    this portal's base URL) and implement `_parse_listings` once the real
    response shape is known.
    """

    _settings_attr: str = ""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._base_url: str | None = getattr(settings, self._settings_attr, None)

    async def fetch_new_tenders(self) -> list[DiscoveredTender]:
        if not self._base_url:
            raise SourceConfigurationError(
                f"{self.name.value} source is not configured "
                f"(set {self._settings_attr.upper()} to enable it)."
            )
        async with httpx.AsyncClient(base_url=self._base_url, timeout=30) as client:
            response = await client.get(self._listing_path())
            response.raise_for_status()
            return self._parse_listings(response.json())

    def _listing_path(self) -> str:
        raise NotImplementedError

    def _parse_listings(self, payload: object) -> list[DiscoveredTender]:
        raise NotImplementedError


class GemSource(_ConfigurableHttpSource):
    name = TenderSourceName.GEM
    _settings_attr = "gem_api_base_url"

    def _listing_path(self) -> str:
        raise NotImplementedError("Wire up GeM's published search/listing API here.")

    def _parse_listings(self, payload: object) -> list[DiscoveredTender]:
        raise NotImplementedError("Map GeM's response fields onto DiscoveredTender here.")


class CpppEprocureSource(_ConfigurableHttpSource):
    name = TenderSourceName.CPPP_EPROCURE
    _settings_attr = "cppp_eprocure_api_base_url"

    def _listing_path(self) -> str:
        raise NotImplementedError("Wire up CPPP/eProcure's listing API here.")

    def _parse_listings(self, payload: object) -> list[DiscoveredTender]:
        raise NotImplementedError("Map CPPP/eProcure's response fields onto DiscoveredTender here.")


class StateProcurementSource(_ConfigurableHttpSource):
    name = TenderSourceName.STATE_PROCUREMENT
    _settings_attr = "state_procurement_api_base_url"

    def _listing_path(self) -> str:
        raise NotImplementedError("Wire up the target state portal's listing API here.")

    def _parse_listings(self, payload: object) -> list[DiscoveredTender]:
        raise NotImplementedError("Map the state portal's response fields onto DiscoveredTender here.")


class PsuPortalSource(_ConfigurableHttpSource):
    name = TenderSourceName.PSU_PORTAL
    _settings_attr = "psu_portal_api_base_url"

    def _listing_path(self) -> str:
        raise NotImplementedError("Wire up the target PSU portal's listing API here.")

    def _parse_listings(self, payload: object) -> list[DiscoveredTender]:
        raise NotImplementedError("Map the PSU portal's response fields onto DiscoveredTender here.")


class RailwaysSource(_ConfigurableHttpSource):
    name = TenderSourceName.RAILWAYS
    _settings_attr = "railways_api_base_url"

    def _listing_path(self) -> str:
        raise NotImplementedError("Wire up IREPS/Railways' listing API here.")

    def _parse_listings(self, payload: object) -> list[DiscoveredTender]:
        raise NotImplementedError("Map Railways' response fields onto DiscoveredTender here.")


class DefenceSource(_ConfigurableHttpSource):
    name = TenderSourceName.DEFENCE
    _settings_attr = "defence_api_base_url"

    def _listing_path(self) -> str:
        raise NotImplementedError("Wire up the Defence procurement portal's listing API here.")

    def _parse_listings(self, payload: object) -> list[DiscoveredTender]:
        raise NotImplementedError("Map the Defence portal's response fields onto DiscoveredTender here.")
