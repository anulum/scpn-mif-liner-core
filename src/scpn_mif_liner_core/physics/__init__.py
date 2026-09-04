# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — level-0 device physics package

"""Level-0 device physics of the liner magneto-inertial family.

Two closed forms on the validated configuration: the mechanical state of
the driven annular shell — its mass, kinetic energy, characteristic
implosion time and drive pressure — and what its convergence does to the
field and the plasma it encloses, by flux conservation and by adiabatic
compression. Both compression relations are ideal limits and are recorded
as upper bounds. No equation is solved and no value describes a real
machine. Design record: ADR 0005.
"""

from __future__ import annotations

from scpn_mif_liner_core.physics.compression import (
    MONATOMIC_GAMMA,
    CompressionState,
    adiabatic_temperature_ratio,
    compressed_density_ratio,
    compressed_field_t,
    compression_state,
)
from scpn_mif_liner_core.physics.implosion import (
    ALUMINIUM_DENSITY_KG_M3,
    COPPER_DENSITY_KG_M3,
    MU0,
    ImplosionState,
    ShellInputs,
    implosion_state,
    magnetic_pressure_pa,
    require_convergence_ratio,
    shell_mass_kg,
)
from scpn_mif_liner_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    Level0Physics,
    level0_physics,
)

__all__ = [
    "ALUMINIUM_DENSITY_KG_M3",
    "COPPER_DENSITY_KG_M3",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "MONATOMIC_GAMMA",
    "MU0",
    "CompressionState",
    "ImplosionState",
    "Level0Physics",
    "ShellInputs",
    "adiabatic_temperature_ratio",
    "compressed_density_ratio",
    "compressed_field_t",
    "compression_state",
    "implosion_state",
    "level0_physics",
    "magnetic_pressure_pa",
    "require_convergence_ratio",
    "shell_mass_kg",
]
