# Chavín de Huántar — Laberintos gallery segment: reverb presets

Stone galleries of an Andean ceremonial centre, studied in situ by Kolar's Stanford team.

Load any of these into a convolution reverb and you are playing in this room, empty or
with people in it. Same idea as the "Hall" setting on a home-theater receiver, except
this one is a specific room and you choose the crowd.

| file | people | | T₅₀₀ (measured from the file) |
|---|---|---|---|
| [`chavin_gallery_000-people.wav`](chavin_gallery_000-people.wav) | 0 | empty | 4.2 s |
| [`chavin_gallery_003-people.wav`](chavin_gallery_003-people.wav) | 3 | chant crowd (T₅₀₀ ≈ 3 s) | 2.5 s |
| [`chavin_gallery_017-people.wav`](chavin_gallery_017-people.wav) | 17 | speech crowd (T₅₀₀ ≈ 1 s) | 0.90 s |
| [`chavin_gallery_023-people.wav`](chavin_gallery_023-people.wav) | 23 | floor full | 0.72 s |

48 kHz, 24-bit, mono, 3.8 s. All files share one gain, so the
quieter tails of the occupied versions are real, not normalised away.

## What these are, honestly

- **Simulated, not recorded.** Geometry: approximate (passage 12 m · chamber 2.2 × 2.2 m, 2.1 m high · granite).
  Room acoustics: pyroomacoustics image-source + ray tracing, seed 1900.
  Anchor: measured, measured impulse responses (Kolar et al., Stanford CCRMA archaeoacoustics program (2008–)).
- **People** are added with [`sabine.py`](../../sabine.py): each octave band decays faster by
  the absorption of N people (0.31 sabins each at 500 Hz, a packed standing crowd).
  The direct sound and the room's fine structure are kept.
- **Capacity** (23 people) is bare floor at crush density, an upper bound.

See [../README.md](../README.md) for how to load these in common software.

CC BY 4.0 — free to use in anything, including commercial work; please credit Bear Branch Institute.
