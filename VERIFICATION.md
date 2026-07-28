# Verification status

Every rate in `pph21/rules.py` is currently marked `verified=False`. That flag
is not decoration — the calculator prints a warning on every result until it is
cleared, and it should not be cleared casually.

## What "verified" requires

Not "I found this on a payroll blog". A rate is verified when it has been read
in the **primary regulation text**, and the reader has recorded:

- the regulation number and article
- the effective date
- the date it was checked
- a link to the official source (peraturan.go.id, JDIH Kemenkeu, or equivalent)

## Outstanding

| item | source claimed | status |
|---|---|---|
| Progressive brackets (5/15/25/30/35%) | UU No. 7/2021 (HPP) Pasal 17 | **unverified** |
| PTKP values | PMK 101/2016 | **unverified** — predates HPP, confirm still current |
| Biaya jabatan 5%, cap 6,000,000/yr | — | **unverified**, source not yet identified |
| PKP rounding to nearest 1,000 down | — | **unverified**, source not yet identified |
| TER (tarif efektif rata-rata) | PMK 168/2023 | **not implemented** |

## TER is missing, deliberately

PMK 168/2023 introduced the effective average rate method for monthly
withholding from January 2024. It is a substantial change and it is **not
implemented here**.

It is not implemented because implementing it from memory would mean inventing
category tables, and a fabricated tax table that looks authoritative is worse
than an absent one. It goes in when someone reads the actual schedule.

Until then this engine computes the **annual** calculation only, and the README
says so.

## Why this file exists

The engine cites a regulation on every result. That citation is a promise, and
a promise you have not checked is just a more convincing way to be wrong.
