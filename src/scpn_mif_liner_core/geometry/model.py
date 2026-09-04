# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — tier-G1 device model

"""Tier-G1 tessellated model of a liner magneto-inertial device.

Five bodies in a fixed order: the magnetised target plasma inside the
liner bore, the liner shell itself, the coaxial return conductor that
closes the current path, and the two end electrodes that drive the axial
current through the liner.

The return conductor and the electrodes are here because the filed design
study drives the implosion with a large axial current through the liner
(LA-7686-MS, Los Alamos, 1979). A current driven axially needs a path
back and a pair of feeds; leaving them out would model a liner but not the
device that implodes it.

Every body is a cylinder or an annular tube about ``z``, so this tier
needs no primitive the shared library does not already have. The axis is
``z``, the origin is the midplane of the liner, and the model is symmetric
about it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.errors import GeometryError
from scpn_reactor_kernels.geometry import (
    TriangleMesh,
    annular_tube,
    cylinder_solid,
    require_segments,
)

from scpn_mif_liner_core.configuration import DeviceConfiguration
from scpn_mif_liner_core.errors import DeviceGeometryError
from scpn_mif_liner_core.geometry.device import DeviceGeometry

MODEL_SCHEMA: Final = "scpn.mif-liner-3d-model.v1"
MODEL_SCHEMA_VERSION: Final = "1.0.0"
MODEL_UNITS: Final = {
    "length": "metre",
    "handedness": "right",
    "axis": "z along the axis of the liner",
    "origin": "z = 0 at the midplane of the liner",
}
MODEL_NON_CLAIMS: Final = (
    "analytic surfaces tessellated from a synthetic configuration and geometry",
    (
        "the geometry is the state before the implosion; no body moves and no "
        "trajectory, deformation or instability is modelled"
    ),
    (
        "the current path is drawn as a coaxial return and two end feeds; the "
        "power supply, the leads and the switching are not modelled"
    ),
    "no body is a CAD solid or an engineering model",
    "no material property, load, field or neutronic quantity is carried",
    "no value describes or validates any real machine",
)

ROLE_PLASMA: Final = "plasma"
ROLE_LINER: Final = "liner"
ROLE_CONDUCTOR: Final = "conductor"
MATERIAL_PLASMA: Final = "plasma"
MATERIAL_LINER_METAL: Final = "liner_metal"
MATERIAL_RETURN_CONDUCTOR: Final = "return_conductor"
MATERIAL_ELECTRODE: Final = "electrode"

BODY_TARGET_PLASMA: Final = "target_plasma"
BODY_LINER_SHELL: Final = "liner_shell"
BODY_RETURN_CONDUCTOR: Final = "return_conductor"
BODY_ELECTRODE_UPSTREAM: Final = "electrode_upstream"
BODY_ELECTRODE_DOWNSTREAM: Final = "electrode_downstream"
BODY_NAMES: Final = (
    BODY_TARGET_PLASMA,
    BODY_LINER_SHELL,
    BODY_RETURN_CONDUCTOR,
    BODY_ELECTRODE_UPSTREAM,
    BODY_ELECTRODE_DOWNSTREAM,
)


@dataclass(frozen=True, slots=True)
class DeviceModel3D:
    """The tessellated device model of one configuration and geometry.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the configuration the model was built from.
    geometry_digest_sha256
        Digest of the geometry the model was built from.
    segments
        Circumferential segment count every body was tessellated at.
    meshes
        The five bodies in the fixed order of :data:`BODY_NAMES`.

    Raises
    ------
    DeviceGeometryError
        If the body names or their order differ from :data:`BODY_NAMES`.
    """

    configuration_digest_sha256: str
    geometry_digest_sha256: str
    segments: int
    meshes: tuple[TriangleMesh, ...]

    def __post_init__(self) -> None:
        """Validate the body set and its order.

        Raises
        ------
        DeviceGeometryError
            If the body names or their order differ from
            :data:`BODY_NAMES`.
        """
        names = tuple(mesh.name for mesh in self.meshes)
        if names != BODY_NAMES:
            raise DeviceGeometryError(
                f"meshes: bodies must be exactly {BODY_NAMES!r} in order, got {names!r}"
            )

    def to_record(self) -> dict[str, Any]:
        """Project the model to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with one entry per body.
        """
        return {
            "schema": MODEL_SCHEMA,
            "schema_version": MODEL_SCHEMA_VERSION,
            "units": dict(MODEL_UNITS),
            "non_claims": list(MODEL_NON_CLAIMS),
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "geometry_digest_sha256": self.geometry_digest_sha256,
            "segments": self.segments,
            "bodies": [
                {
                    "name": mesh.name,
                    "role": mesh.role,
                    "material_identifier": mesh.material_identifier,
                    "vertex_count": mesh.vertex_count,
                    "face_count": mesh.face_count,
                    "volume_m3": mesh.signed_volume_m3(),
                    "surface_area_m2": mesh.surface_area_m2(),
                }
                for mesh in self.meshes
            ],
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the model record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact model record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def build_device_model(
    configuration: DeviceConfiguration, geometry: DeviceGeometry, segments: int
) -> DeviceModel3D:
    """Tessellate the five bodies of a validated design.

    Parameters
    ----------
    configuration
        Validated liner-MIF configuration; its liner supplies the bore.
    geometry
        Validated mechanical envelope.
    segments
        Circumferential segments for every body; at least 8, multiple
        of 8.

    Returns
    -------
    DeviceModel3D
        The composed model.

    Raises
    ------
    DeviceGeometryError
        If the segment count is invalid; the library's refusal is
        re-raised under the device error type with its message.

    Notes
    -----
    The body constructors are not wrapped. Every radial pair is ordered
    because each thickness and gap is strictly positive, and every axial
    pair is ordered because the liner length and the electrode thickness
    are; the segment count has already passed the library's contract. A
    translation layer there could not run.
    """
    try:
        require_segments(segments)
    except GeometryError as exc:
        raise DeviceGeometryError(str(exc)) from exc
    bore = configuration.liner.inner_radius_m
    liner_outer = geometry.liner_outer_radius_m(bore)
    return_inner = geometry.return_conductor_inner_radius_m(bore)
    return_outer = return_inner + geometry.return_conductor_thickness_m
    half = geometry.liner_length_m / 2.0
    electrode = geometry.electrode_thickness_m
    bodies = (
        (
            BODY_TARGET_PLASMA,
            ROLE_PLASMA,
            MATERIAL_PLASMA,
            cylinder_solid(bore, -half, half, segments),
        ),
        (
            BODY_LINER_SHELL,
            ROLE_LINER,
            MATERIAL_LINER_METAL,
            annular_tube(bore, liner_outer, -half, half, segments),
        ),
        (
            BODY_RETURN_CONDUCTOR,
            ROLE_CONDUCTOR,
            MATERIAL_RETURN_CONDUCTOR,
            annular_tube(return_inner, return_outer, -half, half, segments),
        ),
        (
            BODY_ELECTRODE_UPSTREAM,
            ROLE_CONDUCTOR,
            MATERIAL_ELECTRODE,
            cylinder_solid(return_outer, -half - electrode, -half, segments),
        ),
        (
            BODY_ELECTRODE_DOWNSTREAM,
            ROLE_CONDUCTOR,
            MATERIAL_ELECTRODE,
            cylinder_solid(return_outer, half, half + electrode, segments),
        ),
    )
    meshes = tuple(
        TriangleMesh(
            name=name,
            role=role,
            material_identifier=material,
            vertices=vertices,
            faces=faces,
        )
        for name, role, material, (vertices, faces) in bodies
    )
    return DeviceModel3D(
        configuration_digest_sha256=configuration.digest_sha256(),
        geometry_digest_sha256=geometry.digest_sha256(),
        segments=segments,
        meshes=meshes,
    )
