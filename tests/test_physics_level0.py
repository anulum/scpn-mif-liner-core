# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — level-0 record tests

"""The composed level-0 record: identity, canonicity and its non-claims."""

from __future__ import annotations

import hashlib
import json

import pytest
from physics_fixtures import (
    ANCHOR_ENERGY_TOLERANCE,
    ANCHOR_INITIAL_FIELD_T,
    ANCHOR_LOW_YIELD_ENERGY_J,
    anchor_configuration,
    anchor_shell,
    reference_configuration,
    reference_shell,
)

from scpn_mif_liner_core.errors import DeviceConfigurationError
from scpn_mif_liner_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    Level0Physics,
    level0_physics,
)


def reference_record() -> Level0Physics:
    """Build the synthetic reference level-0 record."""
    return level0_physics(reference_configuration(), reference_shell(), 10.0)


def test_the_record_is_schema_tagged_and_states_its_non_claims() -> None:
    """The record names its schema and carries the non-claims verbatim."""
    record = reference_record().to_record()
    assert record["schema"] == LEVEL0_SCHEMA
    assert record["schema_version"] == LEVEL0_SCHEMA_VERSION
    assert record["non_claims"] == list(LEVEL0_NON_CLAIMS)
    assert list(record) == [
        "schema",
        "schema_version",
        "configuration_digest_sha256",
        "shell",
        "implosion",
        "compression",
        "non_claims",
    ]


def test_the_non_claims_say_the_compressions_are_upper_bounds() -> None:
    """Both ideal limits are named in the record, not only in prose."""
    joined = " ".join(LEVEL0_NON_CLAIMS)
    assert "upper bounds" in joined
    assert "perfect-conductor" in joined


def test_the_record_carries_the_declared_shell() -> None:
    """The shell dimensions reach the record under their own names."""
    assert reference_record().to_record()["shell"] == {
        "thickness_m": 0.002,
        "length_m": 0.1,
        "density_kg_m3": 8920.0,
    }


def test_the_record_binds_the_configuration_it_was_built_from() -> None:
    """The record carries the digest of its own configuration."""
    configuration = reference_configuration()
    record = level0_physics(configuration, reference_shell(), 10.0)
    assert record.configuration_digest_sha256 == configuration.digest_sha256()


def test_canonical_bytes_are_already_in_canonical_form() -> None:
    """Re-canonicalising the bytes is a no-op, and they round-trip."""
    record = reference_record()
    data = record.canonical_bytes()
    assert data.endswith(b"\n")
    decoded = json.loads(data)
    assert decoded == record.to_record()
    assert list(decoded) == sorted(decoded)
    again = json.dumps(decoded, sort_keys=True, separators=(",", ":"))
    assert data == (again + "\n").encode("utf-8")
    assert record.digest_sha256() == hashlib.sha256(data).hexdigest()


def test_the_digest_is_stable_and_moves_with_the_convergence() -> None:
    """The same inputs give the same bytes; a different ratio does not."""
    assert reference_record().digest_sha256() == reference_record().digest_sha256()
    other = level0_physics(reference_configuration(), reference_shell(), 12.0)
    assert other.digest_sha256() != reference_record().digest_sha256()


def test_a_convergence_that_does_not_compress_is_refused() -> None:
    """The composed record applies the ratio contract before building."""
    with pytest.raises(DeviceConfigurationError, match="convergence_ratio"):
        level0_physics(reference_configuration(), reference_shell(), 1.0)


def test_the_anchor_record_carries_the_printed_energy_and_field() -> None:
    """Both printed values are recoverable from the composed record.

    Read out of the record the model builds, not out of the fixture that
    fed it.
    """
    record = level0_physics(anchor_configuration(), anchor_shell(), 10.0).to_record()
    energy = record["implosion"]["kinetic_energy_j"]
    assert abs(energy - ANCHOR_LOW_YIELD_ENERGY_J) / ANCHOR_LOW_YIELD_ENERGY_J < (
        ANCHOR_ENERGY_TOLERANCE
    )
    compressed = record["compression"]["compressed_field_t"]
    assert compressed == ANCHOR_INITIAL_FIELD_T * 100.0
    assert record["implosion"]["characteristic_implosion_time_s"] == 20.0e-6
