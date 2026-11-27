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

# Hagia Sophia, measured empty (Pentcheva 2017): RT60 per octave band, seconds
t_empty = {250: 12.0, 500: 12.0, 1000: 10.0, 2000: 8.0}
sabine.occupied_rt60(t_empty, volume_m3=255_800, n_people=5000)
# {250: 8.98, 500: 8.28, 1000: 7.1, 2000: 5.97}
sabine.solve_people(t_empty, volume_m3=255_800, target_t=6.0)
# 11150.7 → occupants needed at 500 Hz (a float; capacity is a separate question)
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
measured empty RT60 about 12 s at 250–500 Hz, 10 s at 1 kHz and 8 s at 2 kHz,
volume 255,800 m³ (Pentcheva, *Hagia Sophia: Sound, Space, and Spirit in
Byzantium*, 2017, pp. 102–4; Icons of Sound, Stanford CCRMA). Empty absorption
is about 3,400 sabins at 500 Hz, so each occupant changes T by about 0.01 %.

| occupants | T₅₀₀ (packed crowd, 0.31/person) | T₅₀₀ (seated audience, 0.44/person) |
|---|---|---|
| 0 | 12.0 s | 12.0 s |
| 1,000 | 11.0 s | 10.6 s |
| 5,000 | 8.3 s | 7.3 s |
| 10,000 | 6.3 s | 5.3 s |

A crowd matters, but it takes thousands of people; T₅₀₀ = 1 s would need about
120,000.

*Prior work:* Weitze, Rindel, Christensen & Gade (Forum Acusticum 2002, EU
CAHRISMA project) simulated the Byzantine church in ODEON, including a version
with an audience: T30,mid 10.5 s → 8.4 s (odeon.dk). In Sabine terms that audience
is roughly 2,000–2,900 people. Simulation tools can model a congregation directly;
this module is for the other case, an impulse response **measured** empty, which
is the only time anyone fires a balloon in a monument.

**King's Chamber, Great Pyramid** (Petrie survey, granite, modelled empty
T₅₀₀ = 13.95 s, V = 320.7 m³). Empty absorption is only 3.7 sabins, so each
occupant adds about 8 % to it:

| occupants | T₅₀₀ (packed crowd) |
|---|---|
| 0 | 13.95 s |
| 10 | 7.6 s |
| 44 | 3.0 s |
| 129 (bare-floor crush capacity) | 1.2 s |

Ten people halve the reverberation time. In a room like this, an empty-room
auralization describes a condition that may rarely have occurred.

Clear speech (T₅₀₀ = 1 s) would need 156 people, more than fit. As a cross-check,
treating the crowd as an absorbing *area* (0.87 per m² at 500 Hz, the tabulated
value for a dense audience) gives 1.2 s with the usable floor packed and 1.0 s
packed wall to wall: conversation is at the edge of possible.

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
- **`attire="light"` (0.70 × the table, 0.31 sabins at 500 Hz) is an assumption,
  not a measurement.** It was introduced for lighter ancient dress, but there is a
  better reason for a figure near it: at crush density bodies shade each other.
  The tabulated audience-area coefficient at 500 Hz (0.87 per m² at 2 persons/m²;
  Vorländer, *Auralization*, 2008) is 0.435 per person at that density, Sabine's
  figure, but spread over a crush crowd (0.35 m² each) it is about 0.30 per person.
  Report results under `"modern"` (1.0) as well.
- **No crowd shading in the model itself.** Absorption is linear in N; in dense
  crowds bodies shade each other and real absorption per person falls. Use the
  `"light"` figure, or your own `per_person=`, for packed rooms.
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
