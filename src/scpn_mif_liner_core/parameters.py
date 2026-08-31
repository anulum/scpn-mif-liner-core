# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — material-liner-MIF parameter model

"""Validated parameter objects of a material-liner-MIF configuration.

The derived quantity implements standard mechanics and nothing more:
the liner specific kinetic energy ``e = v^2 / 2``. It is a rough
consistency instrument with documented applicability bounds (slow-liner
regime; Moses, Krakowski & Miller, LA-7686-MS, 1979); no claim about
any real machine follows from it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

from scpn_mif_liner_core.errors import DeviceConfigurationError

LINER_KINDS: Final = ("liquid", "solid")


def require_finite(name: str, value: float) -> float:
    """Return ``value`` when finite, otherwise fail closed.

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
    DeviceConfigurationError
        If ``value`` is NaN or infinite; non-finite input is rejected,
        never clamped.
    """
    if not math.isfinite(value):
        raise DeviceConfigurationError(f"{name}: must be finite, got {value!r}")
    return value


def require_positive(name: str, value: float) -> float:
    """Return ``value`` when finite and strictly positive.

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
    DeviceConfigurationError
        If ``value`` is non-finite or not strictly positive.
    """
    require_finite(name, value)
    if value <= 0.0:
        raise DeviceConfigurationError(
            f"{name}: must be strictly positive, got {value!r}"
        )
    return value


@dataclass(frozen=True, slots=True)
class MaterialLiner:
    """Material-liner parameters of a liner-MIF configuration.

    Parameters
    ----------
    kind
        Liner class: ``solid`` (mechanical pusher) or ``liquid``
        (rotating liquid wall).
    inner_radius_m
        Initial liner inner radius in metres; strictly positive.
    implosion_velocity_km_s
        Peak implosion velocity in kilometres per second; strictly
        positive.

    Raises
    ------
    DeviceConfigurationError
        If the kind is unknown or a parameter violates its bound.
    """

    kind: str
    inner_radius_m: float
    implosion_velocity_km_s: float

    def __post_init__(self) -> None:
        """Validate the material-liner invariants.

        Raises
        ------
        DeviceConfigurationError
            If the kind is unknown or a parameter violates its bound.
        """
        if self.kind not in LINER_KINDS:
            raise DeviceConfigurationError(
                f"kind: must be one of {LINER_KINDS!r}, got {self.kind!r}"
            )
        require_positive("inner_radius_m", self.inner_radius_m)
        require_positive("implosion_velocity_km_s", self.implosion_velocity_km_s)

    def specific_kinetic_energy_j_kg(self) -> float:
        """Specific kinetic energy of the validated liner.

        Returns
        -------
        float
            ``e = v^2 / 2`` in joules per kilogram.
        """
        velocity_m_s = self.implosion_velocity_km_s * 1.0e3
        return 0.5 * velocity_m_s**2


@dataclass(frozen=True, slots=True)
class MagnetisedTarget:
    """Magnetised-target declaration of a liner-MIF configuration.

    Parameters
    ----------
    initial_field_t
        Initial embedded magnetic field in tesla; strictly positive —
        a premagnetised target is the defining property of
        magneto-inertial fusion.

    Raises
    ------
    DeviceConfigurationError
        If the field is non-finite or not strictly positive.
    """

    initial_field_t: float

    def __post_init__(self) -> None:
        """Validate the magnetised-target invariants.

        Raises
        ------
        DeviceConfigurationError
            If the field is non-finite or not strictly positive.
        """
        require_positive("initial_field_t", self.initial_field_t)
