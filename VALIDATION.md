<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Liner Core — VALIDATION
-->

# Validation

Every gate currently active in this repository, with its exact scope,
followed by the evidence record of each implemented capability.

## Local gates

| Gate | Command | Scope |
|---|---|---|
| Lint | `ruff check .` | all Python under `src/`, `tools/`, and `tests/` |
| Format | `ruff format --check .` | same scope |
| Typing | `mypy --strict src tools tests` | zero errors, strict mode |
| Tests + coverage | `pytest -q --cov=src --cov=tools --cov-branch --cov-fail-under=100` | 100 % statement and branch coverage of `src/` and `tools/` |
| Domain manifest | `python3 tools/validate_reactor_domain.py reactor-domain.json` | schema, registry version/digest, exact configuration set, capability inventory shape and ceiling rule, safety boundary |
| Studio descriptor | `python3 tools/derive_studio_descriptor.py --check` | committed descriptor byte-identical to a fresh derivation |
| Capability inventory | `python3 tools/generate_capability_inventory.py --check` | committed inventory byte-identical to a fresh generation |
| Licensing | `reuse lint` | REUSE 3.x compliance of the full tree |
| Workflow lint | `actionlint` | all files under `.github/workflows/` |
| Workflow modularity | `python3 tools/audit_workflows.py` | distributed workflow inventory: single ownership per job, coordinator/gate contract, action pinning, size ceilings |
| Documentation | `python3 tools/preflight.py --only docs` | UTF-8 readability and relative-link integrity of every Markdown file |
| Orchestrated | `python3 tools/preflight.py` | fail-closed run of all gates above |

## Workflow gates

Definitions are present in-repository; they run on the hosted platform
only once a remote exists under separate owner authority.

The hosted surface is modular: `ci.yml` is a coordinator that carries
only trigger policy, two reusable-workflow calls, and one stable
fail-closed `gate` job aggregating every category (failure,
cancellation, and unexpected skips all fail the gate). Every job is
declared and owned exactly once in the versioned inventory
`.github/workflow-inventory.json`, which the workflow-modularity guard
verifies locally and in hosted CI.

| Workflow | Purpose |
|---|---|
| `ci.yml` | coordinator and stable required gate |
| `reusable-static-policy.yml` | lint, format, typing, domain policy, workflow guard |
| `reusable-tests.yml` | tests with complete statement and branch coverage |
| `pre-commit.yml` | exact pre-commit parity |
| `codeql.yml` | Python code scanning |
| `security-audit.yml` | secrets, dependency, licence, and workflow policy |
| `docs.yml` | strict documentation and link validation, no deployment |
| `sbom.yml` | reproducible dependency inventory, no release |
| `scorecard.yml` | read-only supply-chain analysis |

## Shared ecosystem gate

From the monorepo root:

```bash
python3 agentic-shared/scripts/repository_tier0_scaffold_audit.py \
  03_CODE/SCPN-MIF-LINER-CORE --json
```

proves the Tier-0 local-scaffold machine profile (required and forbidden
paths, Git/remote boundary, workflow pins and permissions, badge non-claims,
JSON integrity, defensive ignore rules).

## Device configuration model

