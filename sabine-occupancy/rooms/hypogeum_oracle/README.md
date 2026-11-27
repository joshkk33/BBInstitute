# Ħal Saflieni Hypogeum — Oracle Room: reverb presets

A small rock-cut chamber in Malta's underground necropolis.

Load any of these into a convolution reverb and you are playing in this room, empty or
with people in it. Same idea as the "Hall" setting on a home-theater receiver, except
this one is a specific room and you choose the crowd.

| file | people | | T₅₀₀ (measured from the file) |
|---|---|---|---|
| [`hypogeum_oracle_000-people.wav`](hypogeum_oracle_000-people.wav) | 0 | empty | 2.5 s |
| [`hypogeum_oracle_009-people.wav`](hypogeum_oracle_009-people.wav) | 9 | speech crowd (T₅₀₀ ≈ 1 s) | 1.0 s |
| [`hypogeum_oracle_022-people.wav`](hypogeum_oracle_022-people.wav) | 22 | floor full | 0.55 s |

48 kHz, 24-bit, mono, 3.4 s. All files share one gain, so the
quieter tails of the occupied versions are real, not normalised away.

## What these are, honestly

- **Simulated, not recorded.** Geometry: approximate (4.5 × 2.7 m floor · ceiling 2.3 m · limestone).
  Room acoustics: pyroomacoustics image-source + ray tracing, seed 1900.
  Anchor: measured-contested, ~110 Hz resonance (Debertolis et al. (SBRG, 2014)).
- **People** are added with [`sabine.py`](../../sabine.py): each octave band decays faster by
  the absorption of N people (0.31 sabins each at 500 Hz, a packed standing crowd).
  The direct sound and the room's fine structure are kept.
- **Capacity** (22 people) is bare floor at crush density, an upper bound.

See [../README.md](../README.md) for how to load these in common software.

## License, credit, and a request

**CC BY 4.0.** Use these in anything, including commercial music, film, games and
research. Please credit:

> Reverb presets: Bear Branch Institute (bearbranch.org), made with sabine.py

Bear Branch Sanctuary, Inc. is a small 501(c)(3) nonprofit. These are free and will
stay free. If they end up in your work, please consider
[a donation to the Sanctuary](https://donate.stripe.com/fZu28qdJ82rkeCD7FxfMA00). It keeps tools like this coming.
