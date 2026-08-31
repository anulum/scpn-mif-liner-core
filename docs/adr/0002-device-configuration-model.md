<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Liner Core — ADR 0002: device configuration model
-->

# ADR 0002 — Device configuration model and evidence-maturity semantics

**Status:** accepted (2026-08-31)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The repository was established architecture-only (ADR 0001). The first
capability lane is the device configuration model for the single
registry configuration this repository owns
(`mechanical_or_liquid_liner_mif`). The claim boundary and
repository-level `evidence_maturity` semantics follow the family pilot.

## Decision

1. The package `scpn_mif_liner_core` implements the device
   configuration model as frozen, strictly typed value objects: the
   material liner (solid-pusher or rotating-liquid class, inner radius,
   implosion velocity) and the magnetised target (initial embedded
   field).
2. Claim boundary — identical to the family pilot: internal-consistency
   validation, cited textbook estimates with documented bounds,
   canonical serialisation with SHA-256 digest, and the data-only SPO
   registry pin. No claim about any real machine; every exercised
   parameter set is a synthetic test fixture.
3. Hard invariants: the liner class is ``solid`` or ``liquid`` (the two
   material-liner branches of the configuration), and the target's
   initial embedded field is strictly positive — a premagnetised target
   is the defining property of magneto-inertial fusion.
4. Derived quantity from standard mechanics: the liner specific kinetic
   energy ``e = v^2 / 2``. Advisory finding, reported by
   `consistency_report()` and never clamped: an implosion velocity
   above ``~1 km/s`` — material-liner (LINUS-class) studies occupy the
   slow branch of magneto-inertial fusion, of order 10^2 m/s,
   contrasted with the 10^3-10^4 m/s fast metal-shell branch
   (R. W. Moses, R. A. Krakowski, R. L. Miller, Los Alamos report
   LA-7686-MS, 1979, Introduction).
5. Repository-level `evidence_maturity` = the highest state claimed by
   any capability entry; per-capability states are the authoritative
   claim surface.
6. Everything else is unchanged: review-only/non-actionable SPO
   profile, no adapter implementation, empty solver seams,
   `not_federated` Studio state, independent machine-protection veto,
   all non-claims.

## Consequences

- The Studio descriptor's `capabilities` array carries its first item
  (schema 1.1.0 data change only).
- The reactor-domain validator gains the populated-capabilities branch
  with the ceiling rule.
- Later lanes (synchronisation/liner/burn diagnostic semantics with
  dual clocks, safety envelope) build on these types; maturity advances
  per capability only with the evidence the family standard requires.
