# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — implosion state tests

"""The driven shell's mechanics, and the printed design points it meets."""

from __future__ import annotations

import math

import pytest
from physics_fixtures import (
    ANCHOR_ENERGY_TOLERANCE,
    ANCHOR_HIGH_YIELD_ENERGY_J,
    ANCHOR_IMPLOSION_WINDOW_S,
    ANCHOR_INITIAL_FIELD_T,
    ANCHOR_LOW_YIELD_ENERGY_J,
    ANCHOR_LOW_YIELD_RADIUS_M,
    ANCHOR_LOW_YIELD_THICKNESS_M,
    anchor_configuration,
    anchor_shell,
    reference_configuration,
    reference_shell,
)

from scpn_mif_liner_core.errors import DeviceConfigurationError
from scpn_mif_liner_core.physics.implosion import (
    COPPER_DENSITY_KG_M3,
    MU0,
    ShellInputs,
    implosion_state,
    magnetic_pressure_pa,
    require_convergence_ratio,
    shell_mass_kg,
)


def test_the_mass_is_the_exact_annulus_not_the_thin_shell() -> None:
    """The ``d^2`` term is kept, and it is not negligible here.

    The thin-shell approximation is light by ``d / (2 r + d)``, which at
    the filed design point's three-millimetre shell on a
    two-hundred-millimetre radius is 0.74 % — comparable to the one per
    cent the energy anchor is asserted at, so discarding it would eat most
    of that margin.
    """
    exact = shell_mass_kg(0.2, 0.003, 0.2, COPPER_DENSITY_KG_M3)
    thin = COPPER_DENSITY_KG_M3 * 2.0 * math.pi * 0.2 * 0.003 * 0.2
    assert exact > thin
    assert math.isclose(
        (exact - thin) / exact, 0.003 / (2.0 * 0.2 + 0.003), rel_tol=1.0e-12
    )


def test_the_mass_is_the_closed_form() -> None:
    """The annulus is the difference of two discs times the length."""
    assert shell_mass_kg(0.2, 0.003, 0.2, 8920.0) == (
        8920.0 * math.pi * (0.203 * 0.203 - 0.2 * 0.2) * 0.2
    )


@pytest.mark.parametrize(
    ("radius", "thickness", "length", "density", "field_name"),
    [
        (0.0, 0.003, 0.2, 8920.0, "inner_radius_m"),
        (0.2, 0.0, 0.2, 8920.0, "thickness_m"),
        (0.2, 0.003, math.inf, 8920.0, "length_m"),
        (0.2, 0.003, 0.2, math.nan, "density_kg_m3"),
    ],
)
def test_the_mass_refuses_each_argument_by_name(
    radius: float, thickness: float, length: float, density: float, field_name: str
) -> None:
    """Each refusal names the field that is wrong."""
    with pytest.raises(DeviceConfigurationError, match=field_name):
        shell_mass_kg(radius, thickness, length, density)


def test_the_magnetic_pressure_is_the_closed_form() -> None:
    """The drive pressure is B squared over twice the permeability."""
    assert magnetic_pressure_pa(13.0) == 13.0 * 13.0 / (2.0 * MU0)


@pytest.mark.parametrize("field", [0.0, -1.0, math.inf, math.nan])
def test_the_magnetic_pressure_refuses_a_field_outside_its_domain(
    field: float,
) -> None:
    """A field that is not strictly positive and finite is refused."""
    with pytest.raises(DeviceConfigurationError, match="field_t"):
        magnetic_pressure_pa(field)


def test_the_state_composes_the_configuration_and_the_declared_shell() -> None:
    """Every field follows from the configuration and the declared shell."""
    configuration, shell = reference_configuration(), reference_shell()
    state = implosion_state(configuration, shell)
    liner = configuration.liner
    assert state.inner_radius_m == liner.inner_radius_m
    assert state.implosion_velocity_m_s == liner.implosion_velocity_km_s * 1.0e3
    assert state.specific_kinetic_energy_j_kg == liner.specific_kinetic_energy_j_kg()
    assert state.kinetic_energy_j == state.shell_mass_kg * (
        state.specific_kinetic_energy_j_kg
    )
    assert state.drive_magnetic_pressure_pa == magnetic_pressure_pa(
        configuration.target.initial_field_t
    )


def test_the_characteristic_time_is_the_radius_over_the_velocity() -> None:
    """A scale, not a trajectory, and the record says so."""
    state = implosion_state(reference_configuration(), reference_shell())
    assert state.characteristic_implosion_time_s == (
        state.inner_radius_m / state.implosion_velocity_m_s
    )


