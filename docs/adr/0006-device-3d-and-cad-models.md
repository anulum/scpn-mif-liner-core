<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Liner Core — ADR 0006
-->

# ADR 0006 — Device 3D and CAD models, including the path the current takes

Status: accepted (2026-09-04). Adds the fourth and fifth implemented
capabilities, `device_3d_model` and `device_cad_model`, at
`computational_prototype`.

## Context

The repository had a configuration model, diagnostic semantics and level-0
physics, and no geometry. The filed design study drives the implosion with
a large axial current through the liner itself (LA-7686-MS, Los Alamos,
1979), and prints the liner's inner radius, wall thickness and length.

## Decision

1. **Five bodies, and the current path is three of them.** The target
   plasma in the bore, the liner shell, a coaxial return conductor and two
   end electrodes. A current driven axially needs a path back and a pair of
   feeds; a model with only a plasma and a liner would draw the thing being
   imploded but not the device that implodes it. The return conductor and
   the electrodes are declared, because the report prints nothing about
   them, and they are said to be declared.

2. **No library increment.** Every body is a cylinder or an annular tube
   about `z`, which the shared library already builds. This family needed
   no new primitive, unlike the field-reversed configuration whose
   separatrix closes on the axis.

3. **One number, one home.** The liner's inner radius lives in the
   configuration and is read from there. The envelope adds only the liner's
   wall and length, the return gap and thickness, and the electrode
   thickness; each derived radius is the previous one plus a declared
   thickness, and the derived-radius accessors validate the bore they are
   handed.

4. **The model is static and says so.** The geometry is the state before
   the implosion. No body moves, and no trajectory, deformation or
   instability is modelled. That is in the record's own `non_claims`, not
   only in prose, because a static model of a device defined by its motion
   is the kind of thing a reader can misread.

5. **The two capabilities are checked against each other, and against the
   physics.** Tier G2 is checked body by body against its analytic closed
   forms and against its tier-G1 twin by the library's evidence kernel.
   Separately, the tier-G1 liner volume divided by the physics capability's
   liner mass over its density is asserted to be exactly the
   inscribed-polygon ratio of the segment count — measured agreement 1e-14.
   Two capabilities that both describe the liner should describe the same
   liner, and now that is a test rather than an assumption.

6. **Anchoring.** The liner's inner radius, wall thickness and length are
   the printed ones, and each is proven recoverable from the built bodies —
   vertex coordinates and bounding boxes of the tier-G1 meshes and the
   tier-G2 solids, not the configuration that fed them. Everything outside
   the liner is declared.

## Consequences

The family has a device model at both tiers whose body set includes the
circuit that drives it. The kernel-library pin, taken in ADR 0005 for one
transcendental kernel, now also names the geometry and CAD kernels the
tiers consume, and the CAD extra is optional per package as elsewhere in
the group.

Nothing here is an engineering model or a statement about a real machine.
Reproducing a printed dimension is an anchor on the geometry and nothing
further.
