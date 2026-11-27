# sabine-occupancy

**Put people back into an empty impulse response.**

Heritage auralization usually renders an empty room: the impulse response was
measured with nobody in it. But in a small, hard-walled space, the occupants
are often the main thing absorbing sound. `sabine.py` applies W. C. Sabine's
reverberation equation to the reverberation time you already have and answers
two questions:

- *What is the RT60 with N people in the room?* — `occupied_rt60`
- *How many people does it take to reach a target RT60?* — `solve_people`

Optionally, it reshapes the measured IR itself so you can hear the occupied
room (`presence_filter`).

One file, numpy only, pure functions. Drop `sabine.py` into your project.

```python
import sabine

t_empty = {500: 10.0}                      # measured empty RT60 per octave band (s)
sabine.occupied_rt60(t_empty, volume_m3=255_800, n_people=5000)
# {500: 7.28}
sabine.solve_people(t_empty, volume_m3=255_800, target_t=6.0)
# 8920.5 → occupants needed (a float; capacity is a separate question)
```

## Why start from a measured RT60

If you have a measured IR, its reverberation time already includes everything
in the room: surfaces, air, furnishings, the room's real modal behaviour.
`absorption_from_rt60` back-solves total absorption from it (A = 0.161·V/T),
the occupants are added, and Sabine's equation runs forward again. Only the
*increment* depends on the diffuse-field model. You need the room volume; you
do not need a surface-by-surface materials breakdown.

If you are building a room from a materials table instead, use
`absorption_from_surfaces` + `air_absorption` → `sabine_t60` / `eyring_t60`.

## Two worked examples: why the correction matters more in small rooms

**Illustration from published values — not a result.** Hagia Sophia, Istanbul:
empty RT60 ≈ 10 s at 500 Hz, volume ≈ 255,800 m³. Empty absorption is
≈ 4,100 sabins, so each occupant changes T by under 0.01 %.

| occupants | T₅₀₀ (light attire) | T₅₀₀ (modern attire) |
|---|---|---|
| 0 | 10.0 s | 10.0 s |
| 1,000 | 9.3 s | 9.0 s |
| 5,000 | 7.3 s | 6.5 s |
| 10,000 | 5.7 s | 4.8 s |

A crowd matters, but it takes thousands of people.

**King's Chamber, Great Pyramid** (Petrie survey, granite, modelled empty
T₅₀₀ = 13.95 s, V = 320.7 m³). Empty absorption is only 3.7 sabins, so each
occupant adds about 8 % to it:

| occupants | T₅₀₀ (light attire) |
|---|---|
| 0 | 13.95 s |
| 10 | 7.6 s |
| 44 | 3.0 s |
| 129 (bare-floor crush capacity) | 1.2 s |

Ten people halve the reverberation time. In a room like this, an empty-room
auralization describes a condition that may rarely have occurred.

`examples/kings_chamber_sensitivity.md` works through which assumptions those
numbers depend on. Short version: **per-person absorption dominates every
other input**. Report results under more than one per-person value.

## Take a room home

[`rooms/`](rooms/) has each of the five booth rooms as convolution-reverb impulse
responses (48 kHz, 24-bit WAV), empty and with people in them, made with this
module's `presence_filter`. Load one into Logic's Space Designer, Ableton's Hybrid
Reverb, Reaper's ReaVerb or any convolution plugin and you are playing in that room,
with that crowd. The presets are CC BY 4.0.

## Assumptions and limits

All of these are in the module docstring too.

- **Diffuse field.** Sabine's equation assumes evenly spread, exponentially
  decaying sound. It is weakest at low frequency in small rooms and in coupled
  or unevenly absorbing spaces.
- **Per-person absorption is the biggest lever.** The default octave table is a
  modern synthesis anchored so 500 Hz equals Sabine's measured 0.44
  sabins per audience member (a *seated* audience, Harvard, c. 1900). Standing
  people in other dress may absorb more or less. Pass `per_person={band: sabins}`
  when you have better data.
- **`attire="light"` is an assumption, not a measurement.** It scales the table
  by 0.70 for lighter ancient dress. Report results under `"modern"` (1.0) as well.
- **No crowd shading.** Absorption is linear in N; in dense crowds bodies shade
  each other and real absorption per person falls.
- **Capacity is a separate claim.** `capacity()` is a bare-floor upper bound
  (default 0.35 m²/person ≈ crush). The acoustic functions never clamp to it.
- **`presence_filter` changes decay rate only.** It multiplies each octave band
  by an exponential so it decays at the occupied RT60, keeping the room's fine
  structure and the direct sound. It does not model changes to early
  reflections (e.g. grazing incidence over a crowd). Per-band decay
  modification is an established technique; this applies it with a
  Sabine-derived target.

## Tests

```bash
python -m unittest -v
```

Includes hand-calculation checks, Sabine's 0.44 figure, round trips,
monotonicity, inverse checks, fail-loudly cases, `presence_filter`
reconstruction and decay-rate checks, and a regression that pins the King's
Chamber numbers published in the ASA abstract (44 / 156 / 129) — plus the
documented fact that the speech-clarity finding reverses at modern attire (110).

## Citing

- W. C. Sabine, *Collected Papers on Acoustics*, Harvard University Press,
  1922 (public domain).
- This module: see `CITATION.cff`. Presented at the 191st Meeting of the
  Acoustical Society of America, Baltimore, December 2026; a POMA paper will
  follow.

## License

MIT for the code (see `LICENSE`), CC BY 4.0 for the [reverb presets](rooms/).
Use it, change it, ship it. A citation is appreciated, not required.

Made by the Bear Branch Institute, part of [Bear Branch Sanctuary](https://bearbranch.org),
a small 501(c)(3) nonprofit. If this saves you time or ends up in your work, please
consider [a donation to the Sanctuary](https://donate.stripe.com/fZu28qdJ82rkeCD7FxfMA00).
