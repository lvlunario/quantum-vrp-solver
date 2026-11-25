# Metamorphic fault routing extension

**SIMULATED NARRATIVE:** this extension belongs to an independent personal
project in a Norway setting, without a host institution. The Inria-style role
discussion is fictional. No real person, institution, meeting, review or
submission participated.

## Purpose

P01 and P02 now have executed bounded development evidence, but that does not
make every nearby transformation a valid mutant. This extension records eight
application/metamorphic faults and assigns the minimum boundary expected to
reject or expose each one. It is separate from the frozen M01–M12 mutation
pilot and does not alter or execute that protocol.

| ID | Fault | Minimum detecting layer | Evidence status |
|---|---|---|---|
| MF01 | Negative demand admitted to P01 | G0 transform precondition | Confirmed by retained P01 rejected control |
| MF02 | Capacity changes across a P01 pair | G0 transform precondition | Confirmed by retained P01 rejected control |
| MF03 | Physical P01 promoted to auxiliary equality | L4 auxiliary-boundary oracle | Confirmed by both auxiliary transition directions with zero physical P01 violations |
| MF04 | Decision-only coordinate permutation | G0 transform precondition | Confirmed by retained P02 material control |
| MF05 | Demand-only coordinate permutation | G0 transform precondition | Confirmed by retained P02 material control |
| MF06 | Duplicate or missing coordinate accepted as a permutation | G0 transform precondition | Prospective route; fault not executed |
| MF07 | Physical and auxiliary validity collapsed | L4 metric-separation oracle | Confirmed by the 40-versus-5 verdict separation and 35 physical-only states |
| MF08 | Physical P02 promoted to auxiliary, QUBO or circuit invariance | G0 scope contract | Prospective route; fault not executed |

## Validation result

The catalog validator executed nine checks against four retained evidence
files. It confirmed six existing-evidence routes, preserved two prospective
routes as explicitly unexecuted, verified eight unique identifiers and the
P01/P02/application coverage, restricted layer names, and enforced a zero
resource boundary with no mutation-pilot overlap.

Six deliberately invalid catalogs were rejected: duplicate identity, unknown
layer, pilot overlap, nonzero mutant count, missing evidence and a false
execution claim. A separate parse confirmed all checks and mutation rejections.
No catalog fault or scientific mutant was executed.

## Fictional discussion decision

**SIMULATED NARRATIVE:** an Inria-style software-testing role challenged the
initial idea of calling all eight items “mutants.” The distinction matters:
MF01, MF02, MF04, MF05 and MF06 violate transformation preconditions, while
MF03, MF07 and MF08 are interpretation or layer-promotion faults. The decision
was to retain one catalog but record the minimum detecting boundary and
evidence status explicitly. No real collaborator participated.

## Boundaries and next step

Catalog validation is not a mutation score. It does not show how often a test
suite kills implemented faults, and it does not authorize M01–M12. MF06 and
MF08 remain routed but unexecuted. The next useful work is to freeze a small
schema for fault class, precondition, detecting layer, blind layer and evidence
status, then test the schema using synthetic catalog records—not to start the
blocked scientific pilot.
