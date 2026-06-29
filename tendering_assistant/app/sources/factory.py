from app.core.config import Settings, get_settings
from app.sources.base import TenderSource
from app.sources.portals import (
    CpppEprocureSource,
    DefenceSource,
    GemSource,
    PsuPortalSource,
    RailwaysSource,
    StateProcurementSource,
)

_SOURCE_CLASSES = [
    GemSource,
    CpppEprocureSource,
    StateProcurementSource,
    PsuPortalSource,
    RailwaysSource,
    DefenceSource,
]


def get_enabled_sources() -> list[TenderSource]:
    """Instantiate every source whose connection settings are configured.

    Sources without a configured base URL are skipped (not errored) so that
    a partial rollout -- e.g. only GeM and Railways wired up so far -- works
    without the others blocking a scan.
    """
    settings: Settings = get_settings()
    sources = [cls(settings) for cls in _SOURCE_CLASSES]
    return [s for s in sources if getattr(settings, s._settings_attr, None)]


def get_all_sources() -> list[TenderSource]:
    settings: Settings = get_settings()
    return [cls(settings) for cls in _SOURCE_CLASSES]
