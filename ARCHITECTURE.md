<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Liner Core — Architecture summary
-->

# Architecture summary

`SCPN-MIF-LINER-CORE` is the device-family owner for mechanical- and
liquid-liner magnetised-target fusion systems inside the SCPN Reactor
Systems Research Group. The repository is currently `architecture_only`: it
defines the device boundary, its ecosystem contracts, and the validation
tooling that enforces both, and it implements no reactor capability.

The authoritative architecture record is
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). The ownership decision and
its consequences are fixed in
[`docs/adr/0001-repository-boundary.md`](docs/adr/0001-repository-boundary.md).

Boundary in one paragraph: this repository owns material-liner MIF plant
and experiment truth — configuration policy for millisecond-class
compression of magnetised targets by solid pushers or rotating liquid-metal
liners, drive-synchronisation and liner–plasma interface budgets,
repetition-oriented lifecycle semantics (liner formation, target
injection, compression, burn, recovery, thermal cycle) with
synchronisation and liner-integrity hazard records, dual-timescale
diagnostic and clock declarations, actuator-response boundaries,
safety-envelope declarations, and the device-owned CONTROL adapter
specification. Faster liner classes and target physics stay with their
owners; solver mathematics in `SCPN-FUSION-CORE`; typed semantics in
`SCPN-PHASE-ORCHESTRATOR` (review-only); admitted control actions are
formed only by `SCPN-CONTROL`; independent machine protection keeps the
final veto; portfolio presentation belongs to `SCPN-STUDIO`, towards which
this project is `not_federated`.
