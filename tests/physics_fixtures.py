# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — level-0 physics fixtures

"""Fixtures of the level-0 physics tests: one synthetic, two anchored.

The **reference** pair is synthetic. Its numbers are round and describe
nothing.

The **anchor** pairs are the two design points of the Fast Liner Reactor
study (R. W. Moses, R. A. Krakowski & R. L. Miller, LA-7686-MS, Los
Alamos, 1979), whose Table II-I prints both columns.

Printed by the source, and therefore anchor values:

===========================  ===========  ============
Quantity                     Low yield    High yield
===========================  ===========  ============
Initial liner inner radius   0.2 m        0.3 m
Initial liner thickness      3.0 mm       4.5 mm
Initial azimuthal field      13.0 T       13.0 T
Initial liner energy         0.336 GJ     0.756 GJ
===========================  ===========  ============

From the report's text rather than its table: the liner is **copper**, its
length is **0.2 m**, the implosion velocity is **1e4 m/s** in both cases,
and the implosion lasts **20 to 40 microseconds**.

**The velocity was recovered, not assumed.** The extraction of the report
loses superscripts, so the velocity reads as "10 m/s" nearly everywhere;
one surviving sentence gives the range ``10^3-10^4 m/s`` but not the
design point. It was settled against the table: at ``1e4 m/s`` the kinetic
energy of an annular copper shell of the printed radius, thickness and
length reproduces both printed energies to 0.8 %, where ``1e3 m/s`` is a
hundredfold too small. Two independent printed rows agreeing to under one
per cent is the evidence, and the test asserts it at that tolerance.

Declared here, and said to be declared: the liner kind and everything
about the target beyond its initial field. The source describes a
mechanical metal pusher, which is what ``solid`` names, but it does not
use this model's vocabulary.

Reproducing a printed value is an anchor, never a claim about that
machine.
"""

from __future__ import annotations

from scpn_mif_liner_core.configuration import DeviceConfiguration, RegistryBinding
from scpn_mif_liner_core.parameters import MagnetisedTarget, MaterialLiner
from scpn_mif_liner_core.physics import COPPER_DENSITY_KG_M3, ShellInputs

REGISTRY = RegistryBinding(version="1.0.0", digest_sha256="0" * 64)

#: Initial liner inner radius printed by LA-7686-MS, Table II-I.
ANCHOR_LOW_YIELD_RADIUS_M = 0.2
ANCHOR_HIGH_YIELD_RADIUS_M = 0.3
#: Initial liner thickness printed by the same table.
ANCHOR_LOW_YIELD_THICKNESS_M = 0.003
ANCHOR_HIGH_YIELD_THICKNESS_M = 0.0045
#: Initial azimuthal field printed for both design points.
ANCHOR_INITIAL_FIELD_T = 13.0
#: Initial liner energy printed for each design point, in joules.
ANCHOR_LOW_YIELD_ENERGY_J = 0.336e9
ANCHOR_HIGH_YIELD_ENERGY_J = 0.756e9
#: Implosion velocity, from the report's text; see the module docstring
#: for how the exponent the extraction lost was recovered.
ANCHOR_IMPLOSION_VELOCITY_KM_S = 10.0
#: Liner length, printed twice in the report's text.
ANCHOR_LINER_LENGTH_M = 0.2
#: Implosion duration window printed in the report's abstract, in seconds.
ANCHOR_IMPLOSION_WINDOW_S = (20.0e-6, 40.0e-6)
#: The report rounds its energies to three figures and never prints the
#: copper density it used, so the energy anchor is asserted at one per
#: cent rather than exactly. Measured agreement is 0.8 % on both rows.
ANCHOR_ENERGY_TOLERANCE = 0.01

#: Declared: the report describes a mechanical metal pusher, but does not
#: use this model's vocabulary for it.
ANCHOR_LINER_KIND = "solid"


def reference_configuration() -> DeviceConfiguration:
    """Build the synthetic reference configuration.

    Returns
    -------
    DeviceConfiguration
        A validated configuration whose numbers are round.
    """
    return DeviceConfiguration(
        identifier="mechanical_or_liquid_liner_mif",
        liner=MaterialLiner(
            kind="solid",
            inner_radius_m=0.1,
            implosion_velocity_km_s=5.0,
        ),
        target=MagnetisedTarget(initial_field_t=10.0),
        registry=REGISTRY,
    )


def reference_shell() -> ShellInputs:
    """Build the synthetic reference shell dimensions.

    Returns
    -------
    ShellInputs
        Round declared dimensions for the reference configuration.
    """
    return ShellInputs(
        thickness_m=0.002,
        length_m=0.1,
        density_kg_m3=COPPER_DENSITY_KG_M3,
    )


def anchor_configuration(*, high_yield: bool = False) -> DeviceConfiguration:
    """Build the configuration of one printed design point.

    Parameters
    ----------
    high_yield
        Select the high-yield column of Table II-I instead of the
        low-yield one.

    Returns
    -------
    DeviceConfiguration
        A validated configuration carrying the printed radius, velocity
        and field.
    """
    radius = ANCHOR_HIGH_YIELD_RADIUS_M if high_yield else ANCHOR_LOW_YIELD_RADIUS_M
    return DeviceConfiguration(
        identifier="mechanical_or_liquid_liner_mif",
        liner=MaterialLiner(
            kind=ANCHOR_LINER_KIND,
            inner_radius_m=radius,
            implosion_velocity_km_s=ANCHOR_IMPLOSION_VELOCITY_KM_S,
        ),
        target=MagnetisedTarget(initial_field_t=ANCHOR_INITIAL_FIELD_T),
        registry=REGISTRY,
    )


def anchor_shell(*, high_yield: bool = False) -> ShellInputs:
    """Build the shell dimensions of one printed design point.

    Parameters
    ----------
    high_yield
        Select the high-yield column of Table II-I.

    Returns
    -------
    ShellInputs
        The printed thickness and length with the copper density the
        report names.
    """
    thickness = (
        ANCHOR_HIGH_YIELD_THICKNESS_M if high_yield else ANCHOR_LOW_YIELD_THICKNESS_M
    )
    return ShellInputs(
        thickness_m=thickness,
        length_m=ANCHOR_LINER_LENGTH_M,
        density_kg_m3=COPPER_DENSITY_KG_M3,
    )
