# Wayland's Smithy chambered long barrow: reverb presets

A chambered long barrow in Oxfordshire. Barely room for eight.

Load any of these into a convolution reverb and you are playing in this room, empty or
with people in it. Same idea as the "Hall" setting on a home-theater receiver, except
this one is a specific room and you choose the crowd.

| file | people | | T₅₀₀ (measured from the file) |
|---|---|---|---|
| [`waylands_smithy_000-people.wav`](waylands_smithy_000-people.wav) | 0 | empty | 1.1 s |
| [`waylands_smithy_001-people.wav`](waylands_smithy_001-people.wav) | 1 | speech crowd (T₅₀₀ ≈ 1 s) | 0.93 s |
| [`waylands_smithy_008-people.wav`](waylands_smithy_008-people.wav) | 8 | floor full | 0.49 s |

48 kHz, 24-bit, mono, 1.6 s. All files share one gain, so the
quieter tails of the occupied versions are real, not normalised away.

## What these are, honestly

- **Simulated, not recorded.** Geometry: approximate (4.3 × 1.5 m floor · ceiling 1.8 m · drystone).
  Room acoustics: pyroomacoustics image-source + ray tracing, seed 1900.
  Anchor: measured, ~112 Hz resonance (Jahn, Devereux & Ibison 1996, JASA 99(2)).
- **People** are added with [`sabine.py`](../../sabine.py): each octave band decays faster by
  the absorption of N people (0.31 sabins each at 500 Hz, a packed standing crowd).
  The direct sound and the room's fine structure are kept.
- **Capacity** (8 people) is bare floor at crush density, an upper bound.

See [../README.md](../README.md) for how to load these in common software.

CC BY 4.0 — free to use in anything, including commercial work; please credit Bear Branch Institute.
