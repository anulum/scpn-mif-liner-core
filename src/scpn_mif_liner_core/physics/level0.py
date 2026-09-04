# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — level-0 physics record

"""Level-0 physics record of one validated liner-MIF configuration.

The record composes the two closed forms this package implements — the
mechanical state of the driven shell and what its convergence does to the
field and the plasma — on a validated configuration together with the
inputs the configuration does not carry, and serialises canonically with a
SHA-256 digest.

Every number in it is a closed-form evaluation on a declared operating
point at ``computational_prototype`` maturity. Two of the relations are
conservation laws taken in their ideal limit and are upper bounds rather
than predictions: a real liner has finite conductivity and loses flux, and
a real compression radiates and conducts.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_mif_liner_core.configuration import DeviceConfiguration
from scpn_mif_liner_core.physics.compression import (
    MONATOMIC_GAMMA,
    CompressionState,
    compression_state,
)
from scpn_mif_liner_core.physics.implosion import (
    ImplosionState,
    ShellInputs,
    implosion_state,
    require_convergence_ratio,
)

LEVEL0_SCHEMA: Final = "scpn.mif-liner-level0-physics.v1"
LEVEL0_SCHEMA_VERSION: Final = "1.0.0"
LEVEL0_NON_CLAIMS: Final = (
    (
        "closed-form evaluation of shell mechanics and ideal compression on a "
        "declared operating point"
    ),
    "no equation of motion, equation of state or transport equation is solved",
    (
        "the compressed field is the perfect-conductor limit and the compressed "
        "temperature the loss-free limit; both are upper bounds, never predictions"
    ),
    "no yield, gain, reactivity, confinement or breakeven statement",
    (
        "no value describes or validates any real machine; an anchor reproduces "
        "a number the filed source prints and nothing further"
    ),
)


@dataclass(frozen=True, slots=True)
class Level0Physics:
    """Composed level-0 record of one configuration and its inputs.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the configuration the record was built from.
    shell
        Declared shell dimensions.
    implosion
        Mechanical state of the shell.
    compression
        What the declared convergence does to the field and the plasma.
    """

    configuration_digest_sha256: str
    shell: ShellInputs
    implosion: ImplosionState
    compression: CompressionState

    def to_record(self) -> dict[str, Any]:
        """Project the record to a JSON-serialisable object.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with its non-claims.
        """
        return {
            "schema": LEVEL0_SCHEMA,
            "schema_version": LEVEL0_SCHEMA_VERSION,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "shell": self.shell.to_record(),
            "implosion": self.implosion.to_record(),
            "compression": self.compression.to_record(),
            "non_claims": list(LEVEL0_NON_CLAIMS),
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def level0_physics(
    configuration: DeviceConfiguration,
    shell: ShellInputs,
    convergence_ratio: float,
    adiabatic_index: float = MONATOMIC_GAMMA,
) -> Level0Physics:
    """Compose the level-0 physics record of one validated configuration.

    Parameters
    ----------
    configuration
        Validated device configuration.
    shell
        Declared shell dimensions the configuration does not carry.
    convergence_ratio
        Declared ``r_0 / r`` at stagnation; strictly greater than one.
    adiabatic_index
        ``gamma`` of the compressed plasma; strictly greater than one.

    Returns
    -------
    Level0Physics
        The composed record.

    Raises
    ------
    DeviceConfigurationError
        If a declared input or a derived quantity falls outside its
        model bound; the refusals of the composed relations are raised
        unchanged, with the field they name.
    """
    ratio = require_convergence_ratio(convergence_ratio)
    return Level0Physics(
        configuration_digest_sha256=configuration.digest_sha256(),
        shell=shell,
        implosion=implosion_state(configuration, shell),
        compression=compression_state(
            configuration.target.initial_field_t,
            configuration.liner.inner_radius_m,
            ratio,
            adiabatic_index,
        ),
    )
