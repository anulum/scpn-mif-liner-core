# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — tier-G1 device model tests

"""The five bodies close, nest, and agree with the physics capability."""

from __future__ import annotations

import hashlib
import json
import math

import pytest
from geometry_fixtures import (
    REFERENCE_SEGMENTS,
    anchor_configuration,
    anchor_geometry,
    reference_configuration,
    reference_geometry,
)
from physics_fixtures import (
    ANCHOR_LINER_LENGTH_M,
    ANCHOR_LOW_YIELD_RADIUS_M,
    anchor_shell,
)

from scpn_mif_liner_core.errors import DeviceGeometryError
from scpn_mif_liner_core.geometry.model import (
    BODY_NAMES,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    DeviceModel3D,
    build_device_model,
)
from scpn_mif_liner_core.physics import COPPER_DENSITY_KG_M3, implosion_state


def reference_model() -> DeviceModel3D:
    """Build the synthetic reference model."""
    return build_device_model(
        reference_configuration(), reference_geometry(), REFERENCE_SEGMENTS
    )


def polygon_area_ratio(segments: int) -> float:
    """Return the inscribed regular polygon area ratio of a segment count."""
    return (segments / (2.0 * math.pi)) * math.sin(2.0 * math.pi / segments)


def test_the_model_carries_the_five_bodies_in_order() -> None:
    """The body set and its order are fixed."""
    assert tuple(mesh.name for mesh in reference_model().meshes) == BODY_NAMES


def test_every_body_is_closed_and_outward_oriented() -> None:
    """Each mesh satisfies the library's closed-surface contract."""
    for mesh in reference_model().meshes:
        assert mesh.signed_volume_m3() > 0.0
        assert mesh.surface_area_m2() > 0.0


def test_the_bodies_nest_the_way_the_current_path_does() -> None:
    """Plasma in the bore, liner around it, return conductor outside."""
    bodies = {mesh.name: mesh for mesh in reference_model().meshes}
    plasma = bodies["target_plasma"].bounding_box()[1][0]
    liner = bodies["liner_shell"].bounding_box()[1][0]
    conductor = bodies["return_conductor"].bounding_box()[1][0]
    assert plasma < liner < conductor


def test_the_electrodes_close_the_assembly_at_both_ends() -> None:
    """The two feeds meet the liner exactly at its ends."""
    bodies = {mesh.name: mesh for mesh in reference_model().meshes}
    liner_low, liner_high = bodies["liner_shell"].bounding_box()
    up_low, up_high = bodies["electrode_upstream"].bounding_box()
    down_low, down_high = bodies["electrode_downstream"].bounding_box()
    assert up_high[2] == liner_low[2]
    assert down_low[2] == liner_high[2]
    assert up_low[2] < up_high[2] < down_low[2] < down_high[2]


def test_the_electrodes_span_the_full_outer_radius() -> None:
    """A feed narrower than the return path would not close the circuit."""
    bodies = {mesh.name: mesh for mesh in reference_model().meshes}
    conductor = bodies["return_conductor"].bounding_box()[1][0]
    for name in ("electrode_upstream", "electrode_downstream"):
        assert bodies[name].bounding_box()[1][0] == conductor


def test_the_record_is_schema_tagged_and_states_its_non_claims() -> None:
    """The record names its schema and carries the non-claims verbatim."""
    record = reference_model().to_record()
    assert record["schema"] == MODEL_SCHEMA
    assert record["schema_version"] == MODEL_SCHEMA_VERSION
    assert record["non_claims"] == list(MODEL_NON_CLAIMS)
    assert [body["name"] for body in record["bodies"]] == list(BODY_NAMES)


def test_the_non_claims_say_the_geometry_is_the_state_before_the_implosion() -> None:
    """A static model of a device that moves must say it is static."""
    assert any("before the implosion" in claim for claim in MODEL_NON_CLAIMS)


def test_the_record_binds_the_inputs_it_was_built_from() -> None:
    """Both digests are the digests of the objects that produced it."""
    configuration, geometry = reference_configuration(), reference_geometry()
    model = build_device_model(configuration, geometry, 64)
    assert model.configuration_digest_sha256 == configuration.digest_sha256()
    assert model.geometry_digest_sha256 == geometry.digest_sha256()


def test_canonical_bytes_are_already_in_canonical_form() -> None:
    """Re-canonicalising the bytes is a no-op, and they round-trip."""
    model = reference_model()
    data = model.canonical_bytes()
    assert data.endswith(b"\n")
    decoded = json.loads(data)
    assert decoded == model.to_record()
    again = json.dumps(decoded, sort_keys=True, separators=(",", ":"))
    assert data == (again + "\n").encode("utf-8")
    assert model.digest_sha256() == hashlib.sha256(data).hexdigest()


def test_a_model_refuses_a_body_set_out_of_order() -> None:
    """The fixed order is enforced at construction, not assumed."""
    model = reference_model()
    with pytest.raises(DeviceGeometryError, match="bodies must be exactly"):
        DeviceModel3D(
            configuration_digest_sha256=model.configuration_digest_sha256,
            geometry_digest_sha256=model.geometry_digest_sha256,
            segments=model.segments,
            meshes=(model.meshes[1], model.meshes[0], *model.meshes[2:]),
        )


@pytest.mark.parametrize("segments", [4, 12, 0])
def test_an_inadmissible_segment_count_is_refused(segments: int) -> None:
    """The library's segment contract governs every body."""
    with pytest.raises(DeviceGeometryError, match="segments"):
        build_device_model(reference_configuration(), reference_geometry(), segments)


def test_the_anchor_bodies_carry_the_printed_liner_dimensions() -> None:
    """The printed values are recoverable from the built liner mesh.

    Read off vertex coordinates and a bounding box of the mesh the model
    produced, not off the configuration that fed it. The library's rings
    start at angle zero, so the vertex on the positive x axis of each ring
    carries that ring's radius exactly.
    """
    model = build_device_model(anchor_configuration(), anchor_geometry(), 64)
    liner = model.meshes[1]
    radii = {vertex[0] for vertex in liner.vertices}
    assert ANCHOR_LOW_YIELD_RADIUS_M in radii
    assert 0.203 in radii
    low, high = liner.bounding_box()
    assert high[2] - low[2] == ANCHOR_LINER_LENGTH_M


@pytest.mark.parametrize("segments", [8, 64, 512])
def test_the_liner_geometry_and_the_liner_physics_are_one_body(
    segments: int,
) -> None:
    """The two capabilities describe the same shell, to the last digit.

    The physics computes the liner's mass from the printed radius,
    thickness, length and density; the geometry tessellates a shell of the
    same dimensions. Dividing the tessellated volume by the physics mass
    over the density must give exactly the inscribed-polygon ratio of the
    segment count — the one difference between them, and one the group
    already characterises. Measured agreement is 1e-14.
    """
    configuration, shell = anchor_configuration(), anchor_shell()
    liner = build_device_model(configuration, anchor_geometry(), segments).meshes[1]
    analytic = implosion_state(configuration, shell).shell_mass_kg / (
        COPPER_DENSITY_KG_M3
    )
    assert math.isclose(
        liner.signed_volume_m3() / analytic,
        polygon_area_ratio(segments),
        rel_tol=1.0e-12,
    )
