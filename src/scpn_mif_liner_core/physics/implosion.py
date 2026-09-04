# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — liner implosion state

"""Implosion state of a cylindrical liner of declared shell dimensions.

The configuration carries the liner's inner radius and its implosion
velocity; the shell's thickness, length and material density are declared
model inputs, because the configuration does not carry them. From those
five numbers the elementary mechanics of a driven annular shell follows:
its mass, its kinetic energy at the declared velocity, the magnetic
pressure of a driving field, and the characteristic time the shell needs
to cross its own initial radius.

Every relation is elementary and closed form. The reference the anchor
fixture is built against is the Fast Liner Reactor design point of
R. W. Moses, R. A. Krakowski and R. L. Miller, LA-7686-MS (Los Alamos,
1979), whose Table II-I prints the liner radius, thickness and field, and
whose text prints the material, the length and the implosion velocity.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Final

from scpn_mif_liner_core.configuration import DeviceConfiguration
from scpn_mif_liner_core.errors import DeviceConfigurationError
from scpn_mif_liner_core.parameters import require_positive

#: Vacuum permeability, SI, CODATA.
MU0: Final = 1.25663706212e-6
#: Density of copper in kilograms per cubic metre; the material the filed
#: design point names for its liner.
COPPER_DENSITY_KG_M3: Final = 8920.0
#: Density of aluminium, the other common solid-liner material.
ALUMINIUM_DENSITY_KG_M3: Final = 2700.0


@dataclass(frozen=True, slots=True)
class ShellInputs:
    """Declared shell dimensions the configuration does not carry.

    Parameters
    ----------
    thickness_m
        Radial thickness of the liner shell; strictly positive.
    length_m
        Axial length of the liner shell; strictly positive.
    density_kg_m3
        Mass density of the liner material; strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If any input is non-finite or not strictly positive.
    """

    thickness_m: float
    length_m: float
    density_kg_m3: float

    def __post_init__(self) -> None:
        """Validate every declared input.

        Raises
        ------
        DeviceConfigurationError
            If any input is non-finite or not strictly positive.
        """
        require_positive("thickness_m", self.thickness_m)
        require_positive("length_m", self.length_m)
        require_positive("density_kg_m3", self.density_kg_m3)

    def to_record(self) -> dict[str, float]:
        """Project the inputs to a JSON-serialisable record.

        Returns
        -------
        dict[str, float]
            One key per declared input.
        """
        return {
            "thickness_m": self.thickness_m,
            "length_m": self.length_m,
            "density_kg_m3": self.density_kg_m3,
        }


def shell_mass_kg(
    inner_radius_m: float, thickness_m: float, length_m: float, density_kg_m3: float
) -> float:
    """Return the mass of an annular cylindrical shell.

    Parameters
    ----------
    inner_radius_m
        Inner radius of the shell; strictly positive.
    thickness_m
        Radial thickness; strictly positive.
    length_m
        Axial length; strictly positive.
    density_kg_m3
        Material density; strictly positive.

    Returns
    -------
    float
        ``rho pi ((r + d)^2 - r^2) l``, the exact annulus rather than the
        thin-shell approximation ``rho 2 pi r d l``. The two differ by the
        ``d^2`` term, a fraction ``d / (2 r + d)`` of the mass — 0.74 % at
        the filed design point's three-millimetre shell on a
        two-hundred-millimetre radius. That is comparable to the tolerance
        the energy anchor is asserted at, so it is not discarded here.

    Raises
    ------
    DeviceConfigurationError
        If any argument is non-finite or not strictly positive.
    """
    inner = require_positive("inner_radius_m", inner_radius_m)
    thickness = require_positive("thickness_m", thickness_m)
    length = require_positive("length_m", length_m)
    density = require_positive("density_kg_m3", density_kg_m3)
    outer = inner + thickness
    return density * math.pi * (outer * outer - inner * inner) * length


def magnetic_pressure_pa(field_t: float) -> float:
    """Return the magnetic pressure of a field.

    Parameters
    ----------
    field_t
        Magnetic flux density in tesla; strictly positive.

    Returns
    -------
    float
        ``B^2 / 2 mu0`` in pascal.

    Raises
    ------
    DeviceConfigurationError
        If the field is non-finite or not strictly positive.
    """
    field = require_positive("field_t", field_t)
    return field * field / (2.0 * MU0)


@dataclass(frozen=True, slots=True)
class ImplosionState:
    """Mechanical state of one liner at its declared operating point.

    Parameters
    ----------
    inner_radius_m
        Initial inner radius, from the configuration.
    implosion_velocity_m_s
        Implosion velocity, from the configuration.
    shell_mass_kg
        Mass of the annular shell.
    specific_kinetic_energy_j_kg
        ``v^2 / 2``.
    kinetic_energy_j
        ``m v^2 / 2``.
    characteristic_implosion_time_s
        ``r_0 / v``: the time the shell needs to cross its own initial
        radius at the declared velocity. It is a scale, not a trajectory:
        a real implosion accelerates, so this is the order of the
        duration and not a prediction of it.
    drive_magnetic_pressure_pa
        ``B_0^2 / 2 mu0`` of the target's initial field.
    """

    inner_radius_m: float
    implosion_velocity_m_s: float
    shell_mass_kg: float
    specific_kinetic_energy_j_kg: float
    kinetic_energy_j: float
    characteristic_implosion_time_s: float
    drive_magnetic_pressure_pa: float

    def to_record(self) -> dict[str, Any]:
        """Project the state to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per field, in the declaration order of the class.
        """
        return {
            "inner_radius_m": self.inner_radius_m,
            "implosion_velocity_m_s": self.implosion_velocity_m_s,
            "shell_mass_kg": self.shell_mass_kg,
            "specific_kinetic_energy_j_kg": self.specific_kinetic_energy_j_kg,
            "kinetic_energy_j": self.kinetic_energy_j,
            "characteristic_implosion_time_s": self.characteristic_implosion_time_s,
            "drive_magnetic_pressure_pa": self.drive_magnetic_pressure_pa,
        }


def implosion_state(
    configuration: DeviceConfiguration, shell: ShellInputs
) -> ImplosionState:
    """Compose the implosion state of one validated configuration.

    Parameters
    ----------
    configuration
        Validated device configuration; its liner supplies the inner
        radius and the implosion velocity, its target the initial field.
    shell
        Declared shell dimensions the configuration does not carry.

    Returns
    -------
    ImplosionState
        The composed state.

    Raises
    ------
    DeviceConfigurationError
        If a declared input falls outside its bound; the refusals name
        the field.
    """
    liner = configuration.liner
    velocity = liner.implosion_velocity_km_s * 1.0e3
    mass = shell_mass_kg(
        liner.inner_radius_m, shell.thickness_m, shell.length_m, shell.density_kg_m3
    )
    specific = liner.specific_kinetic_energy_j_kg()
    return ImplosionState(
        inner_radius_m=liner.inner_radius_m,
        implosion_velocity_m_s=velocity,
        shell_mass_kg=mass,
        specific_kinetic_energy_j_kg=specific,
        kinetic_energy_j=mass * specific,
        characteristic_implosion_time_s=liner.inner_radius_m / velocity,
        drive_magnetic_pressure_pa=magnetic_pressure_pa(
            configuration.target.initial_field_t
        ),
    )


def require_convergence_ratio(ratio: float) -> float:
    """Return a convergence ratio strictly greater than one.

    Parameters
    ----------
    ratio
        Ratio of the initial radius to the stagnation radius.

    Returns
    -------
    float
        The validated ratio.

    Raises
    ------
    DeviceConfigurationError
        If the ratio is not strictly greater than one. A liner that does
        not converge compresses nothing, and every compression relation
        of this package divides by the compressed radius.
    """
    value = require_positive("convergence_ratio", ratio)
    if value <= 1.0:
        raise DeviceConfigurationError(
            f"convergence_ratio: must be strictly greater than one, got {value!r}"
        )
    return value
