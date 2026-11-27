# Newgrange passage tomb — central chamber: reverb presets

A 19 m stone passage into a corbelled chamber in Ireland's Boyne valley.

Load any of these into a convolution reverb and you are playing in this room, empty or
with people in it. Same idea as the "Hall" setting on a home-theater receiver, except
this one is a specific room and you choose the crowd.

| file | people | | T₅₀₀ (measured from the file) |
|---|---|---|---|
| [`newgrange_000-people.wav`](newgrange_000-people.wav) | 0 | empty | 2.2 s |
| [`newgrange_071-people.wav`](newgrange_071-people.wav) | 71 | speech crowd (T₅₀₀ ≈ 1 s) | 1.1 s |
| [`newgrange_081-people.wav`](newgrange_081-people.wav) | 81 | floor full | 1.0 s |

48 kHz, 24-bit, mono, 2.6 s. All files share one gain, so the
quieter tails of the occupied versions are real, not normalised away.

## What these are, honestly

- **Simulated, not recorded.** Geometry: approximate (passage 19 m · chamber 5.2 × 5.2 m, 6 m high · drystone).
  Room acoustics: pyroomacoustics image-source + ray tracing, seed 1900.
  Anchor: measured, ~110 Hz resonance (Jahn, Devereux & Ibison 1996, JASA 99(2)).
- **People** are added with [`sabine.py`](../../sabine.py): each octave band decays faster by
  the absorption of N people (0.31 sabins each at 500 Hz, a packed standing crowd).
  The direct sound and the room's fine structure are kept.
- **Capacity** (81 people) is bare floor at crush density, an upper bound.

See [../README.md](../README.md) for how to load these in common software.

## License, credit, and a request

**CC BY 4.0.** Use these in anything, including commercial music, film, games and
research. Please credit:

> Reverb presets: Bear Branch Institute (bearbranch.org), made with sabine.py

Bear Branch Sanctuary, Inc. is a small 501(c)(3) nonprofit. These are free and will
stay free. If they end up in your work, please consider
[a donation to the Sanctuary](https://donate.stripe.com/fZu28qdJ82rkeCD7FxfMA00). It keeps tools like this coming.
