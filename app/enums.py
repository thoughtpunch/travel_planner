from enum import StrEnum


class Structure(StrEnum):
    A_THREE_ONEWAYS = "A"
    B_NESTED_ENVELOPE = "B"


class Source(StrEnum):
    FAST_FLIGHTS = "fast-flights"
    FLI = "fli"
    SERPAPI = "serpapi"


class VerificationStatus(StrEnum):
    LEAD = "LEAD"
    VALIDATED = "VALIDATED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    STALE = "STALE"
    SKIPPED_QUOTA = "SKIPPED_QUOTA"
    FAILED = "FAILED"


class RunStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class Flag(StrEnum):
    BLACKOUT = "BLACKOUT"
    LONG_GAP = "LONG_GAP"
    INCOMPLETE = "INCOMPLETE"
