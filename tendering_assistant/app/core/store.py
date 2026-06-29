"""In-memory persistence for this initial slice.

A real deployment would swap this for a database (the models are already
plain pydantic objects so that swap doesn't touch business logic). Keeping
state in-process keeps the workflow engine and approval gates easy to read
and test without standing up infrastructure.
"""
from typing import Generic, TypeVar

T = TypeVar("T")


class InMemoryStore(Generic[T]):
    def __init__(self) -> None:
        self._items: dict[str, T] = {}

    def put(self, key: str, value: T) -> T:
        self._items[key] = value
        return value

    def get(self, key: str) -> T | None:
        return self._items.get(key)

    def require(self, key: str) -> T:
        item = self.get(key)
        if item is None:
            raise KeyError(key)
        return item

    def list(self) -> list[T]:
        return list(self._items.values())


opportunities: InMemoryStore = InMemoryStore()
documents: InMemoryStore = InMemoryStore()
analyses: InMemoryStore = InMemoryStore()
bid_drafts: InMemoryStore = InMemoryStore()
clarifications: InMemoryStore = InMemoryStore()
approvals: InMemoryStore = InMemoryStore()