def test_the_state_record_keys_are_the_declared_fields() -> None:
    """The record carries one key per field, in declaration order."""
    state = implosion_state(reference_configuration(), reference_shell())
    assert list(state.to_record()) == [
        "inner_radius_m",
        "implosion_velocity_m_s",
        "shell_mass_kg",
        "specific_kinetic_energy_j_kg",
        "kinetic_energy_j",
        "characteristic_implosion_time_s",
        "drive_magnetic_pressure_pa",
    ]


@pytest.mark.parametrize(
    ("thickness", "length", "density", "field_name"),
    [
        (0.0, 0.1, 8920.0, "thickness_m"),
        (0.002, -1.0, 8920.0, "length_m"),
        (0.002, 0.1, math.inf, "density_kg_m3"),
    ],
)
def test_the_shell_inputs_refuse_each_field_by_name(
    thickness: float, length: float, density: float, field_name: str
) -> None:
    """A declared shell dimension outside its bound is refused."""
    with pytest.raises(DeviceConfigurationError, match=field_name):
        ShellInputs(thickness_m=thickness, length_m=length, density_kg_m3=density)


@pytest.mark.parametrize("ratio", [1.0, 0.5, 0.0, -2.0])
def test_a_liner_that_does_not_converge_is_refused(ratio: float) -> None:
    """A ratio of one compresses nothing; below one it expands."""
    with pytest.raises(DeviceConfigurationError, match="convergence_ratio"):
        require_convergence_ratio(ratio)


@pytest.mark.parametrize("high_yield", [False, True])
def test_the_anchor_reproduces_the_printed_liner_energy(high_yield: bool) -> None:
    """Both printed design points come back out of the printed geometry.

    This is also what establishes the implosion velocity. The report's
    text loses its superscript in extraction, so the velocity reads as
    "10 m/s"; only one sentence survives to give the range 1e3 to 1e4.
    At 1e4 the kinetic energy of an annular copper shell of the printed
    radius, thickness and length reproduces both printed energies to
    under one per cent, and at 1e3 it is a hundredfold too small. Two
    independent printed rows agreeing is the evidence.

    The tolerance is one per cent and not tighter for a stated reason:
    the report rounds its energies to three figures and never prints the
    copper density it used.
    """
    printed = ANCHOR_HIGH_YIELD_ENERGY_J if high_yield else ANCHOR_LOW_YIELD_ENERGY_J
    state = implosion_state(
        anchor_configuration(high_yield=high_yield),
        anchor_shell(high_yield=high_yield),
    )
    assert math.isclose(
        state.kinetic_energy_j, printed, rel_tol=ANCHOR_ENERGY_TOLERANCE
    )


def test_the_wrong_velocity_would_miss_the_printed_energy_entirely() -> None:
    """The evidence is only evidence if the other candidate fails.

    Asserting that 1e4 fits is worth little on its own; the recovery is
    sound because the other end of the printed range is out by two orders
    of magnitude.
    """
    from scpn_mif_liner_core.parameters import MaterialLiner

    slow = anchor_configuration()
    slow_liner = MaterialLiner(
        kind=slow.liner.kind,
        inner_radius_m=slow.liner.inner_radius_m,
        implosion_velocity_km_s=1.0,
    )
    state = implosion_state(
        type(slow)(
            identifier=slow.identifier,
            liner=slow_liner,
            target=slow.target,
            registry=slow.registry,
        ),
        anchor_shell(),
    )
    assert state.kinetic_energy_j < ANCHOR_LOW_YIELD_ENERGY_J / 50.0


@pytest.mark.parametrize("high_yield", [False, True])
def test_the_anchor_time_falls_inside_the_printed_implosion_window(
    high_yield: bool,
) -> None:
    """The report prints 20 to 40 microseconds; both points land in it.

    An independent check on the same recovered velocity, from a different
    printed statement: the characteristic time is the printed radius over
    that velocity, and the report's abstract brackets the duration.
    """
    state = implosion_state(
        anchor_configuration(high_yield=high_yield),
        anchor_shell(high_yield=high_yield),
    )
    low, high = ANCHOR_IMPLOSION_WINDOW_S
    assert low <= state.characteristic_implosion_time_s <= high


def test_the_anchor_carries_the_printed_radius_thickness_and_field() -> None:
    """The printed values reach the state through the built objects."""
    configuration, shell = anchor_configuration(), anchor_shell()
    state = implosion_state(configuration, shell)
    assert state.inner_radius_m == ANCHOR_LOW_YIELD_RADIUS_M
    assert shell.thickness_m == ANCHOR_LOW_YIELD_THICKNESS_M
    assert configuration.target.initial_field_t == ANCHOR_INITIAL_FIELD_T
    assert state.drive_magnetic_pressure_pa == magnetic_pressure_pa(
        ANCHOR_INITIAL_FIELD_T
    )
