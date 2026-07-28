# pph21-engine

Indonesian PPh 21 calculation where **the rules are keyed by effective date**
and every result cites the regulation that produced it.

> **Not tax advice.** This is a calculator that shows its working and names its
> sources. It is not a substitute for a consultant, and the rates are currently
> unverified — see [VERIFICATION.md](VERIFICATION.md).

## The problem it solves

Most payroll code hardcodes current rates. Recompute a 2022 payslip in 2026 and
it silently applies 2026's law — producing a confident, wrong number at exactly
the moment somebody is auditing you.

Here, rules carry `effective_from` / `effective_to`, and asking for a date no
rule covers raises `NoRuleInForce` rather than falling back to the newest set.
Refusing to answer is the correct behaviour.

```python
rules_for(date(2019, 6, 1))
# NoRuleInForce: no rule set covers 2019-06-01 — add one rather than
# defaulting to the current rules
```

## Every result shows its working

```
Regulation: UU No. 7 Tahun 2021 (HPP), Pasal 17
⚠ RATES UNVERIFIED — see VERIFICATION.md before relying on this

  Gross annual             200,000,000   input
  Biaya jabatan             -6,000,000   5%, capped at 6,000,000
  Net income               194,000,000   gross less deductions
  PTKP (K/1)               -63,000,000   UU No. 7 Tahun 2021 (HPP), Pasal 17
  PKP (rounded down)       131,000,000   to nearest 1,000
    5% on 60,000,000         3,000,000   0–60,000,000
    15% on 71,000,000       10,650,000   60,000,000–250,000,000
  PPh 21 annual             13,650,000   sum of bracket portions
  PPh 21 monthly             1,137,500   annual / 12, floored
```

A tax figure without the rule that generated it is unauditable.

## What is NOT here

- **TER (PMK 168/2023).** The monthly effective-rate method is not implemented.
  Implementing it from memory would mean inventing category tables, and a
  fabricated tax table that looks authoritative is worse than an absent one.
- **Verified rates.** Everything is `verified=False` until read in the primary
  regulation text.
- Non-employee PPh 21, severance, expatriate rules, BPJS interaction.

## Run

```bash
python -m tests.test_pph21
```

Eleven tests, covering temporal correctness and bracket arithmetic. They do
**not** verify that the rates themselves are correct — that needs the
regulation, not a test.
