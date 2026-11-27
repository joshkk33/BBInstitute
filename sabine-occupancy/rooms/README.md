# Take a room home: reverb presets

Five ancient rooms as convolution-reverb impulse responses, empty and with people in
them. Each was made with [`sabine.py`](../sabine.py): take the empty room's impulse
response, add N people, and every octave band rings for less time.

| room | empty T₅₀₀ | with people (N: T₅₀₀) — measured from the files |
|---|---|---|
| [King's Chamber](kings_chamber/) | 12.7 s | 44: 3.0 s · 129: 1.2 s |
| [Hypogeum](hypogeum_oracle/) | 2.5 s | 9: 1.0 s · 22: 0.55 s |
| [Newgrange](newgrange/) | 2.2 s | 71: 1.1 s · 81: 1.0 s |
| [Chavín](chavin_gallery/) | 4.2 s | 3: 2.5 s · 17: 0.90 s · 23: 0.72 s |
| [Wayland's Smithy](waylands_smithy/) | 1.1 s | 1: 0.93 s · 8: 0.49 s |

## Loading a preset

Any convolution reverb that accepts a WAV impulse response works:

- **Logic Pro**: Space Designer → IR Sample → load the WAV.
- **Ableton Live**: Hybrid Reverb → Convolution → drag the WAV onto the IR display.
- **Reaper**: ReaVerb → Add → File → choose the WAV.
- **GarageBand / free options**: any free convolution reverb plugin, or SoX / Python:
  `numpy.convolve(dry_audio, impulse_response)`.

Set the reverb to 100% wet to hear the room as it is, or blend to taste.

## Honest limits

These are simulations of surveyed or approximate geometry, not recordings in the
rooms. The occupied versions use Sabine's equation, which is weakest at low
frequency in small rooms. Each room's folder says exactly what went into it.

CC BY 4.0 — free to use in anything, including commercial work; please credit Bear Branch Institute.
