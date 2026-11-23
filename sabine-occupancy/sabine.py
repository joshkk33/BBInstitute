"""sabine — occupancy correction for reverberation time and impulse responses.

Heritage auralization usually renders an empty room: the impulse response was
measured (or simulated) with nobody in it. In a small, hard-walled space the
occupants are often the dominant absorber, so the empty IR can misrepresent
how the room sounded in use. This module applies W. C. Sabine's reverberation
equation to answer "what does this room do with N people in it?" — starting
from a reverberation time you already have.

Quick start
-----------
    >>> import sabine
    >>> t_empty = {500: 13.95}          # empty RT60 per octave band, seconds
    >>> round(sabine.occupied_rt60(t_empty, volume_m3=320.7, n_people=40)[500], 2)
    3.22
    >>> round(sabine.solve_people(t_empty, volume_m3=320.7, target_t=1.0), 1)
    155.7

Units: octave-band centre frequencies in Hz, times in seconds, areas in m²,
volumes in m³, absorption in metric sabins (m² of perfect absorber — Sabine's
"open window" unit).

Assumptions and limits — read these before quoting a number
-----------------------------------------------------------
1. DIFFUSE FIELD. T = k·V/A assumes sound energy is evenly spread and decays
   exponentially. It is weakest at low frequency in small rooms, where
   individual modes dominate the decay, and in rooms with very uneven
   absorption or strongly coupled volumes. Starting from a *measured* empty T
   (the primary entry point here) puts the room's real behaviour into the
   baseline; only the occupants' *increment* relies on the diffuse model.
2. PER-PERSON ABSORPTION IS THE BIGGEST LEVER. The default table is a modern
   octave-band synthesis anchored so 500 Hz equals Sabine's own audience
   figure, 0.44 sabins per person (Collected Papers on Acoustics, 1922,
   measured near 512 Hz). Sabine measured a *seated* audience in Harvard
   lecture halls; standing people in other dress can absorb noticeably more
   or less. Pass `per_person=` with your own table whenever you have one.
3. THE ATTIRE FACTOR IS AN ASSUMPTION, NOT A MEASUREMENT. `attire="light"`
   scales per-person absorption by 0.70 to represent lighter ancient dress.
   It is a modern judgement call. Results that depend on it should be
   reported under both settings (see `ATTIRE`).
4. NO CROWD SHADING. Absorption is linear in N. In dense crowds bodies shade
   each other and the per-person figure drops; linear N therefore overstates
   absorption at crush densities (which shortens the occupied T further than
   reality would).
5. CAPACITY IS A SEPARATE CLAIM. `capacity()` estimates how many people fit
   on a bare floor. It depends on furnishings, obstructions and how people
   actually stand. Nothing in the acoustic functions clamps to it; ask it
   separately.
6. AIR ABSORPTION. When you start from a measured T, air absorption is
   already inside the back-solved A. When you build A from surfaces, add
   `air_absorption()` yourself.

Citation: W. C. Sabine, *Collected Papers on Acoustics*, Harvard University
Press, 1922 (public domain).
"""

from __future__ import annotations

import math
from typing import Iterable, Mapping

import numpy as np

__version__ = "0.1.0"

__all__ = [
    "OCTAVE_BANDS", "PERSON_SABINS", "ATTIRE", "AIR_M",
    "sabine_constant", "absorption_from_rt60", "person_absorption",
    "occupied_rt60", "solve_people",
    "absorption_from_surfaces", "air_absorption", "sabine_t60", "eyring_t60",
    "capacity", "presence_filter",
]

OCTAVE_BANDS = (125, 250, 500, 1000, 2000, 4000)

# Per-person absorption, m² sabins per octave band. Modern synthesis anchored
# so 500 Hz equals Sabine's measured 0.44 per audience member. Not a
# measurement at the other bands — see module docstring, assumption 2.
PERSON_SABINS = {125: 0.20, 250: 0.33, 500: 0.44, 1000: 0.48, 2000: 0.50, 4000: 0.46}

# Multiplier on PERSON_SABINS. "modern" = Sabine's own audience (1.0).
# "light" = 0.70, an ASSUMPTION for lighter ancient dress — not measured.
ATTIRE = {"light": 0.70, "modern": 1.00}

# Air power-attenuation coefficient m (1/m) at ~20 °C, 50 % RH; A_air = 4·m·V.
AIR_M = {125: 0.0001, 250: 0.0003, 500: 0.0006, 1000: 0.0011, 2000: 0.0026, 4000: 0.0072}

