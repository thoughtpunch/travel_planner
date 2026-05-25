"""SerpAPI quota tracker. In-process counter, persisted on Run records.

The ceiling is a HARD upper bound: any call that would breach it raises
QuotaExceeded so the caller can mark the affected query SKIPPED_QUOTA rather
than producing a surprise bill.
"""

from dataclasses import dataclass

from .base import QuotaExceeded


@dataclass
class QuotaTracker:
    ceiling: int
    used_this_run: int = 0
    used_before_run: int = 0

    @property
    def total_used(self) -> int:
        return self.used_before_run + self.used_this_run

    @property
    def remaining(self) -> int:
        return max(0, self.ceiling - self.total_used)

    def reserve(self, n: int = 1) -> None:
        if self.total_used + n > self.ceiling:
            raise QuotaExceeded(
                f"SerpAPI quota would be exceeded: {self.total_used}+{n} > {self.ceiling}"
            )
        self.used_this_run += n

    def estimate_run(self, planned_calls: int) -> dict:
        return {
            "planned_calls": planned_calls,
            "remaining_before": self.remaining,
            "remaining_after_if_run": max(0, self.remaining - planned_calls),
            "would_exceed": planned_calls > self.remaining,
        }