Evidence record of the `device_configuration_model` capability
(`computational_prototype`; design record: `docs/adr/0002-device-configuration-model.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- Validated frozen parameter objects (`MaterialLiner`,
  `MagnetisedTarget`, `DeviceConfiguration`) rejecting non-finite
  values, non-positive extents, an unknown liner class, and a missing
  target premagnetisation (the defining property of magneto-inertial
  fusion) — every rejection branch is tested.
- The specific-kinetic-energy relation `e = v^2 / 2` as a documented
  derived quantity, with an advisory finding for implosion velocities
  beyond the slow material-liner regime ~30 km/s (LINUS-class studies;
  Moses, Krakowski & Miller, LA-7686-MS, 1979), reported and never
  clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.
- A data-only pin equality check binding the model to the SPO reactor
  registry version and digest declared in `reactor-domain.json`.

Bounded claims — what is NOT claimed:

- No parameter set describes, approximates, or validates any real
  machine; every exercised parameter set is a synthetic test fixture.
- The estimates are advisory regime checks, not compression, interface,
  or yield results; no benchmark, dataset, solver, controller, or
  experimental correlation exists in this repository.

## Diagnostic and clock semantics

Evidence record of the `diagnostic_clock_semantics` capability
(`computational_prototype`; design record: `docs/adr/0003-diagnostic-clock-semantics.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- Validated frozen declaration objects (`ClockModel`,
  `DiagnosticChannelPlan`, `DeferredCandidate`, `DiagnosticPlan`)
  rejecting catalogue misalignment: inapplicable candidates,
  inadmissible carriers, evidence-vocabulary mismatches, incompatible
  clock kinds, Nyquist violations, unresolvable event-timing bounds,
  and incomplete candidate coverage — every rejection branch is tested.
- A data-only pin (`ObservabilityBinding`) to the SPO
  observability-profile catalogue release `1.0.0`
  (`d70c0de696534e5a77066ef8420cf7ca17bc4d7321984b0ac83523dbc1dce609`),
  bound in turn to reactor registry `1.0.0`; a plan pinned to any other
  release is rejected.
- A reference plan mirroring canonical practice with synthetic
  declarations: liner-arrival train, compression trajectory, liner-asymmetry set, synthetic oscillator, each bound to its clock domain.
- Documented advisory band and timing checks with their sources stated
  in the code: the declared slow-liner asymmetry design band 1 kHz–10 MHz and µs-scale arrival-timing design bound — synthetic bounds for the ~10^2 m/s slow branch, whose split from the 10^3–10^4 m/s fast branch is documented in the LASL fast-liner assessment (LA-7686-MS 1979); findings are reported, never clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.

Bounded claims — what is NOT claimed:

- No channel describes a real diagnostic, measurement, or facility;
  every plan is a synthetic declaration of HOW evidence slots would be
  bound, marked `synthetic=True` by hard invariant.
- No SPO semantic-profile ingress is declared; the profile registry
  `ingress_state` for this device family remains `not_declared`, and
  no adapter, producer, or handoff exists in this repository.

### Portable plan envelope

The `diagnostic_clock_semantics` capability additionally exercises a
producer-owned portable envelope
(`src/scpn_mif_liner_core/plan_envelope.py`,
`scpn.reactor-diagnostic-plan-envelope.v1` version `1.0.0`): one
canonically serialised object carrying the exact project identity and
owned configurations, the capability and its maturity, the
synthetic/review-only/non-actuating statements, both SPO registry pins,
the SHA-256 digest of the inner canonical plan, the producer revision,
and fixed no-observation/no-control non-claims. The committed immutable
fixture (`tests/data/plan_envelope_fixture.json`, byte hash pinned in
the tests) is verified together with positive, tamper, wrong-project,
wrong-configuration, registry-drift, duplicate-member, and non-finite
rejection paths, all under the 100 % coverage gate. The envelope claims
nothing beyond the enveloped synthetic declaration.

### Typed frames, clock relations, and acquisition geometry

The deepened model adds typed reference frames (per-repository allowed
`FrameKind` subset; every noncyclic `coordinate_frame` binding must
reference a declared frame), clock synchronisation relations
(synthetic offset/uncertainty BOUNDS between declared non-simulation
clocks with an explicit method statement — no correlation evidence is
claimed and no clock is mapped to physical wall time), and per-channel
acquisition windows and element counts with device-cited advisory
scales. Both decoders are hardened per the SPO intake architecture:
recursive exact-key refusal in every nested entry, duplicate-member
refusal, and byte-canonical refusal (a document that is not exactly
canonical bytes is rejected). The envelope is `1.1.0`, adding
`manifest_sha256` — the SHA-256 of the committed canonical
`reactor-domain.json` — verified in tests against the committed file.
All declarations remain synthetic; nothing here observes or controls
anything.

### Signal inventories, frame transformations, and clock topology

The depth slice (envelope `1.2.0`; a `1.1.0` document is refused by the
`1.2.0` codec and vice versa — no defaults, no cross-version coercion;
`1.1.0` remains historical custody at the consumer) adds three typed
declaration surfaces, every branch under the 100 % statement-and-branch
gate:

- A per-channel **signal inventory** (`SignalDeclaration`: identifier,
  quantity, unit, role, description). Hard rules: non-empty, unique and
  sorted; exactly one `carrier`; a `timing_marker` in `"s"` exactly for
  event-relative channels and forbidden otherwise; numerical-only
  channels declare a single `phase`/`rad` carrier. Quantity and unit are
  declared tokens — no SI or UCUM validation is performed or claimed —
  and no declaration creates or overrides a candidate, carrier,
  observation, or phase: the candidate profile stays authoritative. An
  advisory flags a multi-element cyclic array without an amplitude
  signal.
- **Frame transformations** (`FrameTransformation`): the frame kinds this
  repository may declare admit no transformation pair, so the
  transformation tuple must be empty and a second frame — which could
  never be connected — is refused. The model, its admissibility table
  and its declaration-only semantics (`evidence_claimed` always `False`)
  are shared with the portfolio.
- A **clock topology** (`ClockDomain`, `ClockTopology`): every physical
  clock in exactly one domain, the simulation clock in none; a domain
  holding a facility clock is rooted there, otherwise at its shot-event
  epoch; every non-root member declares a relation to its root; every
  non-reference root declares a relation to the reference root (star);
  relations must not form a cycle. The reference plan declares one
  domain (`clk_facility` root, `clk_shot` member); multi-domain rules
  are exercised by test-constructed plans. Scopes are declarations;
  `mapping_state` stays `unmapped`.

## Level-0 device physics

Evidence record of the `level0_device_physics` capability
(`computational_prototype`; design record: `docs/adr/0005-level0-device-physics.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- **Shell mechanics.** The mass of the annular liner as the exact annulus
  `rho pi ((r + d)^2 - r^2) l`, not the thin-shell approximation: the two
  differ by `d / (2 r + d)`, which is 0.74 % at the filed design point and
  comparable to the tolerance the energy anchor is asserted at, so
  discarding it would eat most of that margin. A test asserts the
  difference is exactly that fraction. From the mass follow the kinetic
  energy at the declared velocity, the drive pressure `B^2 / 2 mu0` of the
  target's initial field, and the characteristic time `r_0 / v`, which the
  record names as a scale rather than a trajectory.
- **Flux compression** `B(r) = B_0 (r_0 / r)^2` and **adiabatic
  compression** `T(r) = T_0 (r_0 / r)^(2 (gamma - 1))`. Both are
  conservation laws in their ideal limit and both are recorded as **upper
  bounds**: a real liner has finite conductivity and loses flux, a real
  compression radiates and conducts. The non-integer power goes through
  the shared library's deterministic kernel rather than the platform's,
  and a test asserts the two are the same call.
- Every refusal branch: a radius, thickness, length, density or field that
  is zero, negative, infinite or not-a-number; a convergence ratio that
  does not converge, checked on **all three** compression relations
  because a contract enforced by only some of the functions that need it
  is not enforced; and an adiabatic index that would not heat.
- Canonical serialisation, digest identity, digest stability, and digest
  movement when the declared convergence moves.

Anchoring — and how the velocity was recovered:

- **Printed** by LA-7686-MS (Moses, Krakowski & Miller, Los Alamos, 1979),
  Table II-I, for both design points: the initial liner inner radius
  (0.2 m and 0.3 m), the initial liner thickness (3.0 mm and 4.5 mm), the
  initial azimuthal field (13.0 T for both) and the initial liner energy
  (0.336 GJ and 0.756 GJ). From the report's text: the liner is copper,
  0.2 m long, and the implosion lasts 20 to 40 microseconds.
- **The implosion velocity is not printed in a form the extraction
  preserves.** Superscripts are lost, so it reads as "10 m/s" nearly
  everywhere; one surviving sentence gives the range `10^3-10^4 m/s`. It
  was settled against the table itself: at `1e4 m/s` the kinetic energy of
  an annular copper shell of the printed radius, thickness and length
  reproduces **both** printed energies to 0.83 %, and at `1e3 m/s` it is a
  hundredfold too small. A test asserts the agreement, and a second test
  asserts that the other candidate misses — evidence is only evidence when
  the alternative fails.
- A third printed statement checks the same recovery independently: the
  characteristic time `r_0 / v` is 20 and 30 microseconds for the two
  design points, and the report's abstract brackets the implosion at 20 to
  40 microseconds.
- The energy anchor is asserted at **one per cent, not exactly**, and the
  reason is stated: the report rounds its energies to three figures and
  never prints the copper density it used.
- **Declared, and said to be declared**: the liner kind, the convergence
  ratio, the adiabatic index, and everything about the target beyond its
  initial field.

Bounded claims — what is NOT claimed:

- No equation of motion, equation of state or transport equation is
  solved; every number is a closed-form evaluation on a declared point.
- The compressed field is the perfect-conductor limit and the compressed
  temperature the loss-free limit. Both are upper bounds, never
  predictions, and the record says so in its own non-claims.
- No yield, gain, reactivity, confinement or breakeven statement is made,
  and no value describes or validates a real machine. Reproducing a
  printed number is an anchor on the arithmetic and nothing further.

## Device 3D model

Evidence record of the `device_3d_model` capability
(`computational_prototype`; design record: `docs/adr/0006-device-3d-and-cad-models.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- **Five bodies in a fixed order**, each closed and outward-oriented: the
  target plasma in the bore, the liner shell, the coaxial return conductor
  and the two end electrodes. The bodies nest the way the current path
  does, the electrodes meet the liner exactly at its ends, and each
  electrode spans the full outer radius — a feed narrower than the return
  path would not close the circuit.
- **Every derived radius is the previous one plus a declared thickness**,
  and the accessors validate the bore they are handed rather than trusting
  it. Every envelope field is refused when zero, negative, infinite or
  not-a-number, and the parser refuses an unknown key, a missing field and
  a value of the wrong type, booleans included.
- **The geometry and the physics describe one liner.** The tier-G1 liner
  volume divided by the physics capability's liner mass over its density
  is the inscribed-polygon ratio of the segment count, asserted at 8, 64
  and 512 segments to a relative tolerance of 1e-12; measured agreement is
  1e-14. The only difference between the two capabilities is the
  tessellation deficit the group already characterises.
- Canonical serialisation, digest identity, both input digests bound into
  the record, and a body set out of order refused at construction.

Anchoring — what is printed and what is declared:

- **Printed** by LA-7686-MS and recovered **from the built bodies**: the
  liner's inner radius `0.2 m` and its outer radius `0.203 m` as vertex
  coordinates of the liner mesh, and its length `0.2 m` as the mesh's
  bounding-box extent.
- **Declared, and said to be declared**: the return conductor's gap and
  thickness and the electrode thickness. The report prints nothing about
  the current return path.

## Device CAD model

Evidence record of the `device_cad_model` capability
(`computational_prototype`; same design record).

What is exercised:

- The same five bodies as exact solids, each checked fail-closed by the
  library's evidence kernel: volume and area against their analytic closed
  forms within the measure tolerance, the faceted volume within the
  chord-deficit bound, and the faceted volume against the tier-G1 mesh of
  the same design within the polygon-deficit bound.
- Every body is a cylinder or an annular tube, so each has a well-defined
  smallest circular radius and the deficit bound needs no special case
  here.
- Canonical record, pinned digest in the pinned back-end environment,
  determinism across two builds, normalised STEP bytes whose digest is the
  digest of the exported file, and refusals for a manifest of the wrong
  schema or body count, for bodies out of order, for an invalid deflection
  and for an inadmissible segment count.
- The printed liner dimensions are recovered from the measured bounding
  boxes of the solids the back-end built.

Bounded claims — what is NOT claimed:

- The geometry is the state **before** the implosion. No body moves and no
  trajectory, deformation or instability is modelled; the record says so
  in its own non-claims.
- The current path is drawn as a coaxial return and two end feeds. The
  power supply, the leads and the switching are not modelled.
- STEP determinism is claimed inside one pinned back-end environment only,
  never across back-end versions.
- No engineering model, material property, load, field, neutronic quantity
  or fabrication tolerance is carried, and no value describes or validates
  a real machine.
