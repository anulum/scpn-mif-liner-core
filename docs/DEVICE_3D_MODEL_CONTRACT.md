<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Liner Core — device model contract
-->

# Device model contract

What a consumer of this repository's device models may rely on, written
from the code rather than from a template. Design record:
`docs/adr/0006-device-3d-and-cad-models.md`.

## The two tiers

| Tier | Record | Schema | Built from |
|---|---|---|---|
| G1, tessellated | `DeviceModel3D` | `scpn.mif-liner-3d-model.v1` 1.0.0 | the library's `geometry` group |
| G2, B-rep | `DeviceModelCAD` | `scpn.mif-liner-cad-model.v1` 1.0.0 | the library's `cad` group |

Both are built from the same validated `DeviceConfiguration` and
`DeviceGeometry` and describe the same five bodies. Tier G2 is optional:
it needs the `cad` extra, and every other capability of this package works
without a B-rep back-end.

## Units and frame

| Quantity | Value |
|---|---|
| length | metre |
| handedness | right |
| axis | `z` along the axis of the liner |
| origin | `z = 0` at the midplane of the liner |

## The bodies, in this order

| Name | Role | Material token |
|---|---|---|
| `target_plasma` | `plasma` | `plasma` |
| `liner_shell` | `liner` | `liner_metal` |
| `return_conductor` | `conductor` | `return_conductor` |
| `electrode_upstream` | `conductor` | `electrode` |
| `electrode_downstream` | `conductor` | `electrode` |

The order is fixed and checked at construction on both tiers. A record
whose bodies are reordered or renamed is refused, not sorted.

## Where each dimension comes from

The configuration owns the liner's inner radius, its material kind and the
implosion velocity, and the magnetised target's initial field. The
geometry owns the liner's wall thickness and length, the gap to the return
conductor, that conductor's thickness, and the electrode thickness.

**No cross-check is needed between them, and none is performed.** Every
radius of the build is derived from the configuration's bore by the
geometry's own accessors — `liner_outer_radius_m(bore)` and
`return_conductor_inner_radius_m(bore)` — so a collision between the two
declarations cannot be expressed. That is a property of the shape of the
model, not an omission: where a family's envelope *can* collide with its
configuration, as in the MagLIF family, the refusal is written.

Each declared value is refused in the direction it is wrong, naming the
field and its value. Nothing is clamped.

## Exports and identity

Both records serialise canonically (sorted keys, minimal separators, a
trailing newline, NaN and infinity refused) and carry a SHA-256 digest of
those bytes. Each binds the digests of the configuration and the geometry
it was built from. Tier G2 additionally carries normalised STEP bytes with
their own digest and the versions of the pinned back-ends.

## Declared limits

- **STEP determinism is claimed inside one pinned back-end environment
  only**, never across back-end versions. The record carries the versions.
- The faceting comparison runs at a linear deflection of `1e-4 m` and an
  angular deflection of `0.1 rad`, against an 8-segment tier-G1 reference.
  The evidence kernel bounds each body's faceted volume by `2 d / r` at
  that body's smallest circular radius, and **refuses** a body that misses
  its bound, naming the body.
- The bodies are all cylinders and annular tubes, so each has a
  well-defined smallest circular radius and the bound needs no special
  case.

## Non-claims

- The geometry is the state **before** the implosion. No body moves; no
  trajectory, deformation or instability is modelled.
- The current path is drawn as a coaxial return and two end feeds. The
  power supply, the leads and the switching are not modelled.
- No body is an engineering model; no material property, load, field,
  neutronic quantity or fabrication tolerance is carried.
- No value describes or validates any real machine. Where a record
  reproduces a dimension a filed source prints, that is an anchor on the
  geometry and nothing further.
