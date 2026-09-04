# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — device geometry fixtures

"""Fixtures of the device-model tests: one synthetic, one anchored.

The **reference** pair is synthetic and describes nothing.

The **anchor** pair uses the liner dimensions LA-7686-MS prints — the
inner radius, the wall thickness and the length — and declares everything
outside the liner, because the report prints nothing about the return
conductor or the electrodes.

The printed liner dimensions live in :mod:`physics_fixtures`, which is
their one home; this module imports them rather than restating them.

Reproducing a printed dimension is an anchor, never a claim about that
machine.
"""

from __future__ import annotations

from physics_fixtures import (
    ANCHOR_LINER_LENGTH_M,
    ANCHOR_LOW_YIELD_THICKNESS_M,
    anchor_configuration,
)

from scpn_mif_liner_core.configuration import DeviceConfiguration
from scpn_mif_liner_core.geometry.device import DeviceGeometry

#: Declared: the report prints nothing about the current return path.
ANCHOR_RETURN_GAP_M = 0.02
ANCHOR_RETURN_THICKNESS_M = 0.01
#: Declared: the report prints no electrode thickness.
ANCHOR_ELECTRODE_THICKNESS_M = 0.005

#: Segment count of the reference tessellation.
REFERENCE_SEGMENTS = 64


def reference_configuration() -> DeviceConfiguration:
    """Build the synthetic reference configuration.

    Returns
    -------
    DeviceConfiguration
        A validated configuration whose numbers are round.
    """
    from physics_fixtures import reference_configuration as base

    return base()


def reference_geometry() -> DeviceGeometry:
    """Build the synthetic reference envelope.

    Returns
    -------
    DeviceGeometry
        A validated envelope with round dimensions.
    """
    return DeviceGeometry(
        liner_thickness_m=0.002,
        liner_length_m=0.1,
        return_conductor_gap_m=0.01,
        return_conductor_thickness_m=0.005,
        electrode_thickness_m=0.004,
    )


def anchor_geometry() -> DeviceGeometry:
    """Build the envelope anchored on the printed liner dimensions.

    Returns
    -------
    DeviceGeometry
        The printed liner wall and length, with the current path
        declared.
    """
    return DeviceGeometry(
        liner_thickness_m=ANCHOR_LOW_YIELD_THICKNESS_M,
        liner_length_m=ANCHOR_LINER_LENGTH_M,
        return_conductor_gap_m=ANCHOR_RETURN_GAP_M,
        return_conductor_thickness_m=ANCHOR_RETURN_THICKNESS_M,
        electrode_thickness_m=ANCHOR_ELECTRODE_THICKNESS_M,
    )


__all__ = [
    "ANCHOR_ELECTRODE_THICKNESS_M",
    "ANCHOR_RETURN_GAP_M",
    "ANCHOR_RETURN_THICKNESS_M",
    "REFERENCE_SEGMENTS",
    "anchor_configuration",
    "anchor_geometry",
    "reference_configuration",
    "reference_geometry",
]