_LN_1000 = math.log(1000.0)   # 60 dB of amplitude decay, in nepers


# ── helpers ──────────────────────────────────────────────────────────────────

def _require_positive(name: str, value: float, why: str) -> float:
    if value is None:
        raise ValueError(f"{name} is required: {why}")
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive number (got {value!r}): {why}")
    return value


def _bands(name: str, by_band: Mapping[int, float]) -> dict[int, float]:
    if not isinstance(by_band, Mapping) or not by_band:
        raise ValueError(f"{name} must be a non-empty mapping {{band_hz: value}}")
    out = {}
    for f, v in by_band.items():
        out[int(f)] = _require_positive(f"{name}[{f}]", v, "every band needs a positive value")
    return out


def _per_person_table(attire: str, per_person: Mapping[int, float] | None) -> dict[int, float]:
    if per_person is not None:
        return _bands("per_person", per_person)
    if attire not in ATTIRE:
        raise ValueError(f"attire must be one of {sorted(ATTIRE)} (got {attire!r}), "
                         "or pass your own per_person table")
    return {f: a * ATTIRE[attire] for f, a in PERSON_SABINS.items()}


def sabine_constant(speed_of_sound: float = 343.0) -> float:
    """k in T = k·V/A. 24·ln(10)/c ≈ 0.161 s/m at c = 343 m/s.

    Sabine fit k = 0.171 in 1898 and later 0.164; the modern value is derived
    from the speed of sound, so pass the c that matches your measurement
    conditions if they differ much from 20 °C.
    """
    c = _require_positive("speed_of_sound", speed_of_sound, "k depends on c")
    return 24 * math.log(10) / c


# ── core: measured-first, geometry-free ──────────────────────────────────────

def absorption_from_rt60(rt60_by_band: Mapping[int, float], volume_m3: float,
                         speed_of_sound: float = 343.0) -> dict[int, float]:
    """Back-solve total absorption A per band from a measured empty RT60.

    A = k·V/T. This is the entry point for someone with a measured IR and a
    published volume but no surface-by-surface breakdown. The result includes
    every absorber present during the measurement (surfaces, air, furnishings).
    """
    t = _bands("rt60_by_band", rt60_by_band)
    v = _require_positive("volume_m3", volume_m3,
                          "absorption cannot be recovered from T without the room volume")
    k = sabine_constant(speed_of_sound)
    return {f: k * v / tf for f, tf in t.items()}


def person_absorption(n_people: float, attire: str = "light",
                      per_person: Mapping[int, float] | None = None) -> dict[int, float]:
    """Absorption added by N occupants, sabins per band.

    Uses PERSON_SABINS × ATTIRE[attire] unless `per_person` (sabins per person
    per band) is given, in which case `attire` is ignored.
    """
    n = float(n_people)
    if not math.isfinite(n) or n < 0:
        raise ValueError(f"n_people must be ≥ 0 (got {n_people!r})")
    return {f: n * a for f, a in _per_person_table(attire, per_person).items()}


def occupied_rt60(rt60_empty_by_band: Mapping[int, float], volume_m3: float,
                  n_people: float, attire: str = "light",
                  per_person: Mapping[int, float] | None = None,
                  speed_of_sound: float = 343.0) -> dict[int, float]:
    """Empty RT60 in, occupied RT60 out (Sabine), for every band supplied.

    T_occ = k·V / (A_empty + N·a_person). Bands in `rt60_empty_by_band` must
    all be present in the per-person table.
    """
    a_empty = absorption_from_rt60(rt60_empty_by_band, volume_m3, speed_of_sound)
    a_people = person_absorption(n_people, attire, per_person)
    missing = sorted(set(a_empty) - set(a_people))
    if missing:
        raise ValueError(f"no per-person absorption for band(s) {missing} Hz; "
                         "pass per_person= covering every band you supply")
    k = sabine_constant(speed_of_sound)
    v = float(volume_m3)
    return {f: k * v / (a_empty[f] + a_people[f]) for f in a_empty}


