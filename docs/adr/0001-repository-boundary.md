<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Liner Core — ADR 0001: repository boundary
-->

# ADR 0001 — Repository boundary and ownership

**Status:** accepted (2026-08-30)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The SCPN reactor portfolio assigns every built-in configuration of the SCPN
Phase Orchestrator reactor registry (version `1.0.0`, 32 configurations) to
exactly one device-family repository. Material-liner MIF is the slowest of
the four magneto-inertial liner classes and the most plant-oriented; a
boundary decision was needed against the other liner owners and the target
owners.

## Decision

1. `SCPN-MIF-LINER-CORE` owns exactly one registry configuration:
   `mechanical_or_liquid_liner_mif` (material-liner compression).
2. The repository owns device-level truth only: material-liner
   configuration policy (solid pusher and rotating liquid classes, drive
   synchronisation contracts, liner–plasma interface budgets, repetition
   and heat-extraction facets), repetition-oriented lifecycle semantics
   with synchronisation and liner-integrity hazard records,
   dual-timescale diagnostic and clock declarations, actuator-response
   model boundaries, the safety-envelope declaration, and the
   device-owned CONTROL adapter specification.
3. Target-plasma physics belongs to the target owner (`SCPN-FRC-CORE` for
   a compact-toroid target); the pulsed FRC merge-compression workflow
   stays with `SCPN-MIF-CORE`; the faster liner classes stay with their
   owners.
4. Solver mathematics remains in `SCPN-FUSION-CORE` until an exact surface
   passes the family migration gate. No solver code is copied here.
5. Typed semantics remain in `SCPN-PHASE-ORCHESTRATOR` (review-only).
   Admission and `ControlAction` formation remain exclusively in
   `SCPN-CONTROL`. Machine protection remains independent with the final
   veto. Presentation remains in `SCPN-STUDIO`; this project is
   `not_federated`.
6. The repository starts, and remains until evidenced otherwise, at
   `architecture_only` with empty capability and claim inventories.

## Alternatives considered

- **One repository for all liner-MIF classes**: rejected — millisecond
  mechanical/liquid compression, nanosecond pulsed-power solid liners,
  and standoff plasma-jet liners differ in liner physics, driver,
  timescale, lifecycle, and hazards (surfaces 1–4); only the
  flux-compression idea is shared.
- **Treating the liquid liner as a plant subsystem of another owner**:
  rejected — in this family the liner is the confinement driver itself,
  not a downstream blanket; the plant orientation (recovery, heat
  extraction) is part of the device lifecycle.
- **Absorbing solver code at scaffold time**: rejected — violates the
  migration gate.

## Consequences

- Downstream consumers get one stable identity for the material-liner MIF
  configuration and a manifest to bind against.
- The validator fails on any capability or claim entry while maturity is
  `architecture_only`.
- Boundary changes require a portfolio-level map change first; a future
  ADR records any such change here.
