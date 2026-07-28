#!/usr/bin/env python3
"""Tests for temporal correctness and arithmetic. NOT a check that the RATES are
right — that requires the regulation text, and VERIFICATION.md tracks it."""
from datetime import date
from pph21.rules import rules_for, NoRuleInForce
from pph21.calculate import annual_pph21

failures = []

def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        failures.append(f"{name}: {detail}")

def main() -> int:
    print("pph21-engine self-tests\n")

    # Temporal correctness — the whole point.
    try:
        rules_for(date(2019, 6, 1))
        check("pre-effective date refuses to compute", False, "it returned rules")
    except NoRuleInForce:
        check("pre-effective date refuses to compute", True)

    rs = rules_for(date(2024, 3, 1))
    check("2024 payroll resolves a rule set", rs.regulation.startswith("UU No. 7"))
    check("rules are flagged unverified", rs.verified is False)

    # Below PTKP pays nothing.
    r = annual_pph21(50_000_000, "TK/0", date(2024, 1, 1))
    check("income below PTKP pays zero", r.tax_annual == 0, str(r.tax_annual))

    # First bracket only.
    r = annual_pph21(120_000_000, "TK/0", date(2024, 1, 1))
    # gross 120M − biaya jabatan 6M (capped) − PTKP 54M = 60M PKP → 5% = 3,000,000
    check("first bracket arithmetic", r.tax_annual == 3_000_000, str(r.tax_annual))

    # Biaya jabatan cap binds above 120M gross.
    cap_step = [s for s in r.steps if s.label == "Biaya jabatan"][0]
    check("biaya jabatan capped at 6,000,000", cap_step.amount == -6_000_000)

    # Crossing into the second bracket.
    r2 = annual_pph21(200_000_000, "TK/0", date(2024, 1, 1))
    # 200M − 6M − 54M = 140M PKP → 5% on 60M + 15% on 80M = 3M + 12M = 15,000,000
    check("second bracket arithmetic", r2.tax_annual == 15_000_000, str(r2.tax_annual))

    # Marital status changes the answer.
    single = annual_pph21(200_000_000, "TK/0", date(2024, 1, 1)).tax_annual
    married = annual_pph21(200_000_000, "K/3", date(2024, 1, 1)).tax_annual
    check("higher PTKP lowers tax", married < single, f"{married} vs {single}")

    # Every result cites its regulation.
    check("result carries the regulation", "UU No. 7" in r2.regulation)
    check("trace warns when unverified", "UNVERIFIED" in r2.trace())

    # Unknown status is an error, not a default.
    try:
        annual_pph21(100_000_000, "K/9", date(2024, 1, 1))
        check("unknown PTKP status rejected", False, "it computed")
    except KeyError:
        check("unknown PTKP status rejected", True)

    print()
    print(annual_pph21(200_000_000, "K/1", date(2024, 1, 1)).trace())
    print()
    if failures:
        print(f"{len(failures)} failure(s)")
        for f in failures: print("  ", f)
        return 1
    print("all passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