def solve_people(rt60_empty_by_band: Mapping[int, float], volume_m3: float,
                 target_t: float, band: int = 500, attire: str = "light",
                 per_person: Mapping[int, float] | None = None,
                 speed_of_sound: float = 343.0) -> float:
    """How many occupants bring the RT60 at `band` down to `target_t`.

    Returns a float (the caller decides how to round). Returns 0.0 if the
    empty room is already at or below the target. Does NOT check whether that
    many people fit — call `capacity()` for that separate question.
    """
    band = int(band)
    if band not in {int(f) for f in rt60_empty_by_band}:
        raise ValueError(f"band {band} Hz not in rt60_empty_by_band")
    t_target = _require_positive("target_t", target_t, "need a target reverberation time")
    a_empty = absorption_from_rt60({band: rt60_empty_by_band[band]}, volume_m3,
                                   speed_of_sound)[band]
    table = _per_person_table(attire, per_person)
    if band not in table:
        raise ValueError(f"no per-person absorption for band {band} Hz")
    a_needed = sabine_constant(speed_of_sound) * float(volume_m3) / t_target
    return max((a_needed - a_empty) / table[band], 0.0)


# ── geometry path: for callers building absorption from surfaces ─────────────

def absorption_from_surfaces(surfaces: Iterable[tuple[float, Mapping[int, float]]]
                             ) -> dict[int, float]:
    """Sum area × α per band. `surfaces`: iterable of (area_m2, {band: alpha}).

    All surfaces must cover the same bands. Air absorption is NOT included —
    add `air_absorption(volume)` for the room total.
    """
    total: dict[int, float] | None = None
    for i, (area, alphas) in enumerate(surfaces):
        area = _require_positive(f"surfaces[{i}] area_m2", area, "surface needs an area")
        alphas = {int(f): float(a) for f, a in alphas.items()}
        for f, a in alphas.items():
            if not 0 <= a <= 1:
                raise ValueError(f"surfaces[{i}] alpha at {f} Hz must be in [0, 1] (got {a})")
        if total is None:
            total = {f: 0.0 for f in alphas}
        elif set(alphas) != set(total):
            raise ValueError(f"surfaces[{i}] bands {sorted(alphas)} differ from "
                             f"earlier surfaces {sorted(total)}")
        for f, a in alphas.items():
            total[f] += area * a
    if total is None:
        raise ValueError("surfaces is empty")
    return total


def air_absorption(volume_m3: float, m_by_band: Mapping[int, float] = AIR_M
                   ) -> dict[int, float]:
    """A_air = 4·m·V per band, m = air power-attenuation coefficient (1/m).

    The default m is ~20 °C / 50 % RH; cool damp interiors absorb less at
    high frequency. Supply your own m for other conditions.
    """
    v = _require_positive("volume_m3", volume_m3, "air absorption scales with volume")
    return {int(f): 4 * float(m) * v for f, m in m_by_band.items()}


def sabine_t60(absorption_by_band: Mapping[int, float], volume_m3: float,
               speed_of_sound: float = 343.0) -> dict[int, float]:
    """T = k·V/A per band."""
    a = _bands("absorption_by_band", absorption_by_band)
    v = _require_positive("volume_m3", volume_m3, "T scales with volume")
    k = sabine_constant(speed_of_sound)
    return {f: k * v / af for f, af in a.items()}


def eyring_t60(absorption_by_band: Mapping[int, float], volume_m3: float,
               surface_m2: float, air_absorption_by_band: Mapping[int, float] | None = None,
               speed_of_sound: float = 343.0) -> dict[int, float]:
    """Eyring: T = k·V / (−S·ln(1 − ᾱ) + A_air), ᾱ = A_surfaces / S.

    `absorption_by_band` is SURFACE absorption only (air passed separately).
    Diverges from Sabine as mean absorption grows; near-identical below ᾱ≈0.1.
    """
    a = _bands("absorption_by_band", absorption_by_band)
    v = _require_positive("volume_m3", volume_m3, "T scales with volume")
    s = _require_positive("surface_m2", surface_m2,
                          "Eyring needs total surface area to form the mean absorption")
    air = {f: 0.0 for f in a} if air_absorption_by_band is None else \
        {int(f): float(x) for f, x in air_absorption_by_band.items()}
    k = sabine_constant(speed_of_sound)
    out = {}
    for f, af in a.items():
        alpha = af / s
        if alpha >= 1:
            raise ValueError(f"mean absorption at {f} Hz is ≥ 1 (A={af:.1f} > S={s:.1f})")
        out[f] = k * v / (-s * math.log(1 - alpha) + air.get(f, 0.0))
    return out


# ── capacity: a separate claim from the physics ──────────────────────────────

