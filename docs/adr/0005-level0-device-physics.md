<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Liner Core — ADR 0005
-->

# ADR 0005 — Level-0 device physics: shell mechanics and ideal compression

Status: accepted (2026-09-04). Adds the third implemented capability,
`level0_device_physics`, at `computational_prototype`, and pins the shared
kernel library for the first time in this repository.

## Context

The repository carried a configuration model and diagnostic semantics and
no physics. Its three filed sources are all public laboratory reports, and
one of them — R. W. Moses, R. A. Krakowski and R. L. Miller, LA-7686-MS
(Los Alamos, 1979) — carries a complete design-point table for a fast
liner reactor, with two columns.

## Decision

1. **Two closed forms and no more.**

   *Shell mechanics.* The liner is an annular cylinder. Its mass is the
   exact annulus `rho pi ((r + d)^2 - r^2) l` rather than the thin-shell
   approximation, because the two differ by `d / (2 r + d)` and that is
   0.74 % at the filed design point — comparable to the tolerance the
   energy anchor is asserted at. From the mass follow the kinetic energy,
   the drive pressure of the target's initial field, and the
   characteristic time `r_0 / v`.

   *Ideal compression.* Flux conservation gives
   `B(r) = B_0 (r_0 / r)^2` and adiabatic compression gives
   `T(r) = T_0 (r_0 / r)^(2 (gamma - 1))`.

2. **The compressions are upper bounds and the record says so.** A real
   liner has finite conductivity and loses flux; a real compression
   radiates and conducts. Both statements are in the record's own
   `non_claims`, not only in prose, so a consumer reading the JSON cannot
   miss them.

3. **The characteristic time is named as a scale.** `r_0 / v` is the time
   the shell needs to cross its own initial radius at the declared
   velocity. A real implosion accelerates, so this is the order of the
   duration, not a prediction of it.

4. **The non-integer power goes through the shared library.** The
   adiabatic exponent `2 (gamma - 1)` is `4/3` for a monatomic gas, and a
   transcendental evaluated by the platform would differ between
   back-ends. This is why the repository pins the kernel library here; it
   consumes exactly one kernel, `numerics_transcendental`.

5. **The convergence contract is applied by every relation that needs
   it.** A ratio of one compresses nothing and a ratio below one expands.
   All three compression functions refuse it, and the test checks all
   three, because a contract enforced by only some of the functions that
   need it is not enforced.

## Anchoring, and one value that had to be recovered

Table II-I prints, for the low-yield and high-yield design points: the
initial liner inner radius (0.2 m, 0.3 m), the initial liner thickness
(3.0 mm, 4.5 mm), the initial azimuthal field (13.0 T for both) and the
initial liner energy (0.336 GJ, 0.756 GJ). The report's text adds that the
liner is copper, that it is 0.2 m long, and that the implosion lasts 20 to
40 microseconds.

**The implosion velocity is not printed in a form the extraction
preserves.** Superscripts are lost, so it reads as "10 m/s" in almost
every occurrence; a single surviving sentence gives the range
`10^3-10^4 m/s` but not the design point.

It was settled by arithmetic against the table rather than by choosing.
At `1e4 m/s` the kinetic energy of an annular copper shell of the printed
radius, thickness and length reproduces **both** printed energies to
0.83 %. At `1e3 m/s` the same computation is a hundredfold too small. Two
independent printed rows agreeing to under one per cent is the evidence,
and the test suite asserts both halves of it: that the chosen value fits,
**and** that the alternative misses. A fit that was never contrasted with
a miss is not evidence.

A third printed statement checks the recovery from a different direction:
the characteristic time `r_0 / v` is 20 and 30 microseconds for the two
design points, inside the 20-to-40-microsecond window the abstract prints.

The energy anchor is asserted at one per cent and not more tightly, for a
stated reason: the report rounds its energies to three figures and never
prints the copper density it used. An exact equality would be a claim the
source does not support.

Everything else — the liner kind, the convergence ratio, the adiabatic
index, and the target beyond its initial field — is declared and is said
to be declared, in the fixture docstring and in `VALIDATION.md`.

## Consequences

The family has a physics capability bounded to two closed forms whose
source any reader can open, with a design point that checks itself three
ways. The two ideal limits are recorded as upper bounds rather than
presented as results.

Nothing here claims yield, gain, confinement or performance, and no value
describes a real machine. Reproducing a printed number is an anchor on the
arithmetic and nothing further.
