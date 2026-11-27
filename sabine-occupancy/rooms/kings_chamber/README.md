# Great Pyramid — King's Chamber: reverb presets

A granite room at the heart of the Great Pyramid. The longest echo of the five.

Load any of these into a convolution reverb and you are playing in this room, empty or
with people in it. Same idea as the "Hall" setting on a home-theater receiver, except
this one is a specific room and you choose the crowd.

| file | people | | T₅₀₀ (measured from the file) |
|---|---|---|---|
| [`kings_chamber_000-people.wav`](kings_chamber_000-people.wav) | 0 | empty | 12.7 s |
| [`kings_chamber_044-people.wav`](kings_chamber_044-people.wav) | 44 | chant crowd (T₅₀₀ ≈ 3 s) | 3.0 s |
| [`kings_chamber_129-people.wav`](kings_chamber_129-people.wav) | 129 | floor full | 1.2 s |

48 kHz, 24-bit, mono, 10.0 s. All files share one gain, so the
quieter tails of the occupied versions are real, not normalised away.

## What these are, honestly

- **Simulated, not recorded.** Geometry: surveyed (10.47 × 5.234 m floor · ceiling 5.852 m · granite).
  Room acoustics: pyroomacoustics image-source + ray tracing, seed 1900.
  Anchor: reported, ~30 Hz resonance (various informal measurements).
- **People** are added with [`sabine.py`](../../sabine.py): each octave band decays faster by
  the absorption of N people (0.31 sabins each at 500 Hz, a packed standing crowd).
  The direct sound and the room's fine structure are kept.
- **Capacity** (129 people) is bare floor at crush density, an upper bound.

See [../README.md](../README.md) for how to load these in common software.

## License, credit, and a request

**CC BY 4.0.** Use these in anything, including commercial music, film, games and
research. Please credit:

> Reverb presets: Bear Branch Institute (bearbranch.org), made with sabine.py

Bear Branch Sanctuary, Inc. is a small 501(c)(3) nonprofit. These are free and will
stay free. If they end up in your work, please consider
[a donation to the Sanctuary](https://donate.stripe.com/fZu28qdJ82rkeCD7FxfMA00). It keeps tools like this coming.
