# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — flux and adiabatic compression

"""What a converging liner does to the field and the plasma inside it.

Magneto-inertial fusion is defined by the field the target carries before
the liner arrives, so the relations that matter at level zero are the ones
that say what convergence does to it.

Two closed forms, each a conservation law and nothing more.

**Flux compression.** A perfectly conducting cylindrical shell traps the
axial flux it encloses, so ``B pi r^2`` is constant and
``B(r) = B_0 (r_0 / r)^2``. The perfect-conductor limit is an idealisation
and is named as one: a real liner has finite conductivity and loses flux,
so this is an upper bound on the compressed field, never a prediction of
it.

**Adiabatic compression.** A cylindrical compression of a plasma that
loses no heat raises the number density as ``(r_0 / r)^2`` and the
temperature as ``n^(gamma - 1)``, giving
``T(r) = T_0 (r_0 / r)^(2 (gamma - 1))``. With the monatomic
``gamma = 5/3`` that is ``(r_0 / r)^(4/3)``. Losing no heat is also an
idealisation, and also an upper bound.

Both are evaluated through the shared library's deterministic ``power``
kernel rather than the platform's, because a non-integer exponent is a
transcendental and the group's numbers are reproducible across back-ends.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.errors import NumericsError
from scpn_reactor_kernels.numerics.transcendental import power

from scpn_mif_liner_core.errors import DeviceConfigurationError
from scpn_mif_liner_core.parameters import require_positive
from scpn_mif_liner_core.physics.implosion import require_convergence_ratio

#: Adiabatic index of a monatomic ideal gas.
MONATOMIC_GAMMA: Final = 5.0 / 3.0


def compressed_field_t(initial_field_t: float, convergence_ratio: float) -> float:
    """Return the field after a perfectly flux-conserving compression.

    Parameters
    ----------
    initial_field_t
        Field before the implosion; strictly positive.
    convergence_ratio
        ``r_0 / r``; strictly greater than one.

    Returns
    -------
    float
        ``B_0 (r_0 / r)^2``. An upper bound: a real liner has finite
        conductivity and loses flux.

    Raises
    ------
    DeviceConfigurationError
        If the field or the ratio falls outside its bound.
    """
    field = require_positive("initial_field_t", initial_field_t)
    ratio = require_convergence_ratio(convergence_ratio)
    return field * ratio * ratio


def compressed_density_ratio(convergence_ratio: float) -> float:
    """Return the density gain of a cylindrical compression.

    Parameters
    ----------
    convergence_ratio
        ``r_0 / r``; strictly greater than one.

    Returns
    -------
    float
        ``(r_0 / r)^2``: the area ratio, because a cylindrical
        compression conserves the number per unit length.

    Raises
    ------
    DeviceConfigurationError
        If the ratio is not strictly greater than one.
    """
    ratio = require_convergence_ratio(convergence_ratio)
    return ratio * ratio


def adiabatic_temperature_ratio(
    convergence_ratio: float, adiabatic_index: float = MONATOMIC_GAMMA
) -> float:
    """Return the temperature gain of an adiabatic cylindrical compression.

    Parameters
    ----------
    convergence_ratio
        ``r_0 / r``; strictly greater than one.
    adiabatic_index
        ``gamma``; strictly greater than one, or the compression would
        not heat.

    Returns
    -------
    float
        ``(r_0 / r)^(2 (gamma - 1))``, evaluated through the shared
        library's deterministic power kernel. An upper bound: a real
        compression radiates and conducts.

    Raises
    ------
    DeviceConfigurationError
        If the ratio or the index falls outside its bound, or if the
        power leaves the kernel's admissible range; the kernel's refusal
        is re-raised under the device error type with its message.
    """
    ratio = require_convergence_ratio(convergence_ratio)
    index = require_positive("adiabatic_index", adiabatic_index)
    if index <= 1.0:
        raise DeviceConfigurationError(
            f"adiabatic_index: must be strictly greater than one, got {index!r}"
        )
    try:
        return power(ratio, 2.0 * (index - 1.0))
    except NumericsError as exc:
        raise DeviceConfigurationError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class CompressionState:
    """What one declared convergence does to the field and the plasma.

    Parameters
    ----------
    convergence_ratio
        ``r_0 / r`` of the declared stagnation radius.
    stagnation_radius_m
        The radius the ratio corresponds to.
    adiabatic_index
        ``gamma`` used for the temperature gain.
    compressed_field_t
        ``B_0 (r_0 / r)^2``.
    field_gain
        ``(r_0 / r)^2``.
    density_gain
        ``(r_0 / r)^2``: the same factor, for the same reason — both are
        the area ratio of a cylindrical compression.
    temperature_gain
        ``(r_0 / r)^(2 (gamma - 1))``.
    """

    convergence_ratio: float
    stagnation_radius_m: float
    adiabatic_index: float
    compressed_field_t: float
    field_gain: float
    density_gain: float
    temperature_gain: float

    def to_record(self) -> dict[str, Any]:
        """Project the state to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per field, in the declaration order of the class.
        """
        return {
            "convergence_ratio": self.convergence_ratio,
            "stagnation_radius_m": self.stagnation_radius_m,
            "adiabatic_index": self.adiabatic_index,
            "compressed_field_t": self.compressed_field_t,
            "field_gain": self.field_gain,
            "density_gain": self.density_gain,
            "temperature_gain": self.temperature_gain,
        }


def compression_state(
    initial_field_t: float,
    inner_radius_m: float,
    convergence_ratio: float,
    adiabatic_index: float = MONATOMIC_GAMMA,
) -> CompressionState:
    """Compose the compression state of one declared convergence.

    Parameters
    ----------
    initial_field_t
        Field before the implosion; strictly positive.
    inner_radius_m
        Initial liner inner radius; strictly positive.
    convergence_ratio
        ``r_0 / r``; strictly greater than one.
    adiabatic_index
        ``gamma``; strictly greater than one.

    Returns
    -------
    CompressionState
        The composed state.

    Raises
    ------
    DeviceConfigurationError
        If any argument falls outside its bound.
    """
    radius = require_positive("inner_radius_m", inner_radius_m)
    ratio = require_convergence_ratio(convergence_ratio)
    gain = compressed_density_ratio(ratio)
    return CompressionState(
        convergence_ratio=ratio,
        stagnation_radius_m=radius / ratio,
        adiabatic_index=adiabatic_index,
        compressed_field_t=compressed_field_t(initial_field_t, ratio),
        field_gain=gain,
        density_gain=gain,
        temperature_gain=adiabatic_temperature_ratio(ratio, adiabatic_index),
    )
