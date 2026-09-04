# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — device geometry model

"""Validated mechanical envelope of a liner magneto-inertial device.

The configuration carries the liner's inner radius; it is read from there
and not repeated here. What this envelope adds is the rest of the
assembly: the liner's own wall and length, the coaxial return conductor
that closes the current path, and the end electrodes that drive the axial
current through the liner.

The arrangement is the one the filed design study describes — a thin metal
liner imploded by self-magnetic fields from a large axial current driven
through it (R. W. Moses, R. A. Krakowski and R. L. Miller, LA-7686-MS, Los
Alamos, 1979). A current driven axially needs a path back, so the return
conductor and the electrodes are part of the device, not decoration.

Validation is fail-closed, serialisation is canonical, and the SHA-256
digest identifies the exact geometry.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_mif_liner_core.errors import DeviceGeometryError
from scpn_mif_liner_core.parameters import require_positive

GEOMETRY_FIELDS: Final = (
    "liner_thickness_m",
    "liner_length_m",
    "return_conductor_gap_m",
    "return_conductor_thickness_m",
    "electrode_thickness_m",
)


def _positive(name: str, value: float) -> float:
    """Apply the shared positivity rule under the geometry error type.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceGeometryError
        If the value is non-finite or not strictly positive.
    """
    try:
        return require_positive(name, value)
    except ValueError as exc:
        raise DeviceGeometryError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class DeviceGeometry:
    """Validated liner-MIF mechanical envelope (SI units in the names).

    Parameters
    ----------
    liner_thickness_m
        Radial thickness of the liner shell; strictly positive. The
        liner's inner radius is the configuration's and is not repeated.
    liner_length_m
        Axial length of the liner; strictly positive.
    return_conductor_gap_m
        Radial vacuum gap between the liner's outer surface and the
        return conductor's bore; strictly positive.
    return_conductor_thickness_m
        Radial thickness of the return conductor; strictly positive.
    electrode_thickness_m
        Axial thickness of each of the two end electrodes; strictly
        positive.

    Raises
    ------
    DeviceGeometryError
        If any value is non-finite or not strictly positive.
    """

    liner_thickness_m: float
    liner_length_m: float
    return_conductor_gap_m: float
    return_conductor_thickness_m: float
    electrode_thickness_m: float

    def __post_init__(self) -> None:
        """Validate every declared value.

        Raises
        ------
        DeviceGeometryError
            If any value is non-finite or not strictly positive.
        """
        for name in GEOMETRY_FIELDS:
            _positive(name, getattr(self, name))

    def liner_outer_radius_m(self, inner_radius_m: float) -> float:
        """Return the liner's outer radius for a given bore.

        Parameters
        ----------
        inner_radius_m
            The configuration's liner inner radius; strictly positive.

        Returns
        -------
        float
            Bore plus wall.

        Raises
        ------
        DeviceGeometryError
            If the bore is non-finite or not strictly positive.
        """
        return _positive("inner_radius_m", inner_radius_m) + self.liner_thickness_m

    def return_conductor_inner_radius_m(self, inner_radius_m: float) -> float:
        """Return the return conductor's bore for a given liner bore.

        Parameters
        ----------
        inner_radius_m
            The configuration's liner inner radius; strictly positive.

        Returns
        -------
        float
            The liner's outer radius plus the vacuum gap.

        Raises
        ------
        DeviceGeometryError
            If the bore is non-finite or not strictly positive.
        """
        return self.liner_outer_radius_m(inner_radius_m) + self.return_conductor_gap_m

    def to_record(self) -> dict[str, float]:
        """Project the geometry to a JSON-serialisable record.

        Returns
        -------
        dict[str, float]
            Every declared parameter under its name.
        """
        return {name: getattr(self, name) for name in GEOMETRY_FIELDS}

    def canonical_bytes(self) -> bytes:
        """Serialise the geometry canonically.

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
        """Identify the exact geometry.

        Returns
        -------
        str
            SHA-256 digest of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _number(record: dict[str, Any], field: str) -> float:
    """Return one required real-number field of a record.

    Parameters
    ----------
    record
        Decoded object.
    field
        Field name.

    Returns
    -------
    float
        The value as a float.

    Raises
    ------
    DeviceGeometryError
        If the field is absent or is not a real number.
    """
    if field not in record:
        raise DeviceGeometryError(f"{field}: required")
    value = record[field]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DeviceGeometryError(f"{field}: must be a real number, got {value!r}")
    return float(value)


def geometry_from_record(record: dict[str, Any]) -> DeviceGeometry:
    """Build a geometry from a decoded record, refusing unknown fields.

    Parameters
    ----------
    record
        Decoded object carrying exactly :data:`GEOMETRY_FIELDS`.

    Returns
    -------
    DeviceGeometry
        The validated geometry.

    Raises
    ------
    DeviceGeometryError
        If a field is missing, of the wrong type, unknown, or violates a
        model invariant.
    """
    unknown = sorted(set(record) - set(GEOMETRY_FIELDS))
    if unknown:
        raise DeviceGeometryError(f"geometry: unknown fields {unknown!r}")
    return DeviceGeometry(**{name: _number(record, name) for name in GEOMETRY_FIELDS})
