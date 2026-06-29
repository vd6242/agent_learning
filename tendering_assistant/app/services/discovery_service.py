from app.core.store import discovered_tenders
from app.models.domain import DiscoveredTender
from app.sources.base import TenderSource


def _existing_keys() -> set[tuple[str, str]]:
    return {(t.source.value, t.external_id) for t in discovered_tenders.list()}


async def scan_sources(sources: list[TenderSource]) -> list[DiscoveredTender]:
    """Poll every given source and persist tenders not already seen.

    Returns only the newly-discovered tenders (not the full backlog) so
    callers/API responses stay small on repeated scans.
    """
    seen = _existing_keys()
    newly_found: list[DiscoveredTender] = []

    for source in sources:
        for tender in await source.fetch_new_tenders():
            key = (tender.source.value, tender.external_id)
            if key in seen:
                continue
            seen.add(key)
            discovered_tenders.put(tender.id, tender)
            newly_found.append(tender)

    return newly_found
