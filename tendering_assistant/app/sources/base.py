from abc import ABC, abstractmethod

from app.models.domain import DiscoveredTender, TenderSourceName


class TenderSource(ABC):
    """A connector that polls one external tendering platform.

    Each portal (GeM, CPPP/eProcure, state procurement, PSU, Railways,
    Defence, ...) gets its own implementation behind this interface, the
    same pattern used for LLMProvider: callers depend only on this
    abstraction, never on a portal-specific client.

    Real implementations call the portal's published search/listing API (or
    an authorized scraper where no API exists) filtered to DG Set / BOP -
    relevant categories and return the matches as DiscoveredTender objects.
    Network access, auth, and rate-limit handling are entirely the
    implementation's concern.
    """

    name: TenderSourceName

    @abstractmethod
    async def fetch_new_tenders(self) -> list[DiscoveredTender]:
        """Return tenders found since the last poll, deduped by external_id."""
