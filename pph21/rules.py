"""Tax rules keyed by the date they took effect.

The point of this module: a 2024 payroll recomputed in 2026 must use the rules
that were in force in 2024, not today's. Most payroll code hardcodes current
rates and quietly produces the wrong answer the moment anyone recalculates a
prior period — which is exactly when someone is checking your work.

Every rule set carries the regulation it came from, so a calculation can say
which law produced it rather than asserting a number.

⚠️ RATES REQUIRE VERIFICATION. The structure here is sound; the figures are
transcribed and MUST be checked against the source regulation before this is
used for anything real. Fields marked `verified=False` have NOT been confirmed
against the primary text — see `VERIFICATION.md`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Bracket:
    upper: int | None      # annual PKP ceiling in rupiah; None = no ceiling
    rate: float


@dataclass(frozen=True)
class RuleSet:
    effective_from: date
    effective_to: date | None
    regulation: str
    brackets: tuple[Bracket, ...]
    ptkp: dict[str, int]           # non-taxable income by status
    occupational_cost_rate: float  # biaya jabatan
    occupational_cost_cap_year: int
    verified: bool = False
    notes: str = ""


# UU HPP No. 7/2021 — progressive annual brackets, in force from 2022.
# Widely published and stable; still marked unverified until checked against
# the regulation text itself rather than a secondary source.
UU_HPP_2021 = RuleSet(
    effective_from=date(2022, 1, 1),
    effective_to=None,
    regulation="UU No. 7 Tahun 2021 (HPP), Pasal 17",
    brackets=(
        Bracket(60_000_000, 0.05),
        Bracket(250_000_000, 0.15),
        Bracket(500_000_000, 0.25),
        Bracket(5_000_000_000, 0.30),
        Bracket(None, 0.35),
    ),
    ptkp={
        "TK/0": 54_000_000,
        "TK/1": 58_500_000,
        "TK/2": 63_000_000,
        "TK/3": 67_500_000,
        "K/0": 58_500_000,
        "K/1": 63_000_000,
        "K/2": 67_500_000,
        "K/3": 72_000_000,
    },
    occupational_cost_rate=0.05,
    occupational_cost_cap_year=6_000_000,
    verified=False,
    notes="PTKP values predate HPP and derive from PMK 101/2016. Confirm both.",
)


RULE_SETS: tuple[RuleSet, ...] = (UU_HPP_2021,)


class NoRuleInForce(LookupError):
    """Raised when no rule set covers the requested date.

    Deliberately an error rather than a fallback to the newest rules: silently
    applying today's law to a 2019 payroll is the failure this module exists to
    prevent.
    """


def rules_for(on: date) -> RuleSet:
    for rs in RULE_SETS:
        if rs.effective_from <= on and (rs.effective_to is None or on <= rs.effective_to):
            return rs
    raise NoRuleInForce(
        f"no rule set covers {on.isoformat()} — add one rather than "
        f"defaulting to the current rules"
    )
