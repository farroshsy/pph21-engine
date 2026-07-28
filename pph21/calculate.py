"""Annual PPh 21 calculation that shows its working.

Every result carries the regulation that produced it and a line-by-line trace.
A tax figure without the rule that generated it is unauditable, and an
unauditable tax figure is the only kind that causes an argument.

NOT TAX ADVICE. This is a calculator that cites its sources. See README.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from pph21.rules import RuleSet, rules_for


@dataclass
class Step:
    label: str
    amount: int
    basis: str  # which rule or arithmetic produced this


@dataclass
class Result:
    tax_annual: int
    tax_monthly: int
    regulation: str
    rules_verified: bool
    steps: list[Step] = field(default_factory=list)

    def trace(self) -> str:
        w = max(len(s.label) for s in self.steps)
        lines = [f"  {s.label:<{w}}  {s.amount:>15,}   {s.basis}" for s in self.steps]
        head = [f"Regulation: {self.regulation}"]
        if not self.rules_verified:
            head.append("⚠ RATES UNVERIFIED — see VERIFICATION.md before relying on this")
        return "\n".join(head + [""] + lines)


def annual_pph21(
    gross_annual: int,
    status: str,
    on: date,
    other_deductions_annual: int = 0,
) -> Result:
    """Compute annual PPh 21 for an employee, using the rules in force on `on`.

    `on` is the period being taxed, NOT today. That distinction is the entire
    reason this module exists.
    """
    rs: RuleSet = rules_for(on)
    if status not in rs.ptkp:
        raise KeyError(
            f"unknown PTKP status {status!r} under {rs.regulation}; "
            f"known: {sorted(rs.ptkp)}"
        )

    steps = [Step("Gross annual", gross_annual, "input")]

    occupational = min(
        int(gross_annual * rs.occupational_cost_rate), rs.occupational_cost_cap_year
    )
    capped = occupational == rs.occupational_cost_cap_year
    steps.append(
        Step(
            "Biaya jabatan",
            -occupational,
            f"{rs.occupational_cost_rate:.0%}"
            + (f", capped at {rs.occupational_cost_cap_year:,}" if capped else ""),
        )
    )

    if other_deductions_annual:
        steps.append(Step("Other deductions", -other_deductions_annual, "input"))

    net = gross_annual - occupational - other_deductions_annual
    steps.append(Step("Net income", net, "gross less deductions"))

    ptkp = rs.ptkp[status]
    steps.append(Step(f"PTKP ({status})", -ptkp, rs.regulation))

    # PKP is rounded DOWN to the nearest thousand rupiah before brackets apply.
    pkp_raw = max(0, net - ptkp)
    pkp = (pkp_raw // 1000) * 1000
    steps.append(Step("PKP (rounded down)", pkp, "to nearest 1,000"))

    tax = 0
    lower = 0
    for b in rs.brackets:
        if pkp <= lower:
            break
        ceiling = b.upper if b.upper is not None else pkp
        taxable = min(pkp, ceiling) - lower
        if taxable > 0:
            portion = int(taxable * b.rate)
            tax += portion
            band = f"{lower:,}–{b.upper:,}" if b.upper else f"above {lower:,}"
            steps.append(Step(f"  {b.rate:.0%} on {taxable:,}", portion, band))
        lower = ceiling
        if b.upper is None:
            break

    steps.append(Step("PPh 21 annual", tax, "sum of bracket portions"))
    monthly = tax // 12
    steps.append(Step("PPh 21 monthly", monthly, "annual / 12, floored"))

    return Result(
        tax_annual=tax,
        tax_monthly=monthly,
        regulation=rs.regulation,
        rules_verified=rs.verified,
        steps=steps,
    )
