<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Liner Core — Benchmarks and computation contract
-->

# Benchmarks and computation contract

## Computation contract

The level-0 physics of this package is a set of closed forms evaluated in
IEEE-754 binary64 on the Python floor (SI units; the configuration carries
the implosion velocity in kilometres per second):

| Module | Kernels | Operations |
|---|---|---|
| `physics/implosion.py` | annular shell mass `rho pi ((r + d)^2 - r^2) l`, kinetic energy at the declared velocity, drive pressure `B^2 / 2 mu0`, characteristic time `r_0 / v` | `* /` |
| `physics/compression.py` | flux-compressed field `B_0 (r_0 / r)^2`, compressed density ratio `(r_0 / r)^2`, adiabatic temperature ratio `(r_0 / r)^(2 (gamma - 1))` | `* /`, **one real power** |
| `physics/level0.py` | the composed record with canonical bytes and SHA-256 digest | composition, JSON serialisation |

Every input outside its domain is refused with the package error, never
clamped. The real power is not the platform `pow`: it is evaluated by the
shared library's deterministic `power` kernel (`numerics_transcendental`,
pinned in `reactor-domain.json`), so a native backend that must agree bit
for bit would call the same kernel. The constants and their editions are
documented in `physics/implosion.py` and bound by tests.

**Backend status.** Python floor only. There is no native crate. Audit
plan Q01 asks for a native path on required numeric paths and allows a
scoped, owner-approved exception for trivial non-hot arithmetic; that
decision is the owner's and is recorded as open in the backlog. The
benchmark marks the native backend as unavailable instead of omitting it.

## Level-0 physics — local workstation (non-isolated)

Artefact: `benchmarks/results/level0_physics.local.json` (schema
`scpn-mif-liner-core.level0-physics-benchmark.v1`, generated
2026-10-31T05:30:29.463176+00:00, at commit `a31002aad2a5` with the working
tree of the landing commit). Host: 11th Gen Intel(R) Core(TM) i5-11600K @
3.90GHz, Linux-7.0.0-34-generic-x86_64-with-glibc2.39, Python 3.12.3; load
average at start 2.64; cores not isolated, so treat the numbers as a smoke
timing, not a performance measurement. Parameters: 20000 closed-form points
and 2000 records, 3 warm-up passes, 20 timed passes.

### `closed_forms` (shell mass, drive pressure, compressed field, density ratio and temperature ratio per point)

| Backend | P50 µs/point | P95 µs/point | P99 µs/point | mean µs/point | throughput points/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 2.083 | 2.245 | 2.385 | 2.097 | 479980 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

### `level0_record` (composed record with canonical bytes per point)

| Backend | P50 µs/record | P95 µs/record | P99 µs/record | mean µs/record | throughput records/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 28.603 | 40.281 | 41.140 | 30.202 | 34961 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

## Regenerate

```bash
.venv/bin/python benchmarks/level0_physics.py --label local
```

The script writes `benchmarks/results/level0_physics.<label>.json` with the
provenance above. A number from a fixed CI runner or isolated cores would
replace the smoke timing here; none is claimed yet.
