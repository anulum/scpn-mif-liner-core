<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Liner Core — Architecture
-->

# Architecture

## Purpose and evidence state

`SCPN-MIF-LINER-CORE` is the device-family owner for mechanical- and
liquid-liner magnetised-target fusion systems in the SCPN Reactor Systems
Research Group portfolio. The repository is `architecture_only`: every
section below describes boundaries and contracts, not implemented
capability. The capability and claim inventories are empty; both derived
artefacts are generated and drift-checked.

## The five-surface boundary

1. **Governing confinement physics** — the `mechanical_or_liquid_liner_mif`
   configuration (material-liner compression, `magneto_inertial` registry
   family): a magnetised target plasma compressed by a material liner —
   a mechanically driven solid pusher or a rotating liquid-metal liner
   collapsed by a synchronised driver array — on millisecond-class
   timescales. The slow compression regime changes the physics balance:
   the target must survive its own confinement-time budget through the
   whole compression, liner–plasma interface stability and impurity mixing
   become defining budgets, and the liquid liner doubles as a
   neutron-absorbing, heat-extracting first wall in the plant orientation.
   MagLIF's nanosecond pulsed-power solid liner and the standoff
   plasma-jet liner fail this sharing test; target physics belongs to the
   target's owner.
2. **Primary driver and energy delivery** — synchronised mechanical driver
   arrays (pneumatic or piston systems) or rotating-liquid vortex
   formation with programmed collapse; drive-synchronisation contracts
   are first-class configuration facets.
3. **Plant and shot lifecycle** — repetition-oriented shot lifecycle:
   liner formation (vortex spin-up or pusher reset), target-plasma
   injection, synchronised compression, peak-compression burn window,
   expansion and liner recovery, and heat-extraction cycling. Device-level
   hazard semantics cover synchronisation faults, interface instability
   growth, and liner-integrity or splash faults.
4. **Diagnostic, reference-frame, and clock model** — liner-cavity
   coordinate conventions, liner-trajectory and cavity-shape channels,
   target-compression and burn diagnostics, drive-array synchronisation
   monitors, and millisecond-compression/microsecond-burn clock
   identities declared separately.
5. **Solver, evidence, and control-contract boundary** — versioned seams
   towards `SCPN-FUSION-CORE`, review-only semantics towards
   `SCPN-PHASE-ORCHESTRATOR`, and the device-owned CONTROL adapter
   specification towards `SCPN-CONTROL`.

## Position in the SCPN ecosystem

```text
SCPN-MIF-LINER-CORE (device truth: material-liner policy, repetition
                     lifecycle, synchronisation diagnostics, safety
                     envelope, adapter spec)
   │  optional versioned solver seams (none active)
   ├──────────────► SCPN-FUSION-CORE      (solver mathematics, evidence)
   │  typed review-only semantics
   ├──────────────► SCPN-PHASE-ORCHESTRATOR (semantics, comparability)
   │  device-owned adapter (specification only; no implementation)
   ├──────────────► SCPN-CONTROL          (admission; sole ControlAction author)
   │  derived portfolio descriptor (not_federated)
   └──────────────► SCPN-STUDIO           (catalogue, evidence UI, gating)

SCPN-CONTROL ──admitted ControlAction──► independent machine protection
                                          (final veto) ─► plant actuators
```

## Repository layout

| Path | Role |
|---|---|
| `reactor-domain.json` | portable source of project identity and contracts |
| `studio/portfolio-descriptor.json` | derived Studio descriptor, `not_federated` |
| `capability-inventory.json` | generated, truthfully empty inventory |
| `docs/CONTROL_ADAPTER_SPECIFICATION.md` | device-owned adapter contract |
| `docs/THREAT_MODEL.md` | assets, trust boundaries, misuse paths |
| `docs/adr/0001-repository-boundary.md` | boundary decision record |
| `tools/` | validators, derivation tools, preflight orchestrator |
| `tests/` | statement- and branch-complete tests for `tools/` |
| `.github/workflows/` | read-only CI definitions (no publication) |

## Contract surfaces and versioning

- `reactor-domain.json` follows schema `scpn.reactor-domain.v1`; unknown
  schemas are rejected by consumers.
- The Studio descriptor is derived deterministically and embeds the
  manifest's SHA-256; manual edits are detected as drift.
- The CONTROL adapter contract is specification-only at `0.1.0-spec`.
- SPO binding is fixed to reactor registry `1.0.0`, digest
  `786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090`.

## What would change this architecture

Acceptance of a FUSION solver seam through the family migration gate,
ratification of an SPO `ControlIntent`-class contract, or Studio federation
after a real capability passes producer and consumer gates — each recorded
as a versioned contract change in a new ADR.
