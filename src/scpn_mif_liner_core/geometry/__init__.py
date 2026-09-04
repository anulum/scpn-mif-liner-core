# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — device geometry package

"""Device 3D and CAD models of the liner magneto-inertial family.

The mechanical envelope, the tier-G1 tessellated model and the tier-G2
B-rep model of the same five bodies: the target plasma, the liner shell,
the coaxial return conductor and the two end electrodes that drive the
axial current. Design record: ADR 0006.
"""

from __future__ import annotations

from scpn_mif_liner_core.geometry.cad import (
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    CAD_MODEL_SCHEMA_VERSION,
    CAD_MODEL_UNITS,
    DEFAULT_ANGULAR_DEFLECTION_RAD,
    DEFAULT_LINEAR_DEFLECTION_M,
    DEFAULT_REFERENCE_MESH_SEGMENTS,
    DeviceModelCAD,
    build_device_cad,
)
from scpn_mif_liner_core.geometry.device import (
    GEOMETRY_FIELDS,
    DeviceGeometry,
    geometry_from_record,
)
from scpn_mif_liner_core.geometry.model import (
    BODY_NAMES,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    MODEL_UNITS,
    DeviceModel3D,
    build_device_model,
)

__all__ = [
    "BODY_NAMES",
    "CAD_MODEL_NON_CLAIMS",
    "CAD_MODEL_SCHEMA",
    "CAD_MODEL_SCHEMA_VERSION",
    "CAD_MODEL_UNITS",
    "DEFAULT_ANGULAR_DEFLECTION_RAD",
    "DEFAULT_LINEAR_DEFLECTION_M",
    "DEFAULT_REFERENCE_MESH_SEGMENTS",
    "GEOMETRY_FIELDS",
    "MODEL_NON_CLAIMS",
    "MODEL_SCHEMA",
    "MODEL_SCHEMA_VERSION",
    "MODEL_UNITS",
    "DeviceGeometry",
    "DeviceModel3D",
    "DeviceModelCAD",
    "build_device_cad",
    "build_device_model",
    "geometry_from_record",
]