def capacity(floor_m2: float, perimeter_m: float, m2_per_person: float = 0.35,
             edge_margin_m: float = 0.30) -> float:
    """Bare-floor occupant estimate: (floor − edge_margin·perimeter) / density.

    Default 0.35 m²/person ≈ Fruin level of service E/F (crush). This is an
    UPPER bound: furnishings, sarcophagi, steps and how people actually stand
    all lower it. Use 0.65 for a loose congregation. Returns a float.
    """
    floor = _require_positive("floor_m2", floor_m2, "capacity needs the floor area")
    perim = _require_positive("perimeter_m", perimeter_m,
                              "the edge strip along the walls is excluded from usable floor")
    density = _require_positive("m2_per_person", m2_per_person, "need an area per person")
    usable = floor - float(edge_margin_m) * perim
    if usable <= 0:
        raise ValueError(f"edge margin {edge_margin_m} m leaves no usable floor")
    return usable / density


# ── optional: apply presence to an impulse response ──────────────────────────

def _band_weights(freqs: np.ndarray, bands: list[int]) -> list[np.ndarray]:
    """Complementary octave crossovers: cos²/sin² in log-frequency between
    adjacent centres. The weights sum to exactly 1 at every frequency, so
    splitting and re-summing reconstructs the input exactly."""
    w = [np.zeros_like(freqs) for _ in bands]
    w[0][freqs <= bands[0]] = 1.0
    w[-1][freqs >= bands[-1]] = 1.0
    for i in range(len(bands) - 1):
        lo, hi = bands[i], bands[i + 1]
        sel = (freqs >= lo) & (freqs < hi)
        x = np.log2(freqs[sel] / lo) / math.log2(hi / lo)
        w[i][sel] = np.cos(np.pi * x / 2) ** 2
        w[i + 1][sel] = np.sin(np.pi * x / 2) ** 2
    return w


def presence_filter(ir, sample_rate: float, rt60_empty_by_band: Mapping[int, float],
                    rt60_occupied_by_band: Mapping[int, float],
                    onset_index: int | None = None) -> np.ndarray:
    """Reshape an impulse response so each band decays at its occupied RT60.

    Each band is multiplied by exp(−ln(1000)·t·(1/T_occ − 1/T_empty)), with t
    measured from the direct arrival (`onset_index`, default: the absolute
    peak). The room's fine structure — modes, echoes, measured colouration — is
    kept; only the decay rate changes. The direct sound is untouched: bodies
    soak the reverberant field, not the line of sight.

    Numpy only: bands are split with zero-phase complementary FFT crossovers,
    so with T_occ == T_empty the output equals the input to rounding error.
    Below the lowest band the lowest band's ratio applies, above the highest
    the highest's.

    Not modelled: changes to early reflections (e.g. grazing incidence over
    a crowd), and frequency-dependent shading in dense crowds. This is a
    standard decay-shaping technique applied with a Sabine-derived target, not
    a full occupied-room simulation.
    """
    x = np.asarray(ir, dtype=np.float64)
    if x.ndim != 1 or x.size < 2:
        raise ValueError("ir must be a 1-D array (one channel); loop over channels yourself")
    fs = _require_positive("sample_rate", sample_rate, "needed to place the bands")
    t_emp = _bands("rt60_empty_by_band", rt60_empty_by_band)
    t_occ = _bands("rt60_occupied_by_band", rt60_occupied_by_band)
    if set(t_emp) != set(t_occ):
        raise ValueError("empty and occupied RT60 must cover the same bands")
    bands = sorted(t_emp)

    n0 = int(np.argmax(np.abs(x))) if onset_index is None else int(onset_index)
    if not 0 <= n0 < x.size:
        raise ValueError(f"onset_index {onset_index} outside the IR")
    t = np.maximum(np.arange(x.size) - n0, 0) / fs

    n_fft = 1 << int(math.ceil(math.log2(2 * x.size)))   # zero-pad: no circular wrap
    spec = np.fft.rfft(x, n_fft)
    freqs = np.fft.rfftfreq(n_fft, 1 / fs)
    out = np.zeros_like(x)
    for f, w in zip(bands, _band_weights(freqs, bands)):
        band_sig = np.fft.irfft(spec * w, n_fft)[: x.size]
        rate = _LN_1000 * (1 / t_occ[f] - 1 / t_emp[f])
        out += band_sig * np.exp(-rate * t)
    return out
