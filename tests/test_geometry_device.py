# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — device geometry tests

"""The mechanical envelope validates, serialises and round-trips."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any

import pytest
from geometry_fixtures import anchor_geometry, reference_geometry
from physics_fixtures import ANCHOR_LINER_LENGTH_M, ANCHOR_LOW_YIELD_THICKNESS_M

from scpn_mif_liner_core.errors import DeviceGeometryError
from scpn_mif_liner_core.geometry.device import (
    GEOMETRY_FIELDS,
    DeviceGeometry,
    geometry_from_record,
)


def test_the_record_carries_every_declared_field() -> None:
    """The record is exactly the declared fields, and nothing else."""
    assert sorted(reference_geometry().to_record()) == sorted(GEOMETRY_FIELDS)


def test_the_radii_stack_outward_from_the_configuration_bore() -> None:
    """Each derived radius is the previous one plus a declared thickness."""
    geometry = reference_geometry()
    bore = 0.1
    liner_outer = geometry.liner_outer_radius_m(bore)
    assert liner_outer == bore + geometry.liner_thickness_m
    assert geometry.return_conductor_inner_radius_m(bore) == (
        liner_outer + geometry.return_conductor_gap_m
    )


def test_the_anchor_carries_the_printed_liner_wall_and_length() -> None:
    """The two printed liner dimensions reach the envelope unchanged."""
    geometry = anchor_geometry()
    assert geometry.liner_thickness_m == ANCHOR_LOW_YIELD_THICKNESS_M
    assert geometry.liner_length_m == ANCHOR_LINER_LENGTH_M
    assert geometry.liner_outer_radius_m(0.2) == 0.203


@pytest.mark.parametrize("field", GEOMETRY_FIELDS)
@pytest.mark.parametrize("value", [0.0, -1.0, math.inf, math.nan])
def test_every_field_is_refused_outside_its_domain(field: str, value: float) -> None:
    """A non-finite or non-positive value is refused, naming the field."""
    record = reference_geometry().to_record()
    record[field] = value
    with pytest.raises(DeviceGeometryError, match=field):
        geometry_from_record(record)


@pytest.mark.parametrize("bore", [0.0, -1.0, math.nan])
def test_a_bore_outside_its_domain_is_refused_by_the_derived_radii(
    bore: float,
) -> None:
    """The derived radii validate the bore they are handed."""
    geometry = reference_geometry()
    with pytest.raises(DeviceGeometryError, match="inner_radius_m"):
        geometry.liner_outer_radius_m(bore)
    with pytest.raises(DeviceGeometryError, match="inner_radius_m"):
        geometry.return_conductor_inner_radius_m(bore)


def test_a_record_round_trips_through_its_own_projection() -> None:
    """Projecting and rebuilding gives an equal geometry."""
    geometry = reference_geometry()
    assert geometry_from_record(geometry.to_record()) == geometry


def test_an_unknown_field_is_refused_and_named() -> None:
    """The parser is strict: an unexpected key is an error."""
    record: dict[str, Any] = dict(reference_geometry().to_record())
    record["coil_turns"] = 8
    with pytest.raises(DeviceGeometryError, match="coil_turns"):
        geometry_from_record(record)


def test_a_missing_field_is_refused_and_named() -> None:
    """Every declared field is required."""
    record = reference_geometry().to_record()
    del record["liner_length_m"]
    with pytest.raises(DeviceGeometryError, match="liner_length_m"):
        geometry_from_record(record)


@pytest.mark.parametrize("value", ["0.5", None, True])
def test_a_field_of_the_wrong_type_is_refused(value: Any) -> None:
    """A string, a null and a boolean are not real numbers."""
    record: dict[str, Any] = dict(reference_geometry().to_record())
    record["liner_length_m"] = value
    with pytest.raises(DeviceGeometryError, match="liner_length_m"):
        geometry_from_record(record)


def test_canonical_bytes_and_digest_identify_the_geometry() -> None:
    """The serialisation is canonical and the digest is of those bytes."""
    geometry = reference_geometry()
    data = geometry.canonical_bytes()
    assert data.endswith(b"\n")
    decoded = json.loads(data)
    assert decoded == geometry.to_record()
    assert list(decoded) == sorted(decoded)
    assert geometry.digest_sha256() == hashlib.sha256(data).hexdigest()
    assert geometry.digest_sha256() != anchor_geometry().digest_sha256()


def test_the_dataclass_is_reachable_directly() -> None:
    """The constructor validates the same way the parser does."""
    with pytest.raises(DeviceGeometryError, match="electrode_thickness_m"):
        DeviceGeometry(0.002, 0.1, 0.01, 0.005, 0.0)
