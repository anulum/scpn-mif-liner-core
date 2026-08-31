# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — parameter model tests

"""Every validation branch of the material-liner-MIF parameter model.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

from scpn_mif_liner_core.errors import DeviceConfigurationError
from scpn_mif_liner_core.parameters import (
    MagnetisedTarget,
    MaterialLiner,
    require_finite,
    require_positive,
)


def synthetic_liner(**overrides: Any) -> MaterialLiner:
    """Build a valid synthetic material liner with optional overrides."""
    values: dict[str, Any] = {
        "kind": "liquid",
        "inner_radius_m": 0.2,
        "implosion_velocity_km_s": 2.0,
    }
    values.update(overrides)
    return MaterialLiner(**values)


def test_require_finite_accepts_and_rejects() -> None:
    """The finite guard returns the value and rejects NaN and infinity."""
    assert require_finite("x", 1.5) == 1.5
    for bad in (math.nan, math.inf, -math.inf):
        with pytest.raises(DeviceConfigurationError, match="x: must be finite"):
            require_finite("x", bad)


def test_require_positive_accepts_and_rejects() -> None:
    """The positive guard returns the value and rejects zero and below."""
    assert require_positive("x", 0.1) == 0.1
    for bad in (0.0, -2.0):
        with pytest.raises(DeviceConfigurationError, match="strictly positive"):
            require_positive("x", bad)
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        require_positive("x", math.nan)


def test_both_liner_kinds_construct() -> None:
    """Both material-liner classes construct."""
    assert synthetic_liner().kind == "liquid"
    assert synthetic_liner(kind="solid").kind == "solid"


def test_specific_kinetic_energy_formula() -> None:
    """The specific kinetic energy follows ``v^2 / 2`` exactly."""
    assert synthetic_liner().specific_kinetic_energy_j_kg() == pytest.approx(
        0.5 * (2.0e3) ** 2
    )


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"kind": "plasma"}, "kind"),
        ({"inner_radius_m": 0.0}, "inner_radius_m"),
        ({"implosion_velocity_km_s": -1.0}, "implosion_velocity_km_s"),
        ({"implosion_velocity_km_s": math.nan}, "implosion_velocity_km_s"),
    ],
)
def test_invalid_liner_is_rejected(overrides: dict[str, Any], fragment: str) -> None:
    """Each material-liner violation is rejected with its field name."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        synthetic_liner(**overrides)


def test_valid_target_constructs() -> None:
    """A valid magnetised target constructs unchanged."""
    assert MagnetisedTarget(initial_field_t=5.0).initial_field_t == 5.0


def test_invalid_target_is_rejected() -> None:
    """A missing premagnetisation field is rejected."""
    with pytest.raises(DeviceConfigurationError, match="initial_field_t"):
        MagnetisedTarget(initial_field_t=0.0)
    with pytest.raises(DeviceConfigurationError, match="initial_field_t"):
        MagnetisedTarget(initial_field_t=math.inf)
