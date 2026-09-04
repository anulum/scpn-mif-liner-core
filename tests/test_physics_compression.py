# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — compression tests

"""Flux conservation and adiabatic compression, in their ideal limits."""

from __future__ import annotations

import math
from collections.abc import Callable

import pytest
from physics_fixtures import ANCHOR_INITIAL_FIELD_T, ANCHOR_LOW_YIELD_RADIUS_M

from scpn_mif_liner_core.errors import DeviceConfigurationError
from scpn_mif_liner_core.physics.compression import (
    MONATOMIC_GAMMA,
    adiabatic_temperature_ratio,
    compressed_density_ratio,
    compressed_field_t,
    compression_state,
)


def test_the_field_rises_with_the_square_of_the_convergence() -> None:
    """Flux through the shell is conserved, so B r^2 is constant."""
    assert compressed_field_t(13.0, 10.0) == 13.0 * 100.0
    assert compressed_field_t(13.0, 2.0) == 13.0 * 4.0


def test_the_density_gain_is_the_area_ratio() -> None:
    """A cylindrical compression conserves the number per unit length."""
    assert compressed_density_ratio(10.0) == 100.0


def test_the_field_gain_and_the_density_gain_are_the_same_factor() -> None:
    """Both are the area ratio, and the record does not pretend otherwise."""
    state = compression_state(13.0, 0.2, 10.0)
    assert state.field_gain == state.density_gain
    assert state.compressed_field_t == 13.0 * state.field_gain


def test_the_temperature_gain_is_the_adiabatic_power() -> None:
    """``(r0/r)^(2(gamma-1))``; at gamma = 5/3 the exponent is 4/3."""
    got = adiabatic_temperature_ratio(8.0, MONATOMIC_GAMMA)
    assert math.isclose(got, 8.0 ** (4.0 / 3.0), rel_tol=1.0e-12)


def test_the_temperature_gain_uses_the_shared_deterministic_kernel() -> None:
    """The non-integer exponent goes through the library, not the platform.

    A transcendental evaluated by the platform would differ between
    back-ends; the library's kernel is the group's reproducible one. The
    two agree to well inside the tolerance any consumer would use, which
    is what makes the substitution safe rather than merely different.
    """
    from scpn_reactor_kernels.numerics.transcendental import power

    assert adiabatic_temperature_ratio(6.0) == power(6.0, 2.0 * (MONATOMIC_GAMMA - 1.0))


def test_a_stronger_compression_heats_more() -> None:
    """The ordering is monotone in the convergence ratio."""
    assert adiabatic_temperature_ratio(4.0) < adiabatic_temperature_ratio(9.0)


@pytest.mark.parametrize("ratio", [1.0, 0.5, 0.0])
def test_every_relation_refuses_a_ratio_that_does_not_converge(ratio: float) -> None:
    """A liner that does not converge compresses nothing.

    All three relations are checked, because a contract enforced by only
    some of the functions that need it is not enforced.
    """
    calls: tuple[Callable[[], float], ...] = (
        lambda: compressed_field_t(13.0, ratio),
        lambda: compressed_density_ratio(ratio),
        lambda: adiabatic_temperature_ratio(ratio),
    )
    for call in calls:
        with pytest.raises(DeviceConfigurationError, match="convergence_ratio"):
            call()


@pytest.mark.parametrize("index", [1.0, 0.5])
def test_an_index_that_does_not_heat_is_refused(index: float) -> None:
    """At gamma of one an adiabatic compression does not raise T."""
    with pytest.raises(DeviceConfigurationError, match="adiabatic_index"):
        adiabatic_temperature_ratio(10.0, index)


@pytest.mark.parametrize("index", [0.0, -1.0, math.nan])
def test_an_index_outside_its_domain_is_refused(index: float) -> None:
    """A non-finite or non-positive index is refused first."""
    with pytest.raises(DeviceConfigurationError, match="adiabatic_index"):
        adiabatic_temperature_ratio(10.0, index)


def test_a_power_that_leaves_the_kernel_range_is_re_raised() -> None:
    """The library's refusal reaches the caller as a device error."""
    with pytest.raises(DeviceConfigurationError, match=r"power|exponent"):
        adiabatic_temperature_ratio(1.0e6, 1.0e6)


def test_a_field_outside_its_domain_is_refused() -> None:
    """The initial field must be strictly positive and finite."""
    with pytest.raises(DeviceConfigurationError, match="initial_field_t"):
        compressed_field_t(0.0, 10.0)


def test_the_state_composes_and_reports_the_stagnation_radius() -> None:
    """The record carries the radius the declared ratio corresponds to."""
    state = compression_state(ANCHOR_INITIAL_FIELD_T, ANCHOR_LOW_YIELD_RADIUS_M, 10.0)
    assert state.stagnation_radius_m == ANCHOR_LOW_YIELD_RADIUS_M / 10.0
    assert state.convergence_ratio == 10.0
    assert state.adiabatic_index == MONATOMIC_GAMMA


def test_the_state_refuses_a_radius_outside_its_domain() -> None:
    """The initial radius must be strictly positive and finite."""
    with pytest.raises(DeviceConfigurationError, match="inner_radius_m"):
        compression_state(13.0, 0.0, 10.0)


def test_the_state_record_keys_are_the_declared_fields() -> None:
    """The record carries one key per field, in declaration order."""
    state = compression_state(13.0, 0.2, 10.0)
    assert list(state.to_record()) == [
        "convergence_ratio",
        "stagnation_radius_m",
        "adiabatic_index",
        "compressed_field_t",
        "field_gain",
        "density_gain",
        "temperature_gain",
    ]
