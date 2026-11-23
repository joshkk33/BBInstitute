# King's Chamber — sensitivity of the speech-clarity finding

Geometry (Petrie): V = 320.7 m³, S = 293.4 m², floor = 54.8 m², usable floor (0.3 m edge strip) = 45.4 m².  
Empty absorption at 500 Hz, granite α = 0.01: A = 3.70 sabins (surfaces 2.93 + air 0.77) → T₅₀₀ = 13.95 s.  
Absorption needed for T₅₀₀ = 1 s: k·V/1 = **51.7 sabins** — the empty room supplies 7% of it; occupants must supply the rest.

## 1. The verdict is a statement about per-person absorption

Because the empty room contributes almost nothing, `people for speech ≈ 51.7 / a`, where *a* is absorption per occupant at 500 Hz. The verdict flips when that count drops below capacity.

| capacity assumption | capacity | break-even *a* (sabins/person @500 Hz) |
|---|---|---|
| crush, 0.35 m²/p (abstract) | 129 | **0.372** |
| 0.42 m²/p | 108 | **0.444** |
| 0.50 m²/p | 90 | **0.533** |
| loose assembly, 0.65 m²/p | 69 | **0.695** |

Reference points: Sabine's measured seated audience = 0.44; `attire="light"` (0.70×) = 0.308. **The abstract's finding holds only if a standing occupant absorbs less than 0.37 sabins at 500 Hz** — i.e. less than 85% of Sabine's own figure.

## 2. People needed for speech (T₅₀₀ = 1 s), per-person × granite α

| *a* @500 Hz | α=0.01 | α=0.02 | α=0.03 | verdict vs crush capacity 129 |
|---|---|---|---|---|
| 0.308 (light 0.70× (abstract)) | 156 | 147 | 137 | cannot reach speech (at α=0.01) |
| 0.350 | 138 | 129 | 121 | cannot reach speech (at α=0.01) |
| 0.372 (break-even) | 129 | 122 | 114 | **can** reach speech (at α=0.01) |
| 0.440 (Sabine / modern 1.0×) | 110 | 103 | 96 | **can** reach speech (at α=0.01) |
| 0.500 | 96 | 91 | 85 | **can** reach speech (at α=0.01) |
| 0.600 | 80 | 76 | 71 | **can** reach speech (at α=0.01) |

Granite α moves the count by ~10 people across its published range; per-person absorption moves it by ~70. α is the second-order input.

Break-even granite α₅₀₀ at light attire: **0.038** (published dressed granite ≈ 0.01–0.02). At modern attire the finding is already reversed at α = 0.01, so no α break-even exists on that branch.

## 3. Chant (T₅₀₀ = 3 s) is robust

| *a* @500 Hz | people for chant |
|---|---|
| 0.308 | 44 |
| 0.440 | 31 |
| 0.600 | 23 |

Every plausible per-person value puts chant-length reverberation within capacity.

## 4. Cross-check: audience-area method

Beranek-style practice treats a dense audience as an absorbing *area*, not a count. Treating the packed crowd as a surface covering the usable floor (45.4 m²), optionally plus a 0.5 m edge strip around the crowd block for exposed sides:

| crowd α₅₀₀ | T₅₀₀, top surface only | T₅₀₀, + edge strip |
|---|---|---|
| 0.60 | 1.70 s | 1.32 s |
| 0.75 | 1.39 s | 1.07 s |
| 0.90 | 1.17 s | 0.90 s |
| 1.00 | 1.06 s | 0.82 s |

Caveat: the published audience-area coefficients come from *seated* audiences in upholstered seats; a standing crowd on stone is a different absorber. Without the edge term the area method agrees with the abstract (speech unreachable even at α = 1); with it, the verdict is borderline. Treat as a cross-check, not a result.

## 5. Monte Carlo — P(people for speech > crush capacity)

100,000 draws, seed 20261206. Dimensions ±1 % (1σ, surveyed tier), granite α₅₀₀ uniform 0.01–0.03, capacity held at crush density (the assumption *least* favourable to the finding). Only the per-person prior changes between rows.

| per-person prior | median people for speech | P(finding holds) |
|---|---|---|
| attire fixed light (abstract) | 146 | **100%** |
| attire uniform light…modern (0.308–0.44) | 121 | **31%** |
| per-person uniform 0.25–0.60 (agnostic standing) | 106 | **28%** |
| attire fixed modern (Sabine 0.44) | 102 | **0%** |

The probability is set almost entirely by the per-person prior. Geometry and granite uncertainty, at the surveyed tier, do not move it. **The confidence one can state for the finding is the confidence one has that a standing occupant absorbed under ~0.37 sabins at 500 Hz.**

## What this means for the poster

- Chant-length reverberation (T₅₀₀ ≈ 3 s) at 31–44 occupants: robust under every assumption tested.
- "Cannot be made conversational at any physical occupancy" is **conditional**: it holds if per-person absorption < 0.37 sabins at 500 Hz, and reverses at Sabine's own unscaled 0.44. The 0.70 attire factor is the input carrying the verdict.
- Granite α (the parameter the poster handoff singled out) is second-order: break-even ≈ 0.038 at light attire.
- Suggested phrasing: *"Speech clarity (T₅₀₀ = 1 s) requires 110–156 occupants depending on assumed per-person absorption, against a crush capacity of 129: the chamber reaches conversational reverberation only near crush density, and not at all if a standing occupant absorbs less than ~0.37 sabins at 500 Hz (84 % of Sabine's seated-audience figure)."*
