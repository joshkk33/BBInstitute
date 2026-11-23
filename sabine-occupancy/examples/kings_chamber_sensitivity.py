"""King's Chamber: how robust is "the chamber cannot be made conversational"?

The ASA 191st abstract claims T500 = 1 s needs 156 occupants against a
bare-floor crush capacity of 129. This script asks which input that verdict
actually rests on. Uses only sabine.py. Writes a markdown report to stdout.

    python examples/kings_chamber_sensitivity.py > examples/kings_chamber_sensitivity.md
"""

import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import sabine  # noqa: E402

L, W, H = 10.47, 5.234, 5.852           # Petrie survey
FLOOR, PERIM = L * W, 2 * (L + W)
V, S = FLOOR * H, 2 * FLOOR + PERIM * H
K = sabine.sabine_constant()
A_AIR_500 = sabine.air_absorption(V)[500]
SPEECH, CHANT = 1.0, 3.0
SABINE_A = sabine.PERSON_SABINS[500]     # 0.44, Sabine's measured audience figure


def a_empty(alpha500, volume=V, surface=S):
    return alpha500 * surface + 4 * sabine.AIR_M[500] * volume


def people_for(target, alpha500=0.01, a_person=SABINE_A * 0.7, volume=V, surface=S):
    t_empty = {500: K * volume / a_empty(alpha500, volume, surface)}
    return sabine.solve_people(t_empty, volume, target, per_person={500: a_person})


def cap(m2_per_person=0.35):
    return math.floor(sabine.capacity(FLOOR, PERIM, m2_per_person))   # whole people


