"""Memory-scope routing distinctions (not a claim that life reduces to six enums)."""

from __future__ import annotations

from enum import Enum


class MemoryScope(str, Enum):
    SELF = "SELF"  # AIYE
    ORGAN = "ORGAN"  # PROTEUS
    PROJECT = "PROJECT"
    ENTITY = "ENTITY"  # WORLD
    EPISODE = "EPISODE"  # EVENT
    SECRET_REFERENCE = "SECRET_REFERENCE"

    @classmethod
    def parse(cls, value: str) -> "MemoryScope":
        raw = value.strip().upper().replace("-", "_").replace(" ", "_")
        aliases = {
            "AIYE": cls.SELF,
            "SELF_AIYE": cls.SELF,
            "PROTEUS": cls.ORGAN,
            "WORLD": cls.ENTITY,
            "EVENT": cls.EPISODE,
            "EPISODIC": cls.EPISODE,
            "SECRET": cls.SECRET_REFERENCE,
            "SECRET_REF": cls.SECRET_REFERENCE,
        }
        if raw in aliases:
            return aliases[raw]
        return cls(raw)