def main():
    out = []
    p = out.append
    c35 = cap(0.35)
    p("# King's Chamber — sensitivity of the speech-clarity finding\n")
    p(f"Geometry (Petrie): V = {V:.1f} m³, S = {S:.1f} m², floor = {FLOOR:.1f} m², "
      f"usable floor (0.3 m edge strip) = {FLOOR - 0.3 * PERIM:.1f} m².  ")
    p(f"Empty absorption at 500 Hz, granite α = 0.01: A = {a_empty(0.01):.2f} sabins "
      f"(surfaces {0.01 * S:.2f} + air {A_AIR_500:.2f}) → T₅₀₀ = {K * V / a_empty(0.01):.2f} s.  ")
    p(f"Absorption needed for T₅₀₀ = 1 s: k·V/1 = **{K * V:.1f} sabins** — "
      f"the empty room supplies {a_empty(0.01) / (K * V):.0%} of it; occupants must supply the rest.\n")

    p("## 1. The verdict is a statement about per-person absorption\n")
    p("Because the empty room contributes almost nothing, `people for speech ≈ 51.7 / a`, "
      "where *a* is absorption per occupant at 500 Hz. The verdict flips when that count "
      "drops below capacity.\n")
    p("| capacity assumption | capacity | break-even *a* (sabins/person @500 Hz) |")
    p("|---|---|---|")
    for d, label in [(0.35, "crush, 0.35 m²/p (abstract)"), (0.42, "0.42 m²/p"),
                     (0.50, "0.50 m²/p"), (0.65, "loose assembly, 0.65 m²/p")]:
        c = cap(d)
        a_star = (K * V - a_empty(0.01)) / c
        p(f"| {label} | {c:.0f} | **{a_star:.3f}** |")
    a_star = (K * V - a_empty(0.01)) / c35
    p(f"\nReference points: Sabine's measured seated audience = 0.44; "
      f"`attire=\"light\"` (0.70×) = {0.44 * 0.7:.3f}. "
      f"**The abstract's finding holds only if a standing occupant absorbs less than "
      f"{a_star:.2f} sabins at 500 Hz** — i.e. less than {a_star / 0.44:.0%} of Sabine's own figure.\n")

    p("## 2. People needed for speech (T₅₀₀ = 1 s), per-person × granite α\n")
    alphas = [0.01, 0.02, 0.03]
    persons = [(0.308, "light 0.70× (abstract)"), (0.35, ""), (a_star, "break-even"),
               (0.44, "Sabine / modern 1.0×"), (0.50, ""), (0.60, "")]
    p("| *a* @500 Hz | " + " | ".join(f"α={a}" for a in alphas) + f" | verdict vs crush capacity {c35:.0f} |")
    p("|---|" + "---|" * len(alphas) + "---|")
    for a, label in persons:
        row = [people_for(SPEECH, al, a) for al in alphas]
        verdict = "cannot reach speech" if row[0] > c35 else "**can** reach speech"
        lab = f"{a:.3f}" + (f" ({label})" if label else "")
        p(f"| {lab} | " + " | ".join(f"{math.ceil(n)}" for n in row) + f" | {verdict} (at α=0.01) |")
    p("\nGranite α moves the count by ~10 people across its published range; "
      "per-person absorption moves it by ~70. α is the second-order input.\n")

    alpha_flip_light = (K * V - 4 * sabine.AIR_M[500] * V - c35 * 0.308) / S
    p(f"Break-even granite α₅₀₀ at light attire: **{alpha_flip_light:.3f}** "
      f"(published dressed granite ≈ 0.01–0.02). At modern attire the finding is already "
      "reversed at α = 0.01, so no α break-even exists on that branch.\n")

    p("## 3. Chant (T₅₀₀ = 3 s) is robust\n")
    p("| *a* @500 Hz | people for chant |")
    p("|---|---|")
    for a in (0.308, 0.44, 0.60):
        p(f"| {a:.3f} | {math.ceil(people_for(CHANT, 0.01, a))} |")
    p("\nEvery plausible per-person value puts chant-length reverberation within capacity.\n")

    p("## 4. Cross-check: audience-area method\n")
    p("Beranek-style practice treats a dense audience as an absorbing *area*, not a count. "
      "Treating the packed crowd as a surface covering the usable floor "
      f"({FLOOR - 0.3 * PERIM:.1f} m²), optionally plus a 0.5 m edge strip "
      "around the crowd block for exposed sides:\n")
    usable = FLOOR - 0.3 * PERIM
    crowd_perim = 2 * ((L - 0.6) + (W - 0.6))
    p("| crowd α₅₀₀ | T₅₀₀, top surface only | T₅₀₀, + edge strip |")
    p("|---|---|---|")
    for ac in (0.6, 0.75, 0.9, 1.0):
        a_room = a_empty(0.01) - 0.01 * usable          # crowd covers that floor
        t1 = K * V / (a_room + ac * usable)
        t2 = K * V / (a_room + ac * (usable + 0.5 * crowd_perim))
        p(f"| {ac:.2f} | {t1:.2f} s | {t2:.2f} s |")
    p("\nCaveat: the published audience-area coefficients come from *seated* audiences in "
      "upholstered seats; a standing crowd on stone is a different absorber. Without the "
      "edge term the area method agrees with the abstract (speech unreachable even at "
      "α = 1); with it, the verdict is borderline. Treat as a cross-check, not a result.\n")

    p("## 5. Monte Carlo — P(people for speech > crush capacity)\n")
    rng = np.random.default_rng(20261206)
    n = 100_000
    dim = rng.normal(1, 0.01, (n, 3))                    # surveyed: ±1 % (1σ)
    l, w, h = L * dim[:, 0], W * dim[:, 1], H * dim[:, 2]
    vol, surf = l * w * h, 2 * (l * w + l * h + w * h)
    capn = np.floor((l * w - 0.3 * 2 * (l + w)) / 0.35)
    alpha = rng.uniform(0.01, 0.03, n)
    a0 = alpha * surf + 4 * sabine.AIR_M[500] * vol
    priors = {
        "attire fixed light (abstract)": np.full(n, 0.308),
        "attire uniform light…modern (0.308–0.44)": rng.uniform(0.308, 0.44, n),
        "per-person uniform 0.25–0.60 (agnostic standing)": rng.uniform(0.25, 0.60, n),
        "attire fixed modern (Sabine 0.44)": np.full(n, 0.44),
    }
    p(f"{n:,} draws, seed 20261206. Dimensions ±1 % (1σ, surveyed tier), granite α₅₀₀ "
      "uniform 0.01–0.03, capacity held at crush density (the assumption *least* "
      "favourable to the finding). Only the per-person prior changes between rows.\n")
    p("| per-person prior | median people for speech | P(finding holds) |")
    p("|---|---|---|")
    for name, a in priors.items():
        need = (K * vol - a0) / a
        p(f"| {name} | {np.median(need):.0f} | **{np.mean(need > capn):.0%}** |")
    p("\nThe probability is set almost entirely by the per-person prior. Geometry and "
      "granite uncertainty, at the surveyed tier, do not move it. **The confidence one can "
      "state for the finding is the confidence one has that a standing occupant absorbed "
      f"under ~{a_star:.2f} sabins at 500 Hz.**\n")

    p("## What this means for the poster\n")
    p("- Chant-length reverberation (T₅₀₀ ≈ 3 s) at 31–44 occupants: robust under every "
      "assumption tested.")
    p(f"- \"Cannot be made conversational at any physical occupancy\" is **conditional**: "
      f"it holds if per-person absorption < {a_star:.2f} sabins at 500 Hz, and reverses at "
      "Sabine's own unscaled 0.44. The 0.70 attire factor is the input carrying the verdict.")
    p("- Granite α (the parameter the poster handoff singled out) is second-order: "
      f"break-even ≈ {alpha_flip_light:.3f} at light attire.")
    p("- Suggested phrasing: *\"Speech clarity (T₅₀₀ = 1 s) requires 110–156 occupants "
      f"depending on assumed per-person absorption, against a crush capacity of {c35:.0f}: "
      "the chamber reaches conversational reverberation only near crush density, "
      f"and not at all if a standing occupant absorbs less than ~{a_star:.2f} sabins at "
      "500 Hz (84 % of Sabine's seated-audience figure).\"*")
    print("\n".join(out))


if __name__ == "__main__":
    main()
